import os
import sys
import time
import json
import random
import urllib.request
import urllib.error
import csv

# Thông số API Backend
API_URL = "http://localhost:5000/api/predict"

def main():
    print("🚀 Bắt đầu giả lập luồng dữ liệu mạng DỰA TRÊN DATA THẬT...")
    print(f"🔗 Đích đến: {API_URL}")
    print("Nhấn Ctrl+C để dừng.\n")
    
    # Lấy đường dẫn tuyệt đối tới file CSV thật
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(script_dir, "..", "..", "data", "UNSW-NB15_4.csv")
    
    if not os.path.exists(csv_path):
        print(f"❌ Không tìm thấy file {csv_path}. Vui lòng kiểm tra lại!")
        sys.exit(1)

    # Khai báo 49 cột của dataset gốc
    columns = [
        "srcip", "sport", "dstip", "dsport", "proto", "state", "dur", "sbytes", "dbytes", "sttl", "dttl", 
        "sloss", "dloss", "service", "sload", "dload", "spkts", "dpkts", "swin", "dwin", "stcpb", "dtcpb", 
        "smean", "dmean", "trans_depth", "res_bdy_len", "sjit", "djit", "stime", "ltime", "sintpkt", "dintpkt", 
        "tcprtt", "synack", "ackdat", "is_sm_ips_ports", "ct_state_ttl", "ct_flw_http_mthd", "is_ftp_login", 
        "ct_ftp_cmd", "ct_srv_src", "ct_srv_dst", "ct_dst_ltm", "ct_src_ltm", "ct_src_dport_ltm", 
        "ct_dst_sport_ltm", "ct_dst_src_ltm", "attack_cat", "label"
    ]

    print("⏳ Đang load file CSV thật lên bộ nhớ... (vài giây)")
    packets = []
    try:
        with open(csv_path, mode='r', encoding='utf-8') as f:
            reader = csv.reader(f)
            # Lấy ngẫu nhiên khoảng 50,000 dòng để test thôi (đọc tất cả sẽ nặng RAM)
            for i, row in enumerate(reader):
                if random.random() < 0.1:  # Lấy 10% dữ liệu
                    packet = dict(zip(columns, row))
                    # Convert số liệu sang kiểu Float/Int nếu cần
                    for k, v in packet.items():
                        try:
                            packet[k] = float(v) if '.' in v else int(v)
                        except ValueError:
                            pass # Giữ nguyên chuỗi
                    packets.append(packet)
    except Exception as e:
         print(f"❌ Lỗi đọc CSV: {e}")
         sys.exit(1)

    print(f"✅ Đã chuẩn bị {len(packets)} gói tin thực tế.")
    
    count = 0
    try:
        while True:
            # Chọn bừa 1 gói tin từ data thật
            packet = random.choice(packets)
            
            # Gửi qua HTTP POST
            data = json.dumps(packet).encode("utf-8")
            req = urllib.request.Request(API_URL, data=data, headers={"Content-Type": "application/json"}, method="POST")
            
            try:
                response = urllib.request.urlopen(req)
                resp_data = json.loads(response.read().decode("utf-8"))
                
                print(f"[{count+1}] Đã gửi gói tin từ {packet['srcip']} -> {packet['dstip']}")
                
                # In kết quả AI dự đoán
                if resp_data.get("data", {}).get("is_attack"):
                    ai_cat = resp_data['data']['attack_cat']
                    real_cat = str(packet['attack_cat']).strip()
                    conf = resp_data['data']['confidence']
                    
                    # Nếu file gốc để trống attack_cat thì nó là Normal (thỉnh thoảng label=1 nhưng cat trống)
                    if not real_cat: real_cat = "Normal"
                    
                    print(f"   🚨 AI Phát hiện : {ai_cat} (Độ tin cậy: {conf:.2f})")
                    print(f"   👁️ Nhãn Thực tế: {real_cat}")
                    if ai_cat.lower() == real_cat.lower():
                        print("   --> 🎯 AI ĐOÁN CHÍNH XÁC!")
                    else:
                        print("   --> ⚠️ AI Đoán sai (Trường hợp này sẽ làm giảm Accuracy)")
                else:
                    print(f"   ✅ Bình thường")
                    
            except urllib.error.URLError as e:
                print(f"❌ Không thể kết nối tới Backend: {e.reason}")
                break
                
            count += 1
            # Đợi 2-4 giây rồi gửi tiếp
            time.sleep(random.uniform(2.0, 4.0))
            
    except KeyboardInterrupt:
        print("\n👋 Đã dừng giả lập.")

if __name__ == "__main__":
    main()
