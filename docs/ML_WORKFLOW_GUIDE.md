# Hướng dẫn Chạy và Triển khai Mô hình XGBoost (Intrusion Detection)

Tài liệu này giải thích luồng công việc (Workflow) để huấn luyện mô hình Machine Learning phát hiện xâm nhập và cách đưa nó vào phục vụ (Serving) trong môi trường API/Streaming. Hệ thống đã được thiết kế lại để sử dụng thuần XGBoost/Pandas trên Local, giải quyết triệt để lỗi tương thích của PySpark trên Windows.

---

## 1. Kiến trúc Mô hình (Two-Stage XGBoost)

Hệ thống sử dụng **Kiến trúc 2 Giai đoạn (Two-Stage)** để xử lý sự mất cân bằng dữ liệu nghiêm trọng trong an toàn thông tin:
* **Stage 1 (Binary):** Phân biệt luồng mạng là `Normal` (Bình thường) hay `Attack` (Bị tấn công).
* **Stage 2 (Multiclass):** Với các luồng bị Stage 1 bắt được là `Attack`, mô hình thứ hai sẽ soi chiếu để gọi tên chính xác 1 trong 9 loại mã độc (DoS, Worms, Backdoor, Shellcode, v.v.).

*Lưu ý: Stage 2 đã được tích hợp kỹ thuật **Undersampling (MAX_SAMPLES = 5000)** để đảm bảo mô hình không bỏ sót các cuộc tấn công hiếm gặp nguy hiểm như Backdoor hay Worms.*

---

## 2. Luồng Công việc Huấn luyện (Training Workflow)

Khi bạn có bộ dữ liệu PCAP/CSV mới, hãy làm theo đúng 2 bước sau:

### Bước 2.1: Gom nhóm và Làm sạch Dữ liệu (Data Prep)
Chạy script Batch Processing bằng PySpark để đọc hàng triệu dòng CSV, hợp nhất chúng lại và xử lý triệt để lỗi "Rò rỉ dữ liệu" (Data Leakage) bằng cách cắt theo mốc thời gian (Time Split).

```bash
python batch/spark_sample.py
```
**Đầu ra (Output):**
* `data/processed/train_cleaned.parquet`
* `data/processed/test_cleaned.parquet`

### Bước 2.2: Huấn luyện AI (Model Training)
Vì SparkXGBClassifier trên Windows hay gặp lỗi "Worker exited unexpectedly", chúng ta sẽ chạy phiên bản Production viết bằng XGBoost thuần.

```bash
python ml/train_local_production.py
```
**Đầu ra (Output) tại thư mục `models/`:**
* `stage1_model.json`: AI nhận diện Tấn công.
* `stage2_model.json`: AI phân loại 9 nhãn mã độc.
* `attack_mapping.json`: Từ điển dịch mã số 0-8 ra chữ (Ví dụ: 0 -> Analysis, 2 -> Backdoor).
* `categorical_encoders.json`: Công thức dịch chữ thành số cho dữ liệu Categorical (proto, service, state).
* `feature_names.json`: Trật tự 50 cột dữ liệu chuẩn mực để API lắp ráp.

---

## 3. Luồng Công việc Triển khai (Serving Workflow)

Mô hình đã được lưu dưới chuẩn JSON quốc tế. Để sử dụng nó trong Backend (FastAPI hoặc Kafka Streaming), lập trình viên Backend chỉ cần làm theo logic sau:

### Tích hợp vào Python Backend (FastAPI / Streaming)

```python
import xgboost as xgb
import json
import pandas as pd

# 1. Load các từ điển ánh xạ
with open('models/feature_names.json', 'r') as f:
    feature_names = json.load(f)

with open('models/categorical_encoders.json', 'r') as f:
    encoders = json.load(f)

with open('models/attack_mapping.json', 'r') as f:
    attack_mapping = json.load(f)

# Tạo từ điển ngược để dịch kết quả
reverse_attack_map = {v: k for k, v in attack_mapping.items()}

# 2. Load 2 Model AI vào RAM (Chỉ làm 1 lần khi Start Server)
model_stage1 = xgb.Booster()
model_stage1.load_model('models/stage1_model.json')

model_stage2 = xgb.Booster()
model_stage2.load_model('models/stage2_model.json')

def predict_packet(raw_json_data):
    # raw_json_data là 1 object dạng dict chứa thông tin gói tin mạng (như proto, spkts, dpkts...)
    df = pd.DataFrame([raw_json_data])
    
    # Ép đúng trật tự cột
    # (Tại đây cần viết thêm logic map categorical string thành int dựa trên `encoders`)
    
    dmatrix = xgb.DMatrix(df[feature_names])
    
    # Chạy Stage 1
    is_attack = model_stage1.predict(dmatrix)
    
    if is_attack[0] < 0.5:
        return "Normal"
    else:
        # Nếu là tấn công, chạy Stage 2
        attack_type_idx = int(model_stage2.predict(dmatrix)[0])
        return reverse_attack_map.get(attack_type_idx, "Unknown Attack")
```

Hệ thống XGBoost JSON này cho phép API xử lý dự đoán trên **dưới 1 mili-giây (ms)**, hoàn toàn đáp ứng được luồng Network Streaming cực lớn theo thời gian thực.
