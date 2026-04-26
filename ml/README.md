# Phần 4: Huấn luyện Mô hình Học Máy (Machine Learning)

Trong kiến trúc Network Intrusion Detection System (IDS), **Phân hệ Học Máy** đóng vai trò là "Bộ não". Nó dùng tri thức đã học để phân định ranh giới giữa một gói tin Bình thường (Normal) và một gói tin có dấu hiệu Tấn công (Attack).

---

## Kiến trúc và Luồng xử lý

```
ml/rf_model.py  (Entry point)
│
├── [1] Đọc dữ liệu
│     ├── Ưu tiên: UNSW_NB15_training-set.csv + UNSW_NB15_testing-set.csv
│     └── Fallback: data/processed/UNSW_NB15_cleaned.parquet → split 80/20
│
├── [2] Tiền xử lý (dùng lại module từ batch/)
│     ├── batch/preprocessing.py   → clean_dataframe()
│     └── batch/feature_engineering.py → add_network_features()
│
├── [3] Build Pipeline (ml/train_model.py)
│     ├── StringIndexer   → encode cột categorical (proto, state, service...)
│     └── VectorAssembler → gộp tất cả feature thành vector 'features'
│
├── [4] Train Random Forest (ml/train_model.py)
│     └── RandomForestClassifier (numTrees=50, maxBins=256)
│
└── [5] Đánh giá toàn diện (ml/evaluate.py)
      ├── Accuracy, F1, Precision, Recall, AUC-ROC
      ├── Confusion Matrix
      ├── Overfit Diagnosis (Train vs Test gap)
      └── Top 10 Feature Importances
```

### Tại sao dùng lại module từ `batch/`?

`rf_model.py` import trực tiếp `preprocessing.py` và `feature_engineering.py` từ thư mục `batch/`,
đảm bảo **không có sai lệch pipeline** giữa bước xử lý dữ liệu và bước huấn luyện.
Đây là nguyên tắc **Feature Consistency** — train và inference phải đi qua cùng một bộ transform.

---

## Cấu trúc file

```
ml/
├── rf_model.py       ← Entry point — chạy file này
├── train_model.py    ← Module build pipeline & train RF
└── evaluate.py       ← Module tính metrics & in báo cáo
```

---

## Hướng dẫn chạy tay

### Yêu cầu môi trường

| Thành phần | Phiên bản khuyến nghị |
|---|---|
| Python | 3.8+ |
| PySpark | 4.x (`pip install pyspark`) |
| Java (JDK) | 11 hoặc 17 |
| pyarrow | `pip install pyarrow` |

### Bước 1 — Cài đặt thư viện Python

```bash
pip install pyspark pyarrow
```

### Bước 2 — Cài winutils.exe (CHỈ dành cho Windows)

> Bỏ qua bước này nếu bạn đang chạy trên Linux hoặc macOS.

Mở **PowerShell với quyền Admin** và chạy:

```powershell
# Tạo thư mục
New-Item -ItemType Directory -Path "C:\hadoop\bin" -Force

# Tải winutils.exe
Invoke-WebRequest -Uri "https://github.com/cdarlint/winutils/raw/master/hadoop-3.3.5/bin/winutils.exe" `
    -OutFile "C:\hadoop\bin\winutils.exe" -UseBasicParsing

# Tải hadoop.dll
Invoke-WebRequest -Uri "https://github.com/cdarlint/winutils/raw/master/hadoop-3.3.5/bin/hadoop.dll" `
    -OutFile "C:\hadoop\bin\hadoop.dll" -UseBasicParsing
```

> **Ghi chú:** `rf_model.py` đã tự động set `HADOOP_HOME=C:\hadoop` khi phát hiện Windows — không cần set thủ công.

### Bước 3 — Chuẩn bị dữ liệu

**Tùy chọn A** _(Chuẩn benchmark)_: Có đủ 2 file train/test riêng biệt:

```
data/
├── UNSW_NB15_training-set.csv   ← dữ liệu huấn luyện
└── UNSW_NB15_testing-set.csv    ← dữ liệu kiểm thử độc lập
```

**Tùy chọn B** _(Fallback)_: Chỉ có file Parquet đã xử lý (chạy Batch trước):

```bash
# Chạy batch trước để tạo Parquet
python batch/spark_sample.py
```

