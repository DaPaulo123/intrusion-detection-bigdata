## Require Java 21

import os
import shutil

# Screw Microsoft
if os.name == "nt":
    import msvcrt
else:
    import tty
    import sys
    import termios
import time
from dotenv import load_dotenv
from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col,
    from_json,
    from_unixtime,
    window,
    count,
    sum,
    when,
)
from pyspark.sql.types import (
    StructType,
    StructField,
    StringType,
    DoubleType,
    IntegerType,
    LongType,
)

### Config handling


# Try to get value from following orders: global env, config file (TOML), default value
def get_env(global_env: str | None, config, config_path: list[str], default_value):
    value = None
    if global_env is not None:
        value = os.environ.get(global_env)
    if value is None and config is not None:
        config_value = config
        for item in config_path:
            config_value = config_value.get(item, {})
        value = config_value
    if value is None:
        value = default_value
    return value


load_dotenv()
bootstrap_servers = get_env("KAFKA_BOOTSTRAP_SERVERS", None, [], "localhost:9092")
topic = get_env("KAFKA_TOPIC", None, [], "network_traffic")
checkpoint_base = get_env(
    "CHECKPOINT_BASE",
    None,
    [],
    # MS strike again
    "~/AppData/Local/Temp/checkpoints" if os.name == "nt" else "/tmp/checkpoints",
)
# ← đổi True khi cần reset
reset_checkpoints = get_env("RESET_CHECKPOINTS", None, [], True)

# ─── Cleanup checkpoints ──────────────────────────────────────────────────


def cleanup_checkpoints(*paths):
    for path in paths:
        if os.path.exists(path):
            shutil.rmtree(path)
            print(f"🗑️  Deleted checkpoint: {path}")


if reset_checkpoints:
    cleanup_checkpoints(
        f"{checkpoint_base}/raw_append",
        f"{checkpoint_base}/window_update",
        f"{checkpoint_base}/attack_complete",
    )
# ─── SparkSession ─────────────────────────────────────────────────────────
#
# Exactly-once semantics cần 3 điều kiện:
# 1. Kafka source tự tracking offset qua checkpoint (Spark lo)
# 2. Sink hỗ trợ idempotent write (ở đây dùng console để demo)
# 3. checkpointLocation được set — Spark dùng để recover sau crash
spark = (
    SparkSession.builder.appName("streamWorldStreaming")
    # Kết nối Kafka qua package (tự download khi chạy lần đầu)
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.13:4.1.1")
    .config("spark.sql.adaptive.enabled", "false")  # Giảm log noise khi test local
    .config("spark.sql.shuffle.partitions", "8")
    .master("local[*]")
    .getOrCreate()
)

spark.sparkContext.setLogLevel("WARN")
print("✅ SparkSession created!")

# ─── 2. Schema của 1 record UNSW-NB15 ─────────────────────────────────────
# (Chỉ lấy các field cơ bản để test, sau này mở rộng)

traffic_schema = StructType(
    [
        StructField("srcip", StringType(), True),
        StructField("dstip", StringType(), True),
        StructField("proto", StringType(), True),
        StructField("state", StringType(), True),
        StructField("dur", DoubleType(), True),
        StructField("sbytes", LongType(), True),
        StructField("dbytes", LongType(), True),
        StructField("attack_cat", StringType(), True),
        StructField("Label", IntegerType(), True),
        StructField("Stime", StringType(), True),
    ]
)

# ─── 3. Đọc stream từ Kafka ────────────────────────────────────────────────

raw_stream = (
    spark.readStream.format("kafka")
    .option("kafka.bootstrap.servers", bootstrap_servers)
    .option("subscribe", topic)
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
    .withColumn(
        "event_time", from_unixtime(col("Stime").cast("long")).cast("timestamp")
    )
    .filter(col("event_time").isNotNull())
)

# ─── Các DataFrame cho từng mode ──────────────────────────────────────────

# Mode 1 — APPEND: raw records
# Mỗi batch chỉ in những row MỚI, không reprint lại row cũ.
# Dùng cho: raw record, non-aggregated stream.
# KHÔNG dùng được với aggregation (trừ khi có watermark).
df_append = parsed_stream.select(
    "event_time", "srcip", "dstip", "proto", "attack_cat", "Label"
)

