from flask import Flask, jsonify
from pymongo import MongoClient
import os
from dotenv import load_dotenv
from flask import request, abort
from flask import send_from_directory
from bson import ObjectId
load_dotenv()
app = Flask(__name__)
client = MongoClient(os.environ.get("MONGO_URI"))
def check():
    key = request.headers.get("X-API-Key")
    if key != os.environ.get("API_KEY"):
        abort(403)

db = client["intrusion_detection"]
collection = db["alerts"]


@app.route("/alerts", methods=["GET"])
def get_alerts():
    # check()
    alerts = list(collection.find({}).sort('timestamp', -1))
    for alert in alerts:
        alert['_id'] = str(alert['_id'])
    return jsonify(alerts)

@app.route("/alerts/<attack_cat>", methods=["GET"]) 
def get_alerts_by_type(attack_cat):
    check()
    alerts = list(collection.find({"attack_cat": attack_cat}).sort('timestamp', -1))
    for alert in alerts:
        alert['_id'] = str(alert['_id'])
    return jsonify(alerts)

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "running"})

@app.route("/dashboard")
def dashboard():
    return send_from_directory("../dashboard", "index.html")

@app.route("/alerts/<alert_id>/status", methods=["PUT"])
def update(alert_id):
    stat = request.json.get("status")
    collection.update_one({"_id": ObjectId(alert_id)}, {"$set": {"status": stat}})
    return "Done"

@app.route("/analytics/attack-distribution", methods=["GET"])
def attack_distribution():
    pipeline = [
        {"$group": {"_id": "$attack_cat", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    results = list(collection.aggregate(pipeline))
    for r in results:
        r["attack_cat"] = r.pop("_id")
    return jsonify(results)

@app.route("/analytics/recent-summary", methods=["GET"])
def recent_summary():
    total = collection.count_documents({})
    unverified = collection.count_documents({"status": "unverified"})
    confirmed = collection.count_documents({"status": "confirmed"})
    resolved = collection.count_documents({"status": "resolved"})
    return jsonify({
        "total": total,
        "unverified": unverified,
        "confirmed": confirmed,
        "resolved": resolved
    })

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)


