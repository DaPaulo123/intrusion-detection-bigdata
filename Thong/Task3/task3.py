import os
import sys
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import StructType, StructField, StringType, IntegerType
from pymongo import MongoClient

# 1. Cấu hình môi trường 
os.environ['HADOOP_HOME'] = r'C:\hadoop'
os.environ['PYSPARK_PYTHON'] = sys.executable
os.environ['PYSPARK_DRIVER_PYTHON'] = sys.executable

# 2. Khởi tạo Spark với bản JAR tương thích 
spark = SparkSession.builder \
    .appName("Task3_Final") \
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0") \
    .getOrCreate()
spark.sparkContext.setLogLevel("ERROR")

# 3. Schema dữ liệu (Dữ liệu từ Kafka đẩy sang)
schema = StructType([
    StructField("srcip", StringType(), True),
    StructField("dstip", StringType(), True),
    StructField("proto", StringType(), True),
    StructField("label", IntegerType(), True)
])

# 4. Đọc Stream từ Kafka
df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "localhost:9092") \
    .option("subscribe", "network-traffic") \
    .option("startingOffsets", "latest") \
    .load()

parsed_df = df.selectExpr("CAST(value AS STRING)") \
    .select(from_json(col("value"), schema).alias("data")) \
    .select("data.*")

# 5. Hàm ghi vào MongoDB (Dùng foreachBatch để tránh lỗi Connection)
def write_to_mongo(df, batch_id):
    mongo_uri = "mongodb://admin:password123@localhost:27017/?authSource=admin"
    client = MongoClient(mongo_uri)
    db = client["ids_database"]
    collection = db["alerts"]
    
    # Gom dữ liệu và lọc bỏ các dòng null
    records = [row.asDict() for row in df.collect() if row.srcip is not None]
    if records:
        collection.insert_many(records)
        print(f"✅ [Batch {batch_id}] Đã ghi {len(records)} dòng vào MongoDB!")
    client.close()

# 6. Chạy luồng xử lý
query = parsed_df.writeStream \
    .foreachBatch(write_to_mongo) \
    .start()

print("🔥 HỆ THỐNG ĐÃ SẴN SÀNG! Đang đợi tin từ Kafka...")
query.awaitTermination()