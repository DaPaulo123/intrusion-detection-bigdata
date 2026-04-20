# Data Dictionary - Intrusion Detection System (IDS)

Tài liệu này mô tả các trường dữ liệu (features) được sử dụng trong quá trình huấn luyện mô hình Machine Learning và xử lý luồng dữ liệu thực tế (Real-time Stream).

### 1. Thông tin chung
- **Dataset gốc:** UNSW-NB15
- **Mục tiêu:** Phân loại lưu lượng mạng là **Bình thường (0)** hoặc **Tấn công (1)**.

### 2. Các trường dữ liệu chính (Selected Features)
Dưới đây là các cột quan trọng nhất đã được trích xuất và xử lý trong `task3.py` và `task4.py`:

| Tên cột | Ý nghĩa | Kiểu dữ liệu | Ghi chú |
| :--- | :--- | :--- | :--- |
| **srcip** | Địa chỉ IP nguồn | String | Dùng để định danh máy gửi gói tin |
| **dstip** | Địa chỉ IP đích | String | Máy nhận gói tin |
| **proto** | Giao thức mạng | Categorical | Ví dụ: tcp, udp, icmp, ospf (có 134 loại) |
| **service** | Dịch vụ ứng dụng | Categorical | Ví dụ: http, ftp, smtp, ssh |
| **state** | Trạng thái kết nối | Categorical | Ví dụ: FIN, INT, CON |
| **sbytes** | Số byte gửi từ nguồn | Integer | Đặc trưng quan trọng để nhận diện DDoS |
| **dbytes** | Số byte gửi từ đích | Integer | |
| **dur** | Thời gian kết nối | Float | Tổng thời gian diễn ra record |
| **label** | **Nhãn phân loại** | Binary | 0: Normal, 1: Attack |

### 3. Quy trình xử lý dữ liệu (Data Pipeline)
1. **String Indexing:** Chuyển đổi các cột `proto`, `service`, `state` từ dạng chữ sang mã số để Spark MLlib có thể tính toán.
2. **Vector Assembly:** Gom tất cả các cột đặc trưng vào một vector duy nhất (`features`) trước khi đưa vào mô hình Random Forest.