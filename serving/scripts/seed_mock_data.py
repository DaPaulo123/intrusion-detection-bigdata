import os
import sys
import random
from datetime import datetime, timedelta, timezone
from pymongo import MongoClient

# Thêm thư mục backend vào path để import config
_here = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(os.path.dirname(_here), "backend"))

try:
    from config import Config
    mongo_uri = Config.MONGO_URI
    db_name = Config.DB_NAME
    alerts_col = Config.ALERTS_COLLECTION
    batch_col = Config.BATCH_STATS_COLLECTION
except ImportError:
    # Fallback nếu chạy độc lập mà không có path
    mongo_uri = os.environ.get("MONGO_URI", "mongodb://localhost:27017/")
    db_name = "intrusion_detection"
    alerts_col = "alerts"
    batch_col = "batch_stats"

print(f"Connecting to MongoDB: {mongo_uri}")
client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
db = client[db_name]

# 1. Seed alerts collection
print("Clearing alerts collection...")
db[alerts_col].delete_many({})

attack_categories = ["Normal", "DoS", "Fuzzers", "Exploits", "Worms", "Shellcode", "Analysis", "Backdoor", "Generic", "Reconnaissance"]
ips_source = ["192.168.1.105", "10.0.0.15", "172.16.5.4", "192.168.2.20", "192.168.1.50", "10.10.10.8"]
ips_dest = ["203.0.113.5", "198.51.100.12", "8.8.8.8", "1.1.1.1", "192.168.1.1", "10.0.0.1"]
protocols = ["tcp", "udp", "icmp"]

now = datetime.now(timezone.utc)

alerts_data = []

# Tạo các cảnh báo cũ hơn
for i in range(50):
    time_diff = random.randint(11, 1440) # từ 11 phút đến 24 giờ trước
    alert_time = now - timedelta(minutes=time_diff)
    attack = random.choice(attack_categories)
    
    # Normal thì không có confidence cao hoặc không coi là alert thực sự nhưng ta vẫn lưu hoặc bỏ qua
    is_normal = (attack == "Normal")
    confidence = random.uniform(0.1, 0.4) if is_normal else random.uniform(0.65, 0.99)
    threat_score = random.randint(5, 30) if is_normal else random.randint(50, 100)
    
    status = random.choice(["pending", "handled"])
    resolved_by = "Admin SOC" if status == "handled" else None
    
    alerts_data.append({
        "srcip": random.choice(ips_source),
        "dstip": random.choice(ips_dest),
        "proto": random.choice(protocols),
        "attack_cat": attack,
        "confidence": round(confidence, 4),
        "threat_score": threat_score,
        "status": status,
        "resolved_by": resolved_by,
        "timestamp": alert_time.isoformat().replace("+00:00", "Z")
    })

# Tạo một số cảnh báo rất mới (trong vòng 10 phút gần nhất) để hiển thị real-time
for i in range(8):
    time_diff = random.randint(0, 9) # 0 đến 9 phút trước
    alert_time = now - timedelta(minutes=time_diff)
    attack = random.choice([cat for cat in attack_categories if cat != "Normal"]) # các vụ tấn công
    confidence = random.uniform(0.75, 0.99)
    threat_score = random.randint(70, 100)
    
    alerts_data.append({
        "srcip": random.choice(ips_source),
        "dstip": random.choice(ips_dest),
        "proto": random.choice(protocols),
        "attack_cat": attack,
        "confidence": round(confidence, 4),
        "threat_score": threat_score,
        "status": "pending",
        "resolved_by": None,
        "timestamp": alert_time.isoformat().replace("+00:00", "Z")
    })

db[alerts_col].insert_many(alerts_data)
print(f"Successfully seeded {len(alerts_data)} alerts!")

# 2. Seed batch_stats collection
print("Clearing batch_stats collection...")
db[batch_col].delete_many({})

# Tạo thống kê giờ cao điểm (24 giờ)
peak_hours = []
# Giả định giờ cao điểm là 9h-11h sáng và 14h-16h chiều, 21h-23h tối
for hour in range(24):
    if hour in [9, 10, 11, 14, 15, 16]:
        count = random.randint(120, 250)
    elif hour in [21, 22, 23]:
        count = random.randint(150, 300)
    else:
        count = random.randint(20, 90)
    peak_hours.append({"hour": hour, "attack_count": count})

# Phân bố Threat Score
threat_score_dist = []
# Từ 0 đến 100 chia làm 10 nhóm
ranges = [
    ("0-10", random.randint(5, 15)),
    ("11-20", random.randint(10, 25)),
    ("21-30", random.randint(15, 35)),
    ("31-40", random.randint(20, 45)),
    ("41-50", random.randint(40, 80)),
    ("51-60", random.randint(80, 120)),
    ("61-70", random.randint(150, 250)),
    ("71-80", random.randint(300, 450)),
    ("81-90", random.randint(400, 600)),
    ("91-100", random.randint(250, 400))
]
for r_label, count in ranges:
    threat_score_dist.append({"range": r_label, "count": count})

# Phân bổ tấn công theo danh mục của luồng Batch (tích lũy lớn)
batch_category_summary = [
    {"attack_cat": "DoS", "count": 12450},
    {"attack_cat": "Exploits", "count": 8920},
    {"attack_cat": "Fuzzers", "count": 6430},
    {"attack_cat": "Generic", "count": 5100},
    {"attack_cat": "Reconnaissance", "count": 3400},
    {"attack_cat": "Analysis", "count": 850},
    {"attack_cat": "Backdoor", "count": 620},
    {"attack_cat": "Shellcode", "count": 310},
    {"attack_cat": "Worms", "count": 75}
]

batch_doc = {
    "peak_hours": peak_hours,
    "threat_score_distribution": threat_score_dist,
    "category_summary": batch_category_summary,
    "total_records_processed": 145890,
    "last_batch_run": now.isoformat().replace("+00:00", "Z")
}

db[batch_col].insert_one(batch_doc)
print("Successfully seeded batch_stats!")
client.close()
print("Done seeding data.")
