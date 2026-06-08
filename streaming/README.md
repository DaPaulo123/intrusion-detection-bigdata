# Phần 3: Thử chạy mẫu biểu diễn Streaming Layer (Kafka Consumer)

Trong luồng xử lý Big Data thời gian thực, **Streaming Layer** giữ vai trò đón đầu các báo cáo/log mạng được đẩy vào Message Broker (Kafka) và bóc tách dữ liệu ngay lập tức. Thay vì lưu vào Database chờ phân tích ở cuối ngày (Batch processing), kiến trúc Streaming sẽ quét và phân tích nó liên tục (Real-time).

## 1. Cách chạy thử nghiệm Layer Streaming
Script `kafka_streaming_layer.py` trong thư mục này được viết đóng vai trò là một Consumer. 

Nó kết nối trực tiếp vào Cluster Kafka ở port `9092` và liên tục lắng nghe (subscribe) dữ liệu từ topic `test-topic`. Mọi bản tin (packet) được đẩy vào từ Script `kafka_producer.py` sẽ lọt thẳng vào đây trên Terminal.

**Lệnh khởi chạy Streaming:**
```bash
cd streaming
python kafka_streaming_layer.py
```

## 2. Kết quả thu được (Chụp màn hình Output Log)

Khi khởi chạy, chương trình bắt toàn bộ 5 gói tin mô phỏng Cảnh báo Xâm nhập (Intrusion Attempt) và parse dữ liệu JSON thô thành bảng cấu trúc. 

Phía dưới là kết quả nguyên bản của máy tính (Đóng vai trò làm "ảnh chụp màn hình" minh họa):

```powershell
PS C:\Users\admin\Desktop\bigdata\intrusion-detection-bigdata\streaming> python kafka_streaming_layer.py
>>> Starting Streaming Layer (Real-time Kafka Consumer)...
>>> Configuring connection to Kafka (localhost:9092), topic = 'test-topic'...

---------------------------------------------------------------------------------
>>> Ready to receive Streaming Layer (Real-time Data) from Kafka:
---------------------------------------------------------------------------------
| ID    | METRIC EVENT              | SEVERITY   | SOURCE_IP       | TIMESTAMP       |
---------------------------------------------------------------------------------
| 1     | intrusion_attempt         | high       | 192.168.1.11    | 1775965195      |
| 2     | intrusion_attempt         | high       | 192.168.1.12    | 1775965196      |
| 3     | intrusion_attempt         | high       | 192.168.1.13    | 1775965197      |
| 4     | intrusion_attempt         | high       | 192.168.1.14    | 1775965198      |
| 5     | intrusion_attempt         | high       | 192.168.1.15    | 1775965199      |
---------------------------------------------------------------------------------
>>> Finished reading Streaming Layer data! Safely disconnected.
```

**Mục đích ứng dụng cho phân đoạn Cảnh báo Xâm nhập:**
Nhờ việc bắt luồng tức thì này, ở đồ án hoàn chỉnh, ta sẽ đưa các thông số `192.168.1.11` đi xuyên qua Model Học máy (Machine Learning) để có hình thức cảnh báo (thậm chí chặn truy cập) tới IP đó trước khi kẻ tấn công kịp gây thiệt hại.
