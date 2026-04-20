from pyspark.sql import SparkSession
from pyspark.sql.functions import col

# 1. Khởi tạo Spark
spark = SparkSession.builder.appName("Task2_CleanData").getOrCreate()

print("1. Đang load dữ liệu từ CSV...")
df = spark.read.csv("UNSW_NB15_testing-set.csv", header=True, inferSchema=True)
print(f"-> Số dòng ban đầu: {df.count()}")

# 2. Clean data: Drop null, bỏ qua service '-' và proto 'unknown'
print("2. Đang dọn dẹp dữ liệu (lọc rác)...")
df_clean = df.dropna()

if 'service' in df.columns:
    df_clean = df_clean.filter(col("service") != "-")
if 'proto' in df.columns:
    df_clean = df_clean.filter(col("proto") != "unknown")

print(f"-> Số dòng sau khi clean: {df_clean.count()}")

# 3. Lưu ra định dạng Parquet siêu nhẹ cho Big Data
print("3. Đang xuất ra file Parquet...")
df_clean.write.mode("overwrite").parquet("unsw_cleaned.parquet")

print("======================================================")
print("=> HOÀN THÀNH! Đã lưu folder 'unsw_cleaned.parquet'")
print("======================================================")

spark.stop()