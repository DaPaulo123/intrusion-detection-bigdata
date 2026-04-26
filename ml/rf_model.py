"""
rf_model.py
-----------
Entry point cua Phan 4 (Machine Learning) - Tuan 2 (PySpark MLlib).
Quy trinh:
  1. Doc du lieu (training-set rieng neu co, fallback sang Parquet + split)
  2. Tien xu ly: goi batch/preprocessing.py + batch/feature_engineering.py
  3. Build & train pipeline: goi train_model.py
  4. Danh gia toan dien: goi evaluate.py
"""

from pyspark.sql import SparkSession
import os
import sys
import time
import importlib.util

# Fix cho Windows: set HADOOP_HOME tro vao thu muc chua winutils.exe
# winutils.exe va hadoop.dll phai duoc dat tai C:\hadoop\bin\
if sys.platform == 'win32':
    _winutils_home = r'C:\hadoop'
    os.environ['HADOOP_HOME'] = _winutils_home
    _bin = _winutils_home + r'\bin'
    if _bin not in os.environ.get('PATH', ''):
        os.environ['PATH'] = _bin + ';' + os.environ.get('PATH', '')


def _import_module(name: str, filepath: str):
    """Load module tu duong dan tuyet doi, tranh phu thuoc sys.path."""
    spec = importlib.util.spec_from_file_location(name, filepath)
    mod  = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

_here  = os.path.dirname(os.path.abspath(__file__))
_batch = os.path.abspath(os.path.join(_here, '..', 'batch'))

# Import tu ml/
_train_mod    = _import_module("train_model",    os.path.join(_here,  "train_model.py"))
_eval_mod     = _import_module("evaluate",       os.path.join(_here,  "evaluate.py"))

# Import tu batch/
_prep_mod     = _import_module("preprocessing",  os.path.join(_batch, "preprocessing.py"))
_feat_mod     = _import_module("feature_engineering", os.path.join(_batch, "feature_engineering.py"))
_hdfs_mod     = _import_module("hdfs_utils",     os.path.join(_batch, "hdfs_utils.py"))

build_preprocessing_pipeline = _train_mod.build_preprocessing_pipeline
apply_pipeline                = _train_mod.apply_pipeline
train_random_forest           = _train_mod.train_random_forest
compute_metrics               = _eval_mod.compute_metrics
print_report                  = _eval_mod.print_report
clean_dataframe               = _prep_mod.clean_dataframe
add_network_features          = _feat_mod.add_network_features
load_csv                      = _hdfs_mod.load_csv
load_parquet                  = _hdfs_mod.load_parquet


def main():
    spark = SparkSession.builder \
        .appName("UNSW-NB15-RF-Model") \
        .master("local[*]") \
        .config("spark.sql.warehouse.dir", "file:///tmp/spark-warehouse") \
        .getOrCreate()
    spark.sparkContext.setLogLevel("ERROR")

    # Fix Windows: bypass winutils.exe bang LocalFileSystem
    hc = spark.sparkContext._jsc.hadoopConfiguration()
    hc.set("fs.file.impl", "org.apache.hadoop.fs.LocalFileSystem")
    hc.set("fs.file.impl.disable.cache", "true")

    # Su dung _here (duong dan tuyet doi toi thu muc ml/) de khong phu thuoc CWD
    train_csv    = os.path.join(_here, '..', 'data', 'UNSW_NB15_training-set.csv')
    test_csv     = os.path.join(_here, '..', 'data', 'UNSW_NB15_testing-set.csv')
    parquet_path = os.path.join(_here, '..', 'data', 'processed', 'UNSW_NB15_cleaned.parquet')

    try:
        # ---- BUOC 1: Doc du lieu ----
        if os.path.exists(train_csv) and os.path.exists(test_csv):
            print(">>> [1/5] Su dung file TRAIN + TEST rieng biet (chuan UNSW-NB15 benchmark)...")
            raw_train = load_csv(spark, train_csv)
            raw_test  = load_csv(spark, test_csv)
            use_split = False
        elif os.path.exists(parquet_path):
            print(">>> [1/5] Fallback: doc Parquet va split 80/20")
            print("    [WARN] Chi co 1 tap du lieu -> ket qua chi mang tinh tham khao!")
            raw_train = load_parquet(spark, parquet_path)
            raw_test  = None
            use_split = True
        else:
            print("Error: Khong tim thay du lieu. Chay batch/spark_sample.py truoc.")
            spark.stop()
            return

        if raw_train is None:
            print("Error: Khong doc duoc du lieu.")
            spark.stop()
            return

        # ---- BUOC 2: Tien xu ly (dung cac module batch/) ----
        print(">>> [2/5] Preprocessing + Feature Engineering...")
        proc_train = add_network_features(clean_dataframe(raw_train))
        proc_test  = add_network_features(clean_dataframe(raw_test)) if raw_test else None


        # ---- BUOC 3: Build pipeline va transform ----
        print(">>> [3/5] Build Pipeline (StringIndexer + VectorAssembler)...")
        feature_cols, fitted_pipeline, assembler, train_data = \
            build_preprocessing_pipeline(proc_train)

        categorical_cols = [c for c, t in proc_train.dtypes if t == 'string' and c != 'label']

        if use_split:
            print("         -> Split 80/20 (fallback)...")
            train_data, test_data = train_data.randomSplit([0.8, 0.2], seed=42)
        else:
            print("         -> Dung file test doc lap (chuan benchmark)...")
            test_data = apply_pipeline(proc_test, fitted_pipeline, assembler,
                                       categorical_cols)

        # ---- BUOC 4: Train model ----
        print(">>> [4/5] Training Random Forest (numTrees=50)...")
        start = time.time()
        model = train_random_forest(train_data, num_trees=50, max_bins=256)
        print(f"         -> Hoan thanh trong {time.time() - start:.2f} giay!")

        # ---- BUOC 5: Danh gia ----
        print(">>> [5/5] Danh gia mo hinh...")
        pred_train = model.transform(train_data)
        pred_test  = model.transform(test_data)

        train_metrics = compute_metrics(pred_train)
        test_metrics  = compute_metrics(pred_test)

        print_report(train_metrics, test_metrics, model, feature_cols, pred_test)

    except Exception as e:
        print(f"Loi: {e}")
        import traceback; traceback.print_exc()

    finally:
        spark.stop()


if __name__ == "__main__":
    main()
