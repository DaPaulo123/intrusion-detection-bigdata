import json
import time
from kafka import KafkaProducer
from kafka.errors import NoBrokersAvailable

def json_serializer(data):
    return json.dumps(data).encode('utf-8')

# Connecting to Kafka producer, retry logic included for cluster startup delays
producer = None
while producer is None:
    try:
        producer = KafkaProducer(
            bootstrap_servers=['localhost:9092'],
            value_serializer=json_serializer
        )
    except NoBrokersAvailable:
        print("Waiting for Kafka to be ready...")
        time.sleep(2)

topic = 'test-topic'

for i in range(1, 6):
    data = {
        'id': i,
        'event': 'intrusion_attempt',
        'severity': 'high',
        'source_ip': f'192.168.1.{10+i}',
        'timestamp': time.time()
    }
    producer.send(topic, data)
    print(f"Sent: {data}")
    time.sleep(1)

producer.flush()
print("Finished sending 5 JSON packets.")