# Mode 2 — UPDATE: window aggregation + watermark
# Mỗi batch chỉ in những row THAY ĐỔI so với batch trước.
# Dùng cho: aggregation với watermark (window functions).
# Tiết kiệm hơn complete vì không reprint toàn bộ.
df_update = (
    parsed_stream.withWatermark("event_time", "10 seconds")
    .groupBy(window(col("event_time"), "5 minutes"))
    .agg(
        count("*").alias("total_packets"),
        sum(when(col("Label") == 1, 1).otherwise(0)).alias("total_attacks"),
    )
    .select(
        col("window.start").alias("window_start"),
        col("window.end").alias("window_end"),
        col("total_packets"),
        col("total_attacks"),
    )
)

# Mode 3 — COMPLETE: running total theo loại attack
# Mỗi batch reprint TOÀN BỘ kết quả từ đầu đến giờ.
# Dùng cho: aggregation không có watermark, muốn thấy running total.
# Tốn memory hơn vì Spark phải giữ toàn bộ state.
# KHÔNG dùng được với watermark.
df_complete = (
    parsed_stream.filter(col("Label") == 1)
    .groupBy("attack_cat")
    .agg(count("*").alias("total_count"))
)

# ─── Helper functions ─────────────────────────────────────────────────────


def stop_all_queries():
    for q in spark.streams.active:
        q.stop()


def wait_for_esc(q):
    """Vòng lặp chờ ESC — dừng query và về menu khi nhấn ESC."""
    print("  (Press ESC to return to menu)\n")
    # Original loop, only work for Windows
    if os == "nt":
        while q.isActive:
            if msvcrt.kbhit():
                key = msvcrt.getch()
                if key == b"\x1b":  # ESC = byte 0x1b
                    print("\n⏹  Query stopped.")
                    q.stop()
                    break
    else:
        # Reading raw keyboard on non Windows
        orig_settings = termios.tcgetattr(sys.stdin)
        tty.setcbreak(sys.stdin)
        while q != chr(27):  # ESC
            q = sys.stdin.read(1)[0]
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, orig_settings)
    time.sleep(0.1)


def print_menu():
    print("\n" + "=" * 50)
    print("  STREAM PROCESSOR — Select output mode")
    print("=" * 50)
    print("  1. [APPEND]   Raw records every 10 seconds")
    print("  2. [UPDATE]   Packet count every 5 minutes")
    print("  3. [COMPLETE] Running total attacks by category")
    print("  4. Exit")
    print("=" * 50)


# ─── Các query runners ────────────────────────────────────────────────────


def run_append():
    print("\n▶ Running APPEND mode...\n")
    q = (
        df_append.writeStream.outputMode("append")
        .format("console")
        .option("truncate", False)
        .option("numRows", 10)
        .option("checkpointLocation", f"{checkpoint_base}/raw_append")
        .trigger(processingTime="10 seconds")
        .queryName("raw_append")
        .start()
    )
    wait_for_esc(q)


def run_update():
    print("\n▶ Running UPDATE mode...\n")
    q = (
        df_update.writeStream.outputMode("update")
        .format("console")
        .option("truncate", False)
        .option("numRows", 10)
        .option("checkpointLocation", f"{checkpoint_base}/window_update")
        .trigger(processingTime="10 seconds")
        .queryName("window_update")
        .start()
    )
    wait_for_esc(q)


def run_complete():
    print("\n▶ Running COMPLETE mode...\n")
    q = (
        df_complete.writeStream.outputMode("complete")
        .format("console")
        .option("truncate", False)
        .option("numRows", 20)
        .option("checkpointLocation", f"{checkpoint_base}/attack_complete")
        .trigger(processingTime="10 seconds")
        .queryName("attack_complete")
        .start()
    )
    wait_for_esc(q)


# ─── Main loop ────────────────────────────────────────────────────────────

ACTIONS = {"1": run_append, "2": run_update, "3": run_complete}

while True:
    print_menu()
    try:
        choice = input("\n  Select option (1-4): ").strip()
    except KeyboardInterrupt:
        print("\n\n👋 Exit.")
        stop_all_queries()
        spark.stop()
        break

    if choice in ACTIONS:
        stop_all_queries()
        ACTIONS[choice]()
    elif choice == "4":
        print("\n👋 Exit.")
        stop_all_queries()
        spark.stop()
        break
    else:
        print("\n  ⚠️  Invalid choice, please enter 1-4.")
