import json
import time
import os
import pandas as pd
import tomllib
from kafka import KafkaProducer

with open("settings.toml", mode="rb") as f:
    config = tomllib.load(f)

col_info = pd.read_csv(config["simulation"]["csv_header_path"], encoding="cp1252")
# Chuyển toàn bộ tên cột thành chữ thường để chuẩn hóa với Model AI
col_header = [str(name).lower().strip() for name in col_info["Name"]]

# Maybe add type checking here?
df = pd.read_csv(
    config["simulation"]["csv_sim_path"],
    names=col_header,
)

# Lấy toàn bộ dữ liệu file số 4 (Hơn 440,000 dòng)
# df = df.head(50000) # Đã bỏ giới hạn
df = df.sort_values("stime")

# So far nothing yet
producer = KafkaProducer(
    bootstrap_servers=os.environ.get(
        "KAFKA_BOOTSTRAP_SERVERS", config["kafka"]["bootstrap_servers"]
    ),
    retries=config["kafka"]["retries"],
    acks=config["kafka"]["acks"],
    value_serializer=lambda x: json.dumps(x).encode("utf-8"),
)

print(f"Streaming {len(df)} packets...")
for _, row in df.iterrows():
    producer.send("network_traffic", value=row.to_dict())
    time.sleep(0.2) # Khoảng 50 gói / giây

producer.flush()
print("Stream complete!")
