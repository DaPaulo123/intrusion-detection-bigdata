

import os
import sys
import json
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, from_unixtime
from pyspark.sql.types import (
    StructType, StructField,
    StringType, DoubleType, IntegerType, LongType
)

# ─── 1. Tạo SparkSession ───────────────────────────────────────────────────

# Fix cho Windows: set HADOOP_HOME tro vao thu muc chua winutils.exe
if sys.platform == 'win32':
    _winutils_home = r'C:\hadoop'
    os.environ['HADOOP_HOME'] = _winutils_home
    _bin = _winutils_home + r'\bin'
    if _bin not in os.environ.get('PATH', ''):
        os.environ['PATH'] = _bin + ';' + os.environ.get('PATH', '')

spark = (
    SparkSession.builder
    .appName("streamWorldStreaming")
    # Kết nối Kafka qua package (tự download khi chạy lần đầu)
    .config(
        "spark.jars.packages",
        "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0"
    )
    .config("spark.sql.adaptive.enabled", "false")     # Giảm log noise khi test local
    .config("spark.sql.shuffle.partitions", "8")
    .master("local[2]")  # dùng 2 CPU core local
    .getOrCreate()
)

spark.sparkContext.setLogLevel("WARN")
print("✅ SparkSession created!")

import pandas as pd

# ─── 2. Tự động đọc Schema từ file features ────────────────────────────────
# (Lấy đúng yêu cầu của bạn: đọc file data để biết đặc trưng dataset)

print("Đang quét cấu trúc file NUSW-NB15_features.csv...")
feature_df = pd.read_csv("../data/NUSW-NB15_features.csv", encoding="cp1252")

fields = []
for _, row in feature_df.iterrows():
    # Chuẩn hóa tên cột về chữ thường
    col_name = str(row["Name"]).strip().lower()
    # Chú ý: cột Type trong file CSV gốc có dấu cách thừa "Type "
    col_type_str = str(row["Type "]).strip().lower()
    
    if col_type_str in ["integer", "float", "binary", "timestamp"]:
        spark_type = DoubleType()
    else:
        spark_type = StringType()
        
    fields.append(StructField(col_name, spark_type, True))

traffic_schema = StructType(fields)
print(f"✅ Đã trích xuất thành công {len(fields)} đặc trưng!")

# ─── 3. Đọc stream từ Kafka ────────────────────────────────────────────────

raw_stream = (
    spark.readStream
    .format("kafka")
    .option("kafka.bootstrap.servers", "localhost:9092")
    .option("subscribe", "network_traffic")
    .option("startingOffsets", "latest")
    .load()
)

print("✅ Kafka stream connected!")

# ─── 4. Parse JSON payload ─────────────────────────────────────────────────
# Kafka trả về raw bytes trong cột "value", cần decode + parse JSON

parsed_stream = (
    raw_stream
    # Decode bytes → string
    .select(col("value").cast("string").alias("raw_json"))
    # Parse JSON theo schema
    .select(from_json(col("raw_json"), traffic_schema).alias("data"))
    # Flatten: data.srcip → srcip
    .select("data.*")
    # Drop các trường chứa kết quả để AI tự dự đoán (chống Data Leakage)
    .drop("attack_cat", "label")
    # Parse timestamp string → timestamp type (nhớ dùng đúng tên 'stime' đã in thường)
    .withColumn("event_time", from_unixtime(col("stime").cast("long")).cast("timestamp"))
)

# ─── 5. stream World query — Kết nối API ──────────────────────────

import urllib.request
import urllib.error

API_BATCH_URL = "http://localhost:5000/api/predict/batch"

def send_to_api(batch_df, batch_id):
    records = batch_df.collect()
    if not records: return
    
    payload = [row.asDict() for row in records]
    chunk_size = 100
    for i in range(0, len(payload), chunk_size):
        chunk = payload[i:i + chunk_size]
        try:
            data = json.dumps(chunk, default=str).encode("utf-8")
            req = urllib.request.Request(API_BATCH_URL, data=data, headers={"Content-Type": "application/json"}, method="POST")
            response = urllib.request.urlopen(req)
            resp_data = json.loads(response.read().decode("utf-8"))
            if resp_data.get("status") == "success":
                attacks = [r for r in resp_data["data"]["predictions"] if r["is_attack"]]
                print(f"✅ [Batch {batch_id}] Gửi {len(chunk)} gói. Phát hiện {len(attacks)} tấn công!")
        except Exception as e:
            print(f"❌ Lỗi gửi API: {e}")

stream_query = (
    parsed_stream
    .writeStream
    .foreachBatch(send_to_api)
    .option("checkpointLocation", "C:/tmp/checkpoint_stream_api")
    .trigger(processingTime="5 seconds")
    .start()
)

print("🚀 Streaming pipeline started! Forwarding data from Kafka -> SOC API...")
print("   Nhấn Ctrl+C để dừng.\n")
import signal

def shutdown_handler(signum, frame):
    print("\n  Shutting down...")
    stream_query.stop()
    spark.stop()

signal.signal(signal.SIGINT, shutdown_handler)

stream_query.awaitTermination()