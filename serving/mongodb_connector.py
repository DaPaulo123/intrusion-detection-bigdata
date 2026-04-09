from pymongo import MongoClient

client = MongoClient("mongodb+srv://admin:bigdata2025@cluster0.lsq1xwd.mongodb.net/?appName=Cluster0")

db = client["intrusion_detection"]
collection = db["alerts"]

fake_alert = {
    "srcip": "192.168.1.105",
    "dstip": "10.0.0.1",
    "attack_cat": "DoS",
    "confidence": 0.94,
    "timestamp": "2024-01-15T10:23:01"
}

result = collection.insert_one(fake_alert)
print(f"Inserted alert with id: {result.inserted_id}")

alert = collection.find_one({"attack_cat": "DoS"})
print(f"Retrieved: {alert}")