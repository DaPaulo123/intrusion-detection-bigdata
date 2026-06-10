from pymongo import MongoClient

client = MongoClient("mongodb://127.0.0.1:58477/")

db = client["intrusion_detection"]
collection = db["alerts"]
# collection.delete_many({})
fake_alert = {
    "srcip": "192.118.1.145",
    "dstip": "10.0.23.1",
    "attack_cat": "DoS",
    "confidence": 0.96,
    "timestamp": "2026-01-15T10:23:01",
    "status": "Unverified"
}

result = collection.insert_one(fake_alert)
print(f"Inserted alert with id: {result.inserted_id}")

alert = collection.find_one({"attack_cat": "DoS"})
print(f"Retrieved: {alert}")

