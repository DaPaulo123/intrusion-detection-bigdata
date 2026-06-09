"""
two_stage_xgb_model.py
---------------------
Trien khai kien truc 2 giai doan (Two-stage Classification) de giai quyet
bai toan mat can bang du lieu (Class Imbalance).

- Stage 1 (Binary): Phan loai Normal (0) vs Attack (1).
- Stage 2 (Multiclass): Voi cac luong bi Stage 1 phat hien la Attack (1),
  tiep tuc phan loai chi tiet ra 9 loai tan cong (DoS, Worms, Shellcode...).
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, when
from pyspark.ml import Pipeline
from pyspark.ml.feature import StringIndexer, VectorAssembler
from xgboost.spark import SparkXGBClassifier
from pyspark.ml.evaluation import MulticlassClassificationEvaluator

import os
import sys
import importlib.util

# Fix cho Windows: set HADOOP_HOME tro vao thu muc chua winutils.exe
if sys.platform == 'win32':
    _winutils_home = r'C:\hadoop'
    os.environ['HADOOP_HOME'] = _winutils_home
    _bin = _winutils_home + r'\bin'
    if _bin not in os.environ.get('PATH', ''):
        os.environ['PATH'] = _bin + ';' + os.environ.get('PATH', '')

def _import_module(name: str, filepath: str):
    spec = importlib.util.spec_from_file_location(name, filepath)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load module from {filepath}")
    mod  = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

_here  = os.path.dirname(os.path.abspath(__file__))
_batch = os.path.abspath(os.path.join(_here, '..', 'batch'))

_eval_mod = _import_module("evaluate", os.path.join(_here, "evaluate.py"))
_train_mod = _import_module("train_model", os.path.join(_here, "train_model.py"))

print_report = _eval_mod.print_report
add_class_weights = _train_mod.add_class_weights

def main():
    spark = SparkSession.builder \
        .appName("UNSW-TwoStage-XGB") \
        .master("local[*]").config("spark.python.worker.faulthandler.enabled", "true") \
        .getOrCreate()
    spark.sparkContext.setLogLevel("ERROR")

    # Fix Windows filesystem
    hc = spark.sparkContext._jsc.hadoopConfiguration()  # type: ignore
    hc.set("fs.file.impl", "org.apache.hadoop.fs.LocalFileSystem")

    train_parquet = os.path.join(_here, '..', 'data', 'processed', 'train_cleaned.parquet')
    test_parquet  = os.path.join(_here, '..', 'data', 'processed', 'test_cleaned.parquet')

    print(">>> [1/6] Doc du lieu da duoc lam sach tu Batch Processing...")
    if not os.path.exists(train_parquet) or not os.path.exists(test_parquet):
        print("Loi: Khong tim thay du lieu. Vui long chay 'python batch/spark_sample.py' truoc.")
        spark.stop()
        return

    _hdfs_mod = _import_module("hdfs_utils", os.path.join(_batch, "hdfs_utils.py"))
    proc_train = _hdfs_mod.load_parquet(spark, train_parquet)
    proc_test  = _hdfs_mod.load_parquet(spark, test_parquet)
    print(">>> [2/6] Da load xong du lieu train_cleaned va test_cleaned.")

    # Tao cot is_attack: 0 neu Normal, 1 neu la tan cong
    proc_train = proc_train.withColumn("is_attack", when(col("attack_cat") == "Normal", 0.0).otherwise(1.0))
    proc_test  = proc_test.withColumn("is_attack", when(col("attack_cat") == "Normal", 0.0).otherwise(1.0))

    print(">>> [3/6] Chuan bi Pipeline chung (Encoding & Assembling)...")
    categorical_cols = [c for c, t in proc_train.dtypes if t == 'string' and c != 'attack_cat']
    
    # Ma hoa tat ca String thanh Index (bao gom ca label attack_cat)
    indexers: list = [StringIndexer(inputCol=c, outputCol=c+'_index', handleInvalid='skip') for c in categorical_cols]
    
    # Quan trong: Ma hoa attack_cat tren TOAN BO tap train de xac dinh Index cua Normal
    label_indexer = StringIndexer(inputCol="attack_cat", outputCol="attack_cat_index", handleInvalid='skip')
    label_indexer_model = label_indexer.fit(proc_train)
    
    # Tim Index cua nhan 'Normal' de xai trong luc ket hop du doan
    labels_array = label_indexer_model.labels
    normal_index = float(labels_array.index("Normal"))
    print(f"         -> Index cua nhan 'Normal' la: {normal_index}")

    indexers.append(label_indexer_model)
    
    feature_cols = [c for c in proc_train.columns if c not in categorical_cols and c not in ['attack_cat', 'is_attack']] + [c+'_index' for c in categorical_cols]
    assembler = VectorAssembler(inputCols=feature_cols, outputCol='features')
    
    prep_pipeline = Pipeline(stages=indexers + [assembler])  # type: ignore
    fitted_prep = prep_pipeline.fit(proc_train)
    
    # Data da san sang de huan luyen
    train_data = fitted_prep.transform(proc_train)
    test_data = fitted_prep.transform(proc_test)

    print(">>> [4/6] Huan luyen Stage 1: Binary Model (Normal vs Attack)...")
    xgb_stage1 = SparkXGBClassifier(label_col="is_attack", features_col="features", n_estimators=100, max_depth=6, random_state=42, num_workers=1)
    model_stage1 = xgb_stage1.fit(train_data.limit(1000))
    
    print(">>> [5/6] Huan luyen Stage 2: Multiclass Model (Chi huan luyen tren du lieu Attack)...")
    # Loc ra cac dong la tan cong thuc su (is_attack == 1)
    attack_train_data = train_data.filter(col("is_attack") == 1)
    
    # Ap dung Class Weights CHỈ CHO Stage 2 de cuu cac nhan hiem (Worms, Shellcode...)
    attack_train_weighted = add_class_weights(attack_train_data, label_col="attack_cat_index", weight_col="class_weight")
    
    xgb_stage2 = SparkXGBClassifier(
        label_col="attack_cat_index", 
        features_col="features", 
        weight_col="class_weight", # Kich hoat TRONG SO
        n_estimators=150,             # Tang so cay cho model nay de phan loai 9 nhan tot hon
        max_depth=6, 
        random_state=42,
        num_workers=1
    )
    model_stage2 = xgb_stage2.fit(attack_train_weighted.limit(500))
    
    print(">>> [6/6] Ghep noi va Danh gia mo hinh 2 Giai doan...")
    # Buoc 1: Du doan tren tap test voi Stage 1, xoa bot cac cot de tranh trung lap
    pred_1 = model_stage1.transform(test_data) \
        .withColumnRenamed("prediction", "pred_stage1") \
        .drop("rawPrediction", "probability")
    
    # Buoc 2: Du doan toan bo tren Stage 2 (tam thoi)
    pred_2 = model_stage2.transform(pred_1).withColumnRenamed("prediction", "pred_stage2")
    
    # Buoc 3: Ket hop (Neu Stage 1 bao la Normal (0) => gan nhan la Normal_index, Nguoc lai lay ket qua Stage 2)
    final_pred = pred_2.withColumn(
        "final_prediction",
        when(col("pred_stage1") == 0, normal_index).otherwise(col("pred_stage2"))
    )
    
    # Tinh toan Accuracy & F1 cho giai phap moi
    evaluator_acc = MulticlassClassificationEvaluator(labelCol="attack_cat_index", predictionCol="final_prediction", metricName="accuracy")
    evaluator_f1 = MulticlassClassificationEvaluator(labelCol="attack_cat_index", predictionCol="final_prediction", metricName="f1")
    
    acc = evaluator_acc.evaluate(final_pred)
    f1 = evaluator_f1.evaluate(final_pred)
    
    print("\n=======================================================")
    print("      KET QUA MO HINH 2 GIAI DOAN (TWO-STAGE XGB)      ")
    print("=======================================================")
    print(f"  Accuracy (Test) : {acc * 100:.2f}%")
    print(f"  F1-Score (Test) : {f1 * 100:.2f}%")
    print("-------------------------------------------------------")
    print("  Confusion Matrix (Test Set - Final Prediction):")
    final_pred.groupBy('attack_cat', 'final_prediction').count().orderBy('attack_cat').show(100)
    print("=======================================================")

    # Luu 2 mo hinh va Pipeline
    print("\n>>> [7/7] Luu cac Mo hinh va Pipeline (Model Persistence)...")
    model_dir = os.path.join(_here, '..', 'models')
    os.makedirs(model_dir, exist_ok=True)
    
    pipeline_path = os.path.join(model_dir, 'two_stage_pipeline')
    stage1_path   = os.path.join(model_dir, 'two_stage_model1_binary')
    stage2_path   = os.path.join(model_dir, 'two_stage_model2_multi')

    print(f"         -> Dang ghi Pipeline vao: {pipeline_path}")
    fitted_prep.write().overwrite().save(pipeline_path)
    
    print(f"         -> Dang ghi Stage 1 (Binary) vao: {stage1_path}")
    model_stage1.write().overwrite().save(stage1_path)
    
    print(f"         -> Dang ghi Stage 2 (Multi) vao:  {stage2_path}")
    model_stage2.write().overwrite().save(stage2_path)
    print(">>> Hoan thanh! Kien truc 2 lop da san sang cho API Serving.")

    spark.stop()

if __name__ == "__main__":
    main()
