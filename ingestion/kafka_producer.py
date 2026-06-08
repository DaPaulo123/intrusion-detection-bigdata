import json
import os
import time
from pathlib import Path

import pandas as pd
import tomllib  # Python 3.11+

# try:
#    import tomllib  # Python 3.11+
# except ImportError:
#     import tomli as tomllib  # Python 3.10 trở xuống
from kafka import KafkaProducer


# Try to get value from following orders: global env, config file, default value
def get_env(global_env: str, config, config_path: list[str], default_value):
    value = os.environ.get(global_env)
    if value is None:
        config_value = config
        for item in config_path:
            config_value = config_value.get(item, {})
        value = config_value
    if value is None:
        value = default_value
    return value


current_dir = Path(__file__).parent
with open(current_dir / "settings.toml", mode="rb") as f:
    config = tomllib.load(f)

# Windows file format again
col_info = pd.read_csv(
    current_dir / config["simulation"]["csv_header_path"], encoding="cp1252"
)
col_header = list(col_info["Name"])

# Maybe add type checking here?
df = pd.read_csv(
    current_dir / config["simulation"]["csv_sim_path"],
    names=col_header,
    low_memory=False,
)
df["Stime"] = pd.to_numeric(df["Stime"], errors="coerce")
df = df.dropna(subset=["Stime"])
df = df.sort_values("Stime")
df = df.fillna(0)

# So far nothing yet
producer = KafkaProducer(
    bootstrap_servers=get_env(
        "KAFKA_BOOTSTRAP_SERVERS",
        config,
        ["kafka", "bootstrap_servers"],
        "localhost:9092",
    ),
    retries=config["kafka"]["retries"],
    acks=config["kafka"]["acks"],
    value_serializer=lambda x: json.dumps(x).encode("utf-8"),
)

print(f"Streaming {len(df)} packets...")
for _, row in df.iterrows():
    producer.send(config["simulation"]["topic_name"], value=row.to_dict())
    # producer.send("network_traffic", value=row.to_json())
    time.sleep(0.001)

producer.flush()
print("Stream complete!")
