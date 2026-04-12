# Ingestion module setup

This module handles ingesting data into the pipeline using Kafka.

## How to run Kafka locally

1. Make sure you have Docker and Docker Compose installed.
2. In the root directory `intrusion-detection-bigdata`, start the Kafka cluster (Zookeeper & Kafka):

```bash
docker-compose up -d
```

3. To check if the containers are running properly, use:

```bash
docker-compose ps
```

## How to send test data

To send 5 test JSON packets to Kafka:

1. Install the Python dependencies (ensure you have a virtual environment set up if preferred):

```bash
pip install -r requirements.txt
```

2. Run the `kafka_producer.py` script:

```bash
cd ingestion
python kafka_producer.py
```

This will connect to the local Kafka broker (`localhost:9092`), wait until it is available, send 5 JSON packets to the `test-topic`, and then exit.

## View Data in Kafka
You can use a GUI tool like Offset Explorer to view the real-time messages residing inside Kafka topics:

![Offset Explorer Data View](../docs/images/kafka_explorer_test.png)
