"""
spark_sample.py
----------------
Entry point cua Phan 2 (Batch Processing).
Quy trinh (Chong Data Leakage):
  1. Doc file CSV tho UNSW-NB15 (Ca TRAIN va TEST)
  2. Lam sach du lieu (goi preprocessing.py)
  3. Tinh toan dac trung tu tap TRAIN (goi calculate_network_stats)
  4. Ap dung dac trung do vao ca TRAIN va TEST (goi apply_network_features)
  5. Luu ket qua ra 2 file Parquet rieng biet
"""

import os
import sys
import argparse
import logging
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType

# Cau hinh Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

# Fix cho Windows: set HADOOP_HOME tro vao thu muc chua winutils.exe
# winutils.exe va hadoop.dll phai duoc dat tai C:\hadoop\bin\
if sys.platform == 'win32':
    _winutils_home = r'C:\hadoop'
    os.environ['HADOOP_HOME'] = _winutils_home
    _bin = _winutils_home + r'\bin'
    if _bin not in os.environ.get('PATH', ''):
        os.environ['PATH'] = _bin + ';' + os.environ.get('PATH', '')

# Import cac module noi bo
sys.path.insert(0, os.path.dirname(__file__))
from preprocessing import clean_dataframe
from feature_engineering import calculate_network_stats, apply_network_features
from hdfs_utils import load_csv, save_parquet


def main():
    parser = argparse.ArgumentParser(description="UNSW-NB15 Batch Processing Pipeline")
    _here = os.path.dirname(os.path.abspath(__file__))
    
    parser.add_argument("--data_path", type=str, default=os.path.join(_here, '..', 'data', 'UNSW-NB15_*.csv'), help="Path to full dataset CSVs (glob pattern)")
    parser.add_argument("--train_out", type=str, default=os.path.join(_here, '..', 'data', 'processed', 'train_cleaned.parquet'), help="Path to save processed train parquet")
    parser.add_argument("--test_out", type=str, default=os.path.join(_here, '..', 'data', 'processed', 'test_cleaned.parquet'), help="Path to save processed test parquet")
    args = parser.parse_args()

    spark = SparkSession.builder \
        .appName("UNSW-NB15-Batch-Processing") \
        .master("local[*]") \
        .config("spark.sql.warehouse.dir", "file:///tmp/spark-warehouse") \
        .getOrCreate()
    spark.sparkContext.setLogLevel("WARN")

    # Fix Windows: bypass winutils.exe bang LocalFileSystem
    hc = spark.sparkContext._jsc.hadoopConfiguration() # type: ignore
    hc.set("fs.file.impl", "org.apache.hadoop.fs.LocalFileSystem")
    hc.set("fs.file.impl.disable.cache", "true")

    # Schema chuan cho UNSW-NB15 (49 cot) de tang toc do doc file thay vi inferSchema
    unsw_schema_ddl = "srcip STRING, sport STRING, dstip STRING, dsport STRING, proto STRING, state STRING, dur DOUBLE, sbytes INT, dbytes INT, sttl INT, dttl INT, sloss INT, dloss INT, service STRING, sload DOUBLE, dload DOUBLE, spkts INT, dpkts INT, swin INT, dwin INT, stcpb LONG, dtcpb LONG, smean INT, dmean INT, trans_depth INT, res_bdy_len INT, sjit DOUBLE, djit DOUBLE, stime INT, ltime INT, sintpkt DOUBLE, dintpkt DOUBLE, tcprtt DOUBLE, synack DOUBLE, ackdat DOUBLE, is_sm_ips_ports INT, ct_state_ttl INT, ct_flw_http_mthd INT, is_ftp_login INT, ct_ftp_cmd INT, ct_srv_src INT, ct_srv_dst INT, ct_dst_ltm INT, ct_src_ltm INT, ct_src_dport_ltm INT, ct_dst_sport_ltm INT, ct_dst_src_ltm INT, attack_cat STRING, label INT"

    import glob
    data_files = glob.glob(args.data_path)
    if not data_files:
        logging.error(f"Missing dataset CSV at path: {args.data_path}")
        spark.stop()
        return

    try:
        # ---- BUOC 1: Doc du lieu tho va tao tap Train/Test ----
        logging.info("--- [1/4] Doc du lieu UNSW-NB15 va chia tap Train/Test ---")
        df_raw = spark.read.schema(unsw_schema_ddl).csv(data_files, header=False)
        
        # Thay vi randomSplit (gay rò rỉ dữ liệu do các gói tin trong cùng 1 cuộc tấn công bị chia cắt ra cả 2 tập),
        # Chung ta phai chia tap train/test theo THOI GIAN (Chronological Split) de mo phong thuc te.
        time_quantiles = df_raw.approxQuantile("stime", [0.8], 0.01)
        split_time = time_quantiles[0]
        logging.info(f"Cat tap du lieu tai thoi diem (stime threshold): {split_time}")
        
        from pyspark.sql.functions import col
        df_train_raw = df_raw.filter(col("stime") <= split_time)
        df_test_raw = df_raw.filter(col("stime") > split_time)
        
        logging.info(f"Tong so dong (TRAIN tho): {df_train_raw.count()}")
        logging.info(f"Tong so dong (TEST tho) : {df_test_raw.count()}")

        # ---- BUOC 2: Lam sach (goi preprocessing.py) ----
        logging.info("--- [2/4] Lam sach du lieu (preprocessing) ---")
        df_train_clean = clean_dataframe(df_train_raw)
        df_test_clean  = clean_dataframe(df_test_raw)

        # ---- BUOC 3 & 4: Feature Engineering an toan (Chong Leakage) ----
        logging.info("--- [3/4] Feature Engineering (Calculate on Train & Apply on Both) ---")
        proto_stats, state_stat = calculate_network_stats(df_train_clean)
        
        df_train_final = apply_network_features(df_train_clean, proto_stats, state_stat)
        df_test_final  = apply_network_features(df_test_clean, proto_stats, state_stat)

        logging.info(f"Tong so dong (TRAIN sau xu ly): {df_train_final.count()}")
        logging.info(f"Tong so dong (TEST sau xu ly) : {df_test_final.count()}")

        # ---- BUOC 5: LUU PARQUET ----
        logging.info("--- [4/4] Luu Parquet ---")
        
        # Bo coalesce(1) de tranh OOM tren Big Data, thay bang repartition de toi uu xu ly song song
        df_train_final = df_train_final.repartition(4)
        df_test_final  = df_test_final.repartition(4)
        
        logging.info(f" -> Saving: {args.train_out}")
        save_parquet(df_train_final, args.train_out, overwrite=True)
        
        logging.info(f" -> Saving: {args.test_out}")
        save_parquet(df_test_final, args.test_out, overwrite=True)
        logging.info("Hoan thanh Batch Processing!")

    except Exception as e:
        logging.error(f"Loi: {e}")
        import traceback; traceback.print_exc()

    finally:
        spark.stop()


if __name__ == "__main__":
    main()
