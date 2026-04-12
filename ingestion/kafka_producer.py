import json
import logging
import time

import pandas as pd
import tomllib
from kafka import KafkaProducer

# TODO: Add logging
# Logging is good
# logger = logging.getLogger(__name__)
# logging.basicConfig(filename="log_producer.txt", level=logging.INFO)

with open("config.toml", mode="rb") as f:
    config = tomllib.load(f)
    # logging.info("Loading config file")


col_info = pd.read_csv(config["csv_header_path"], encoding="cp1252")
col_header = list(col_info["Name"])

# Maybe add type checking here?
df = pd.read_csv(
    config["csv_sim_path"],
    names=col_header,
)
df = df.sort_values("Stime")

# So far nothing yet
producer = KafkaProducer(
    bootstrap_servers=config["bootstrap_servers"],
    value_serializer=lambda x: json.dumps(x).encode("utf-8"),
)

for _, row in df.iterrows():
    producer.send("network_traffic", value=row.to_json())
    time.sleep(0.01)

producer.flush()
