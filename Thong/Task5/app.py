from flask import Flask, jsonify
from pymongo import MongoClient

app = Flask(__name__)

@app.route('/api/alerts', methods=['GET'])
def get_alerts():
    try:
        # Kết nối tới MongoDB
        client = MongoClient("mongodb://admin:password123@localhost:27017/?authSource=admin")
        db = client["ids_database"]
        # Lấy dữ liệu từ collection 'alerts'
        logs = list(db.alerts.find({}, {'_id': 0}).sort("_id", -1).limit(20))
        return jsonify(logs)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == '__main__':
    print("🌐 Dashboard đang chạy tại: http://127.0.0.1:5000/api/alerts")
    app.run(host='0.0.0.0', port=5000, debug=True)