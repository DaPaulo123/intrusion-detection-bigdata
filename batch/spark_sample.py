"""
spark_sample.py
----------------
Entry point cua Phan 2 (Batch Processing).
Quy trinh:
  1. Doc file CSV tho UNSW-NB15
  2. In ten cot va mau du lieu (kham pha - Data Exploration)
  3. Lam sach du lieu (goi preprocessing.py)
  4. Tao them feature moi (goi feature_engineering.py)
  5. Luu ket qua ra Parquet (goi hdfs_utils.py)
"""

import os
import sys
from pyspark.sql import SparkSession

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
from feature_engineering import add_network_features
from hdfs_utils import load_csv, save_parquet


def main():
    spark = SparkSession.builder \
        .appName("UNSW-NB15-Batch-Processing") \
        .master("local[*]") \
        .config("spark.sql.warehouse.dir", "file:///tmp/spark-warehouse") \
        .getOrCreate()
    spark.sparkContext.setLogLevel("ERROR")

    # Fix Windows: bypass winutils.exe bang LocalFileSystem
    hc = spark.sparkContext._jsc.hadoopConfiguration()
    hc.set("fs.file.impl", "org.apache.hadoop.fs.LocalFileSystem")
    hc.set("fs.file.impl.disable.cache", "true")

    # Su dung duong dan tuyet doi de chay duoc tu bat ky thu muc nao
    _here        = os.path.dirname(os.path.abspath(__file__))
    raw_path     = os.path.join(_here, '..', 'data', 'UNSW_NB15_testing-set.csv')
    parquet_path = os.path.join(_here, '..', 'data', 'processed', 'UNSW_NB15_cleaned.parquet')

    if not os.path.exists(raw_path):
        print(f"Error: {raw_path} not found.")
        spark.stop()
        return

    try:
        # ---- BUOC 1: Doc du lieu tho ----
        print("\n--- [1/4] Doc du lieu UNSW-NB15 ---")
        df = load_csv(spark, raw_path)
        original_count = df.count()
        print(f"Tong so dong (tho): {original_count}")

        # ---- BUOC 2: Kham pha (Data Exploration) ----
        print("\n--- [2/4] Kham pha du lieu ---")
        print("Cac cot trong dataset:")
        for c in df.columns:
            print(f"  - {c}")
        print("\n5 dong dau tien:")
        df.show(5, truncate=False)

        # ---- BUOC 3: Lam sach (goi preprocessing.py) ----
        print("\n--- [3/4] Lam sach du lieu (preprocessing) ---")
        df_clean = clean_dataframe(df)

        # ---- BUOC 4: Feature Engineering (goi feature_engineering.py) ----
        print("\n--- [4/4] Feature Engineering ---")
        df_final = add_network_features(df_clean)

        clean_count = df_final.count()
        print(f"Tong so dong sau xu ly : {clean_count}")
        print(f"So dong da xoa         : {original_count - clean_count}")
        print(f"Cac cot moi them       : total_bytes, byte_ratio, pkt_ratio, log_duration, is_bidirectional")

        # ---- LUU PARQUET (goi hdfs_utils.py) ----
        print(f"\n--- Luu Parquet -> {parquet_path} ---")
        save_parquet(df_final, parquet_path, overwrite=True)

    except Exception as e:
        print(f"Loi: {e}")

    finally:
        spark.stop()


if __name__ == "__main__":
    main()
