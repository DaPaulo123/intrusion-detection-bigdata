from flask import Flask, jsonify
from pymongo import MongoClient

app = Flask(__name__)

client = MongoClient("mongodb://localhost:27017/")
db = client["intrusion_detection"]
collection = db["alerts"]

@app.route("/alerts", methods=["GET"])
def get_alerts():
    alerts = list(collection.find({}, {"_id": 0}))
    return jsonify(alerts)

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "running"})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)