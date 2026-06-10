"""
rf_model.py -> xgb_model.py
-----------
Entry point cua Phan 4 (Machine Learning) - Tuan 2 (XGBoost).
Quy trinh:
  1. Doc du lieu tu ket qua cua Batch (train_cleaned.parquet, test_cleaned.parquet)
  2. Build & train pipeline: goi train_model.py
  3. Danh gia toan dien: goi evaluate.py
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
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load module {name} from {filepath}")
    mod  = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

_here  = os.path.dirname(os.path.abspath(__file__))
_batch = os.path.abspath(os.path.join(_here, '..', 'batch'))

# Import tu ml/
_train_mod    = _import_module("train_model",    os.path.join(_here,  "train_model.py"))
_eval_mod     = _import_module("evaluate",       os.path.join(_here,  "evaluate.py"))

# Import tu batch/
_hdfs_mod     = _import_module("hdfs_utils",     os.path.join(_batch, "hdfs_utils.py"))

build_preprocessing_pipeline = _train_mod.build_preprocessing_pipeline
apply_pipeline                = _train_mod.apply_pipeline
train_xgboost                 = _train_mod.train_xgboost
add_class_weights             = _train_mod.add_class_weights
compute_metrics               = _eval_mod.compute_metrics
print_report                  = _eval_mod.print_report
load_parquet                  = _hdfs_mod.load_parquet


def main():
    spark = SparkSession.builder \
        .appName("UNSW-NB15-XGB-Model") \
        .master("local[*]") \
        .config("spark.sql.warehouse.dir", "file:///tmp/spark-warehouse") \
        .getOrCreate()
    spark.sparkContext.setLogLevel("ERROR")

    # Fix Windows: bypass winutils.exe bang LocalFileSystem
    hc = spark.sparkContext._jsc.hadoopConfiguration() # type: ignore
    hc.set("fs.file.impl", "org.apache.hadoop.fs.LocalFileSystem")
    hc.set("fs.file.impl.disable.cache", "true")

    # Su dung _here (duong dan tuyet doi toi thu muc ml/) de khong phu thuoc CWD
    train_parquet = os.path.join(_here, '..', 'data', 'processed', 'train_cleaned.parquet')
    test_parquet  = os.path.join(_here, '..', 'data', 'processed', 'test_cleaned.parquet')

    try:
        # ---- BUOC 1 & 2: Doc du lieu da duoc Batch xu ly ----
        print(">>> [1/4] Doc du lieu da duoc lam sach tu Batch Processing...")
        if not os.path.exists(train_parquet) or not os.path.exists(test_parquet):
            print(f"Error: Khong tim thay {train_parquet} hoac {test_parquet}")
            print("Vui long chay 'python batch/spark_sample.py' truoc!")
            spark.stop()
            return
            
        proc_train = load_parquet(spark, train_parquet)
        proc_test  = load_parquet(spark, test_parquet)

        if proc_train is None or proc_test is None:
            print("Error: Khong doc duoc du lieu Parquet.")
            spark.stop()
            return

        # ---- BUOC 3: Build pipeline va transform ----
        print(">>> [2/4] Build Pipeline (StringIndexer + VectorAssembler) cho nhãn attack_cat...")
        feature_cols, fitted_pipeline, assembler, train_data, final_label_col = \
            build_preprocessing_pipeline(proc_train, label_col='attack_cat')

        categorical_cols = [c for c, t in proc_train.dtypes if t == 'string' and c != 'attack_cat']

        print("         -> Dung tap test tu Batch de danh gia...")
        test_data = apply_pipeline(proc_test, fitted_pipeline, assembler,
                                   categorical_cols, label_col='attack_cat', final_label_col=final_label_col)

        # ---- BUOC 4: Train model ----
        print(">>> [3/4] Xu ly Class Imbalance va Training XGBoost...")
        start = time.time()
        
        # 1. Tinh va them trong so de can bang nhan hiem
        train_data_weighted = add_class_weights(train_data, label_col=final_label_col, weight_col='class_weight')
        
        # 2. Train mo hinh kem trong so
        model = train_xgboost(train_data_weighted, label_col=final_label_col, weight_col='class_weight', num_trees=100, max_depth=6)
        
        print(f"         -> Hoan thanh trong {time.time() - start:.2f} giay!")

        # ---- BUOC 5: Danh gia ----
        print(">>> [4/4] Danh gia mo hinh...")
        pred_train = model.transform(train_data)
        pred_test  = model.transform(test_data)

        train_metrics = compute_metrics(pred_train, label_col=final_label_col)
        test_metrics  = compute_metrics(pred_test, label_col=final_label_col)

        print_report(train_metrics, test_metrics, model, feature_cols, pred_test, label_col=final_label_col)

        # ---- BUOC 6: Luu mo hinh ----
        print(">>> [5/5] Luu Mo Hinh (Model Persistence)...")
        model_dir = os.path.join(_here, '..', 'models')
        os.makedirs(model_dir, exist_ok=True)
        
        pipeline_path = os.path.join(model_dir, 'xgb_pipeline_saved')
        model_path    = os.path.join(model_dir, 'xgb_model_saved')

        print(f"         -> Dang ghi Pipeline vao: {pipeline_path}")
        fitted_pipeline.write().overwrite().save(pipeline_path)
        
        print(f"         -> Dang ghi Model vao:    {model_path}")
        model.write().overwrite().save(model_path)
        print(">>> Hoan thanh! Mo hinh da san sang cho API Serving.")

    except Exception as e:
        print(f"Loi: {e}")
        import traceback; traceback.print_exc()

    finally:
        spark.stop()


if __name__ == "__main__":
    main()
