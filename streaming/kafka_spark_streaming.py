import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json
from pyspark.sql.types import (
    StructType,
    StructField,
    IntegerType,
    StringType,
    DoubleType,
)

# Load Spark-Kafka integration package
# Using Spark 3.5.1 package as it is stable for most recent PySpark versions
os.environ["PYSPARK_SUBMIT_ARGS"] = (
    "--packages org.apache.spark:spark-sql-kafka-0-10_2.13:4.1.1 pyspark-shell"
)


def main():
    print(">>> Khởi tạo Spark Session với Kafka Packages...")
    spark = (
        SparkSession.builder.appName("Kafka-Spark-Streaming-Demo")
        .config("spark.sql.streaming.forceDeleteTempCheckpointLocation", "true")
        .master("local[*]")
        .getOrCreate()
    )

    spark.sparkContext.setLogLevel("WARN")

    # Schema của JSON data đẩy từ Producer
    # Wait, where are these fields
    schema = StructType(
        [
            StructField("id", IntegerType(), True),
            StructField("event", StringType(), True),
            StructField("severity", StringType(), True),
            StructField("source_ip", StringType(), True),
            StructField("timestamp", DoubleType(), True),
        ]
    )

    print(">>> Đang kết nối tới Kafka (localhost:9092), topic = 'test-topic'...")

    # Read stream từ Kafka
    # Dùng availableNow=True hoặc once=True để xử lý các tin nhắn đã có sẵn rồi dừng,
    # rất tiện cho việc biểu diễn và chụp màn hình kết quả
    try:
        df = (
            spark.readStream.format("kafka")
            .option("kafka.bootstrap.servers", "localhost:9092")
            .option("subscribe", "network_traffic")
            .option("startingOffsets", "earliest")
            .load()
        )

        # Parse từ Kafka's binary value -> String -> JSON Schema
        df_string = df.selectExpr("CAST(value AS STRING)")
        parsed_df = df_string.select(
            from_json(col("value"), schema).alias("data")
        ).select("data.*")

        print(">>> Sẵn sàng in luồng Streaming Layer ra Console:")
        # Write stream ra terminal
        query = (
            parsed_df.writeStream.outputMode("append")
            .format("console")
            .trigger(availableNow=True)
            .start()
        )

        query.awaitTermination()
        print(">>> Đã quét xong toàn bộ Data Streaming Test!")

    except Exception as e:
        print(f">>> Lỗi khi thiết lập Streaming Layer: {e}")
    finally:
        spark.stop()


if __name__ == "__main__":
    main()
