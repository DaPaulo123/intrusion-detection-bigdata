

import json
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, from_unixtime
from pyspark.sql.types import (
    StructType, StructField,
    StringType, DoubleType, IntegerType, LongType
)

# ─── 1. Tạo SparkSession ───────────────────────────────────────────────────

spark = (
    SparkSession.builder
    .appName("streamWorldStreaming")
    # Kết nối Kafka qua package (tự download khi chạy lần đầu)
    .config(
        "spark.jars.packages",
        "org.apache.spark:spark-sql-kafka-0-10_2.13:4.1.1"
    )
    .config("spark.sql.adaptive.enabled", "false")     # Giảm log noise khi test local
    .config("spark.sql.shuffle.partitions", "8")
    .master("local[2]")  # dùng 2 CPU core local
    .getOrCreate()
)

spark.sparkContext.setLogLevel("WARN")
print("✅ SparkSession created!")

# ─── 2. Schema của 1 record UNSW-NB15 ─────────────────────────────────────
# (Chỉ lấy các field cơ bản để test, sau này mở rộng)

traffic_schema = spark.read \
    .option("header", True) \
    .option("inferSchema", True) \
    .csv("data/raw/UNSW-NB15.csv") \
    .schema

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
    # Parse timestamp string → timestamp type
    .withColumn("event_time", from_unixtime(col("Stime").cast("long")).cast("timestamp"))
)

# ─── 5. stream World query — chỉ print ra console ──────────────────────────

stream_query = (
    parsed_stream
    .select(
        "event_time",
        "srcip",
        "dstip",
        "proto",
        "attack_cat",
        "Label"
    )
    .writeStream
    .outputMode("append")
    .format("console")
    .option("truncate", False)       # không cắt bớt text dài
    .option("numRows", 20)           # hiện 20 dòng mỗi batch
    .option("checkpointLocation", "C:/tmp/checkpoint_stream")
    .trigger(processingTime="5 seconds")  # xử lý mỗi 5 giây 1 lần
    .start()
)

print("🚀 Streaming query started! Waiting for data from Kafka...")
print("   Topic: network_traffic")
print("   Output: console (mỗi 5 giây hiện 1 batch)")
print("   Nhấn Ctrl+C để dừng.\n")
import signal

def shutdown_handler(signum, frame):
    print("\n  Shutting down...")
    stream_query.stop()
    spark.stop()

signal.signal(signal.SIGINT, shutdown_handler)

try:
    stream_query.awaitTermination()
except Exception:
    pass