```
data/processed/
└── UNSW_NB15_cleaned.parquet   ← rf_model.py sẽ split 80/20 tự động
```

### Bước 4 — Chạy ML Pipeline

Chạy từ thư mục gốc dự án (`intrusion-detection-bigdata/`):

```bash
python ml/rf_model.py
```

Hoặc chạy từ bên trong thư mục `ml/`:

```bash
cd ml
python rf_model.py
```

### Thứ tự chạy đầy đủ (từ đầu đến cuối)

```bash
# 1. Batch Processing (tạo Parquet)
python batch/spark_sample.py

# 2. Machine Learning (train + evaluate)
python ml/rf_model.py
```

---

## Kết quả kiểm thử thực tế (2026-04-26)

> Dữ liệu: `UNSW_NB15_testing-set.csv` → sau batch còn **35,179 dòng**  
> Môi trường: Windows local, PySpark 4.1.1, Java 17, Random Forest 50 cây

### Output trên console

```
>>> [1/5] Fallback: doc Parquet va split 80/20
[hdfs_utils] Da doc Parquet: .../data/processed/UNSW_NB15_cleaned.parquet (35179 dong)
>>> [2/5] Preprocessing + Feature Engineering...
>>> [3/5] Build Pipeline (StringIndexer + VectorAssembler)...
         -> Split 80/20 (fallback)...
>>> [4/5] Training Random Forest (numTrees=50)...
         -> Hoan thanh trong 18.01 giay!
>>> [5/5] Danh gia mo hinh...

=======================================================
           MODEL EVALUATION REPORT
=======================================================
  Metric               Train       Test        Gap
  -----------------------------------------------
  Accuracy            98.21%     98.35%     -0.15%
  F1-Score            98.20%     98.35%     -0.15%
-------------------------------------------------------
  Precision (Test) : 98.35%
  Recall    (Test) : 98.35%
  AUC-ROC   (Test) : 99.86%
-------------------------------------------------------
  Overfit Diagnosis:
  [OK]      Gap = -0.15% -> Mo hinh on dinh, khong overfit
-------------------------------------------------------
  Confusion Matrix (Test Set):
+-----+----------+-----+
|label|prediction|count|
+-----+----------+-----+
|    0|       0.0| 1759|   ← True Negative  (Normal đúng)
|    0|       1.0|   82|   ← False Positive (Normal → Attack)
|    1|       0.0|   31|   ← False Negative (Attack bị bỏ sót)
|    1|       1.0| 4996|   ← True Positive  (Attack đúng)
+-----+----------+-----+

  Top 10 Important Features:
     1. sttl                           -> 0.1765
     2. ct_state_ttl                   -> 0.1191
     3. dmean                          -> 0.0779
     4. dttl                           -> 0.0629
     5. byte_ratio     ← (FE mới)      -> 0.0553
     6. dbytes                         -> 0.0469
     7. pkt_ratio      ← (FE mới)      -> 0.0428
     8. total_bytes    ← (FE mới)      -> 0.0396
     9. dload                          -> 0.0337
    10. tcprtt                         -> 0.0328
=======================================================
```

### Tổng hợp kết quả

| Metric | Giá trị |
|---|---|
| **Accuracy (Test)** | **98.35%** |
| **F1-Score (Test)** | **98.35%** |
| **Precision (Test)** | **98.35%** |
| **Recall (Test)** | **98.35%** |
| **AUC-ROC** | **99.86%** |
| Overfit Gap (Accuracy) | **-0.15%** → ✅ Ổn định |
| Thời gian train (50 cây) | ~18 giây |
| Số dòng dữ liệu | 35,179 dòng |
| Số feature đầu vào | 42 features |

### Nhận xét

- **Không overfit**: Gap Train–Test âm (-0.15%) cho thấy model tổng quát tốt.
- **3/10 feature quan trọng nhất** (`byte_ratio`, `pkt_ratio`, `total_bytes`) đều là feature **tự tạo** bởi `feature_engineering.py` — xác nhận thiết kế Feature Engineering có giá trị thực sự.
- **False Negative = 31** dòng: Có 31 cuộc tấn công bị bỏ sót trong 7,868 dòng test (~0.4%).
- **AUC-ROC = 99.86%**: Model phân biệt Normal/Attack gần như hoàn hảo ở mọi ngưỡng phân loại.
