import os
import sys
import time
import pandas as pd
from sklearn.ensemble import RandomForestClassifier as SklearnRF
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import LabelEncoder

# Cấu hình Spark
os.environ['HADOOP_HOME'] = "C:\\hadoop"
os.environ['PYSPARK_PYTHON'] = sys.executable
os.environ['PYSPARK_DRIVER_PYTHON'] = sys.executable
from pyspark.sql import SparkSession
from pyspark.ml.feature import VectorAssembler, StringIndexer
from pyspark.ml.classification import RandomForestClassifier as SparkRF
from pyspark.ml.evaluation import MulticlassClassificationEvaluator

# Khởi tạo dữ liệu
file_path = "UNSW_NB15_testing-set.csv"

# ==========================================
# 1. HUẤN LUYỆN BẰNG SCIKIT-LEARN (PANDAS)
# ==========================================
print("\n--- [1] Đang chạy với Scikit-learn ---")
start_time = time.time()
df_pd = pd.read_csv(file_path).drop(columns=['id', 'attack_cat'], errors='ignore').dropna()

# Encode chữ thành số
for col in df_pd.select_dtypes(include=['object']).columns:
    df_pd[col] = LabelEncoder().fit_transform(df_pd[col].astype(str))

X = df_pd.drop(columns=['label'])
y = df_pd['label']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

sk_model = SklearnRF(n_estimators=100, random_state=42)
sk_model.fit(X_train, y_train)
sk_acc = accuracy_score(y_test, sk_model.predict(X_test))
sk_time = time.time() - start_time
print(f"Hoàn thành Sklearn. Thời gian: {sk_time:.2f}s")

# ==========================================
# 2. HUẤN LUYỆN BẰNG PYSPARK MLLIB
# ==========================================
print("\n--- [2] Đang chạy với PySpark MLlib ---")
start_time = time.time()
spark = SparkSession.builder.appName("CompareML").getOrCreate()
spark.sparkContext.setLogLevel("ERROR")

df_sp = spark.read.csv(file_path, header=True, inferSchema=True)
input_cols = ["proto", "service", "state"]
output_cols = [c + "_index" for c in input_cols]
indexer = StringIndexer(inputCols=input_cols, outputCols=output_cols, handleInvalid="keep")
df_indexed = indexer.fit(df_sp).transform(df_sp)

feature_cols = [c for c, t in df_indexed.dtypes if t in ['int', 'double'] 
                and c not in ['id', 'label', 'attack_cat', 'proto', 'service', 'state']]

assembler = VectorAssembler(inputCols=feature_cols, outputCol="features")
data = assembler.transform(df_indexed).select("features", "label")
train_sp, test_sp = data.randomSplit([0.8, 0.2], seed=42)

sp_rf = SparkRF(labelCol="label", featuresCol="features", numTrees=100).setMaxBins(140)
sp_model = sp_rf.fit(train_sp)
predictions = sp_model.transform(test_sp)
evaluator = MulticlassClassificationEvaluator(metricName="accuracy")
sp_acc = evaluator.evaluate(predictions)
sp_time = time.time() - start_time
print(f"Hoàn thành PySpark. Thời gian: {sp_time:.2f}s")

# ==========================================
# KẾT QUẢ SO SÁNH
# ==========================================
print("\n" + "="*50)
print(f"{'Tiêu chí':<20} | {'Scikit-learn':<15} | {'PySpark MLlib'}")
print("-" * 50)
print(f"{'Độ chính xác (%)':<20} | {sk_acc*100:<15.2f} | {sp_acc*100:.2f}")
print(f"{'Thời gian chạy (s)':<20} | {sk_time:<15.2f} | {sp_time:.2f}")
print("="*50)

spark.stop()