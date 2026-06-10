# Phần 4: Huấn luyện Mô hình Học Máy (Machine Learning)

Trong kiến trúc Network Intrusion Detection System (IDS), **Phân hệ Học Máy** đóng vai trò là "Bộ não". Đặc biệt, để giải quyết triệt để vấn đề mất cân bằng dữ liệu (Class Imbalance) giữa các cuộc tấn công khổng lồ (DoS) và các loại mã độc hiếm (Worms, Shellcode), dự án đã nâng cấp lên **Kiến trúc Phân loại 2 Lớp (Two-Stage Classifier)** sử dụng thuật toán **XGBoost (Extreme Gradient Boosting)**.

---

## Kiến trúc và Luồng xử lý (Two-Stage ML)

```text
ml/two_stage_xgb_model.py  (Entry point)
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
│     └── Thuật toán: XGBoost (n_estimators=100, max_depth=6).
│
├── [4] Stage 2 (Chuyên Gia Bắt Bệnh - Multiclass Classification)
│     ├── Nhiệm vụ: Chi tiết hóa loại mã độc (DoS, Fuzzers, Worms, Shellcode...).
│     ├── Dữ liệu học: CHỈ học trên các gói tin thực sự là Tấn công (Bỏ qua Normal).
│     ├── Vũ khí đặc biệt: Kích hoạt Trọng số phạt (Class Weights) để bắt các mã độc siêu hiếm.
│     └── Thuật toán: XGBoost (n_estimators=150, max_depth=6, weight_col="class_weight").
│
└── [5] Đánh giá & Xuất Mô hình (Model Persistence)
      ├── Kết nối luồng dự đoán (Cascade Logic).
      └── Lưu 3 Model Pipeline vào thư mục models/ ở root.
```

### Tại sao chọn XGBoost thay vì Random Forest?
- **Độ chính xác cao hơn:** XGBoost xây dựng cây tuần tự, cây sau học từ sai lầm của cây trước (Gradient Boosting), nắm bắt mẫu dữ liệu phức tạp hơn.
- **Xử lý mất cân bằng dữ liệu tốt hơn:** Hỗ trợ trực tiếp `weight_col` và `scale_pos_weight` để tối ưu Recall cho các nhóm thiểu số.
- **Tích hợp Regularization (L1, L2):** Giúp chống overfitting tốt hơn RF trên tập dữ liệu 3 triệu dòng.
- **Tốc độ Inference nhanh hơn:** Cây nông hơn, tối ưu hóa toán học tốt hơn → phù hợp cho Real-time Detection.

### Tại sao dùng Kiến trúc Two-Stage?
Nếu gộp chung 1 bước, núi dữ liệu `Normal` và `DoS` (chiếm 90%) sẽ đè bẹp hoàn toàn các mã độc nhỏ như `Worms`. Bằng cách thiết lập Stage 2 chỉ phân tích "tội phạm", mô hình tập trung tối đa sự chú ý vào các đặc trưng tinh tế của các mã độc hiếm mà không bị nhiễu.

---

## Cấu trúc file

```text
ml/
├── two_stage_xgb_model.py  ← Entry point chính (Nên chạy file này)
├── xgb_model.py            ← Entry point đơn giản (Single-stage XGBoost)
├── train_model.py          ← Module cung cấp hàm train_xgboost, add_class_weights
└── evaluate.py             ← Module tính metrics & in báo cáo (Hỗ trợ cả RF & XGBoost)
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
python ml/two_stage_xgb_model.py
```

---

## Tổng hợp Kết quả

| Metric | Giá trị (Two-Stage XGBoost + Class Weights) |
|---|---|
| **Cấu trúc Cây (Stage 1)** | 100 cây, max_depth=6 |
| **Cấu trúc Cây (Stage 2)** | 150 cây, max_depth=6 |

---
Tất cả các mô hình đã được trích xuất thành công vào thư mục `models/` ở gốc dự án, sẵn sàng cho Hệ thống **Web API (Serving Layer)** tải lên và quét gói tin Real-time.
