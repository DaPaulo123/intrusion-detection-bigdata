# Phân hệ Batch Processing & Tiền xử lý dữ liệu

Phân hệ `batch` đảm nhận vai trò là bộ lọc tiền tuyến (Front-line filter) cho hệ thống, đảm bảo nguồn dữ liệu khổng lồ sẽ được đưa vào định dạng lưu trữ tối ưu hóa là `Parquet` sau khi đã xóa bỏ triệt để mọi "rác" trong dữ liệu. Quy trình này có thể triển khai chạy Job định kỳ.

---

## Các kỹ thuật Tiền xử lý Dữ liệu đã áp dụng

Trong `spark_sample.py`, bộ dữ liệu UNSW-NB15 đi qua 4 bước xử lý liên tiếp:

### 1. Xử lý giá trị trống (Missing Values)
- **Phương pháp**: `df.dropna()` — loại bỏ toàn bộ dòng có ít nhất 1 trường NULL.
- **Lý do**: Bất kỳ bản ghi nào thiếu thông số sẽ gây lỗi tính toán số học (NaN propagation) trong quá trình huấn luyện ML.

### 2. Xóa cột thừa (Redundant Columns)
- **Cột loại bỏ**: `id`, `attack_cat`
  - `id`: Bộ đếm dòng, không mang thông tin mạng → giữ lại sẽ gây overfit.
  - `attack_cat`: Nhãn đa lớp chi tiết → gây **Data Leakage** khi dự án chỉ thực hiện phân loại nhị phân (cột `label`).

### 3. Lọc nhiễu chuỗi (Denoising)
- **Phương pháp**: Filter loại bỏ giá trị `"-"` và `"unknown"` ở các cột `service`, `state`.
- **Lý do**: Thiết bị mạng ghi nhãn mơ hồ khi không nhận dạng được giao thức/dịch vụ. Giữ lại sẽ làm `StringIndexer` tạo thêm category rác.

### 4. Feature Engineering
Tạo thêm 5 cột đặc trưng mới từ dữ liệu gốc:

| Cột mới | Công thức | Ý nghĩa |
|---|---|---|
| `total_bytes` | `sbytes + dbytes` | Tổng byte trao đổi 2 chiều |
| `byte_ratio` | `sbytes / total_bytes` | Tỷ lệ byte chiều lên |
| `pkt_ratio` | `spkts / (spkts + dpkts)` | Tỷ lệ gói tin chiều lên |
| `log_duration` | `log1p(dur)` | Log hóa thời gian (xử lý phân phối lệch) |
| `is_bidirectional` | `1` nếu `sbytes>0 AND dbytes>0` | Kết nối hai chiều hay không |

---

## Cấu trúc file

```
batch/
├── spark_sample.py       ← Entry point — chạy file này
├── preprocessing.py      ← Module làm sạch dữ liệu (dùng chung với ml/)
├── feature_engineering.py← Module tạo feature mới (dùng chung với ml/)
└── hdfs_utils.py         ← Tiện ích đọc/ghi CSV & Parquet
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

PySpark trên Windows cần `winutils.exe` và `hadoop.dll` để đọc/ghi file.  
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

> **Ghi chú:** Script `spark_sample.py` đã tự động set `HADOOP_HOME=C:\hadoop`
> khi phát hiện chạy trên Windows — **không cần** set biến môi trường thủ công.

### Bước 3 — Chuẩn bị dữ liệu đầu vào

Đảm bảo file CSV tồn tại tại đường dẫn:

```
intrusion-detection-bigdata/
└── data/
    └── UNSW_NB15_testing-set.csv   ← file này phải có (~15 MB)
```

### Bước 4 — Chạy Batch Pipeline

Chạy từ thư mục gốc dự án (`intrusion-detection-bigdata/`):

```bash
python batch/spark_sample.py
```

Hoặc chạy từ bên trong thư mục `batch/`:

```bash
cd batch
python spark_sample.py
```

---

## Kết quả kiểm thử thực tế (2026-04-26)

> Dữ liệu: `UNSW_NB15_testing-set.csv` — môi trường: Windows local, PySpark 4.1.1

### Output trên console

```
--- [1/4] Doc du lieu UNSW-NB15 ---
[hdfs_utils] Da doc CSV: .../data/UNSW_NB15_testing-set.csv (82332 dong)
Tong so dong (tho): 82332

--- [2/4] Kham pha du lieu ---
Cac cot trong dataset: (45 cot)
  - id, dur, proto, service, state, spkts, dpkts,
    sbytes, dbytes, rate, sttl, dttl, sload, dload,
    sloss, dloss, sinpkt, dinpkt, sjit, djit, swin,
    stcpb, dtcpb, dwin, tcprtt, synack, ackdat,
    smean, dmean, trans_depth, response_body_len,
    ct_srv_src, ct_state_ttl, ct_dst_ltm, ct_src_dport_ltm,
    ct_dst_sport_ltm, ct_dst_src_ltm, is_ftp_login,
    ct_ftp_cmd, ct_flw_http_mthd, ct_src_ltm,
    ct_srv_dst, is_sm_ips_ports, attack_cat, label

--- [3/4] Lam sach du lieu (preprocessing) ---

--- [4/4] Feature Engineering ---
Tong so dong sau xu ly : 35179
So dong da xoa         : 47153
Cac cot moi them       : total_bytes, byte_ratio, pkt_ratio, log_duration, is_bidirectional

--- Luu Parquet -> .../data/processed/UNSW_NB15_cleaned.parquet ---
[hdfs_utils] Da luu Parquet thanh cong: .../data/processed/UNSW_NB15_cleaned.parquet
```

### Thống kê kết quả

| Chỉ số | Giá trị |
|---|---|
| Tổng dòng thô (CSV đầu vào) | **82,332 dòng** |
| Dòng sau khi làm sạch | **35,179 dòng** |
| Dòng bị loại bỏ | 47,153 dòng (service=`-` hoặc null/unknown) |
| Số cột gốc | 45 cột |
| Số cột sau xử lý | 47 cột (thêm 5, bỏ 3: `id`, `attack_cat`, cột gốc categorical) |
| File output | `data/processed/UNSW_NB15_cleaned.parquet` ✅ |

---

## Lưu ý khi tích hợp với ML (Phần 4)

File Parquet được tạo ra ở bước này là **đầu vào** của `ml/rf_model.py`.  
Nếu chưa có file `UNSW_NB15_training-set.csv`, `rf_model.py` sẽ tự động đọc Parquet này và split 80/20 để train + test.  
Xem chi tiết tại [`ml/README.md`](../ml/README.md).