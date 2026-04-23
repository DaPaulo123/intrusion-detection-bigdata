from flask import Flask, jsonify
from pymongo import MongoClient
import os
from dotenv import load_dotenv
load_dotenv()
app = Flask(__name__)
client = MongoClient(os.environ.get("MONGO_URI"))

db = client["intrusion_detection"]
collection = db["alerts"]

@app.route("/alerts", methods=["GET"])
def get_alerts():
    alerts = list(collection.find({}, {"_id": 0}).sort('timestamp', -1))
    return jsonify(alerts)

@app.route("/alerts/<attack_cat>", methods=["GET"]) 
def get_alerts_by_type(attack_cat):
    alerts = list(collection.find({"attack_cat": attack_cat}, {"_id": 0}).sort('timestamp', -1))
    return jsonify(alerts)

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "running"})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)