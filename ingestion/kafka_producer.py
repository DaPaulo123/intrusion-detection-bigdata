import pandas as pd
import json
import time
from kafka import KafkaProducer

df = pd.read_csv('data/raw/UNSW-NB15.csv')
df = df.sort_values('Stime')  # chronological order

producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda x: json.dumps(x).encode('utf-8')
)

print(f"Streaming {len(df)} packets...")
for _, row in df.iterrows():
    producer.send('network_traffic', value=row.to_dict())
    time.sleep(0.01)  # 100 packets/second

producer.flush()
print("Stream complete!")