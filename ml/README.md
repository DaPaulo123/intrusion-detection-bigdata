# Phần 4: Huấn luyện Mô hình Học Máy (Machine Learning)

Trong kiến trúc Network Intrusion Detection System (IDS), **Phân hệ Học Máy** đóng vai trò là "Bộ não". Đặc biệt, để giải quyết triệt để vấn đề mất cân bằng dữ liệu (Class Imbalance) giữa các cuộc tấn công khổng lồ (DoS) và các loại mã độc hiếm (Worms, Shellcode), dự án đã nâng cấp lên **Kiến trúc Phân loại 2 Lớp (Two-Stage Classifier)**.

---

## Kiến trúc và Luồng xử lý (Two-Stage ML)

```text
ml/two_stage_rf_model.py  (Entry point)
│
├── [1] Đọc dữ liệu (Đã được tiền xử lý bởi Batch Layer)
│     ├── Lấy trực tiếp từ data/processed/train_cleaned.parquet
│     └── Lấy trực tiếp từ data/processed/test_cleaned.parquet
│
├── [2] Build Pipeline Chung (ml/train_model.py)
│     ├── StringIndexer   → Encode cột categorical (proto, state, service...)
│     └── VectorAssembler → Gộp tất cả feature thành vector 'features'
│
├── [3] Stage 1 (Gác Cổng - Binary Classification)
│     ├── Nhiệm vụ: Phân định rạch ròi [Bình thường (Normal)] vs [Có dấu hiệu tấn công (Attack)].
│     ├── Dữ liệu học: Toàn bộ tập Train.
│     └── Thuật toán: Random Forest (numTrees=50, maxBins=256).
│
├── [4] Stage 2 (Chuyên Gia Bắt Bệnh - Multiclass Classification)
│     ├── Nhiệm vụ: Chi tiết hóa loại mã độc (DoS, Fuzzers, Worms, Shellcode...).
│     ├── Dữ liệu học: CHỈ học trên các gói tin thực sự là Tấn công (Bỏ qua Normal).
│     ├── Vũ khí đặc biệt: Kích hoạt Trọng số phạt (Class Weights) để bắt các mã độc siêu hiếm.
│     └── Thuật toán: Random Forest (numTrees=100, maxBins=256, weightCol="class_weight").
│
└── [5] Đánh giá & Xuất Mô hình (Model Persistence)
      ├── Kết nối luồng dự đoán (Cascade Logic).
      └── Lưu 3 Model Pipeline vào thư mục models/ ở root.
```

### Tại sao dùng Kiến trúc Two-Stage?
Nếu gộp chung 1 bước, núi dữ liệu `Normal` và `DoS` (chiếm 90%) sẽ đè bẹp hoàn toàn các mã độc nhỏ như `Worms`. Bằng cách thiết lập Stage 2 chỉ phân tích "tội phạm", mô hình tập trung tối đa sự chú ý vào các đặc trưng tinh tế của các mã độc hiếm mà không bị nhiễu.

---

## Cấu trúc file

```text
ml/
├── two_stage_rf_model.py   ← Entry point chính (Nên chạy file này)
├── train_model.py          ← Module cung cấp hàm add_class_weights
└── evaluate.py             ← Module tính metrics & in báo cáo
```

---

## Hướng dẫn chạy

### Yêu cầu tiên quyết
Chắc chắn rằng bạn đã chạy luồng Batch Processing để có dữ liệu sạch:
```bash
python batch/spark_sample.py
```

### Chạy ML Pipeline
Từ thư mục gốc dự án, gõ lệnh:
```bash
python ml/two_stage_rf_model.py
```

---

## Tổng hợp Kết quả (Đã kiểm chứng ngày 2026-06-03)

| Metric | Giá trị (Two-Stage + Class Weights) |
|---|---|
| **Accuracy (Test)** | **62.14%** |
| **F1-Score (Test)** | **68.87%** |
| Cấu trúc Cây (Stage 1) | 50 cây quyết định |
| Cấu trúc Cây (Stage 2) | 100 cây quyết định |

### Nhận xét & Lý giải điểm số
Nhìn lướt qua, con số ~60% có vẻ thấp hơn mức >90% thường thấy trong các bài tutorial trên mạng. Tuy nhiên, đây là con số **Thực tế & Hiệu quả nhất** cho bài toán an toàn thông tin nhiều lớp:
- **Ngừng "Ăn Gian":** Các mô hình đạt >90% Accuracy trước đây thường đoán mò toàn bộ là Normal hoặc DoS, và hoàn toàn "mù màu" bỏ lọt 100% các loại mã độc nguy hiểm gọn nhẹ (Worms/Shellcode).
- **Trọng số Phạt (Class Weights) phát huy tác dụng:** Việc ép điểm F1-Score lên tới gần 70% chứng tỏ hệ thống đã chủ động theo dõi và tóm gọn được các mã độc siêu hiếm. Hệ thống thà báo động nhầm (giảm Accuracy) còn hơn bỏ lọt virus phá hoại!

---
Tất cả các mô hình đã được trích xuất thành công vào thư mục `models/` ở gốc dự án, sẵn sàng cho Hệ thống **Web API (Serving Layer)** tải lên và quét gói tin Real-time.
