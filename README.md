# intrusion-detection-bigdata
Real-time Network Intrusion Detection System using Kafka, Spark, and MLlib

This project builds a real-time network intrusion detection system 
using a Lambda architecture. It processes network traffic from the 
UNSW-NB15 dataset to classify attacks with high accuracy as they 
happen — detecting threats within seconds of occurrence. The system 
is designed to be scalable and extensible for future network 
security use cases.

## Setup & Installation

### Prerequisites
- Python 3.10+
- Docker Desktop
- Conda (Anaconda or Miniconda) — optional but recommended

### 1. Clone the repository
git clone https://github.com/your-repo-url
cd intrusion-detection-bigdata

### 2. Create and activate environment

# Option A — with conda (recommended)
conda create -n bigdata python=3.10
conda activate bigdata

# Option B — with plain Python venv
python -m venv bigdata
# Windows:
bigdata\Scripts\activate
# Mac/Linux:
source bigdata/bin/activate

### 3. Install dependencies
pip install -r requirements.txt

### 4. Start all services
docker-compose up -d

### 5. Verify services are running
docker ps
# You should see: kafka, zookeeper, mongodb

### 6. Run the API
cd serving/api
python app.py

### 7. Test the API
Open browser at http://localhost:5000/health
Open browser at http://localhost:5000/alerts


## Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Ingestion | Apache Kafka | Real-time stream ingestion |
| Batch Storage | HDFS (Hadoop) | Historical data storage |
| Processing | Apache Spark (PySpark) | Batch + stream processing |
| Stream Processing | Spark Structured Streaming | Real-time classification |
| ML | Spark MLlib | Model training + inference |
| Graph Analysis | GraphFrames | Network topology analysis |
| Serving | MongoDB | Store results + alerts |
| Cache | Redis | Real-time model results |
| API | Flask | REST API for dashboard |
| Container | Docker | Service containerization |
| Orchestration | Kubernetes | Container management |

## Team

## Team

| Person | Role | Responsibilities |
|--------|------|-----------------|
| A | Data Ingestion | Replay UNSW-NB15 dataset through Kafka, define message schemas |
| B | Batch Processing | Preprocess raw data, engineer features, analyze historical patterns |
| C | Stream Processing | Classify network packets in real-time using Spark Structured Streaming |
| D | ML + Analytics | Train and evaluate intrusion detection model, optimize accuracy |
| E | Serving + Deploy | REST API, MongoDB storage, dashboard, Docker deployment |