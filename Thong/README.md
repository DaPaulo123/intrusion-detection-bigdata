# Setup Kafka & Test Ingestion

## Yêu cầu môi trường
- Java 8 hoặc 11 (Đã set biến `JAVA_HOME`)
- Apache Kafka (Phiên bản có hỗ trợ Zookeeper, vd: 3.7.x)

## Các bước khởi động
**Lưu ý:** Chạy các lệnh sau trong thư mục gốc của Kafka (trên Windows dùng CMD/PowerShell):

1. **Khởi động Zookeeper:**
   `.\bin\windows\zookeeper-server-start.bat .\config\zookeeper.properties`

2. **Khởi động Kafka Server:**
   `.\bin\windows\kafka-server-start.bat .\config\server.properties`
   *(Nếu lỗi WMIC, set cứng biến môi trường: `set KAFKA_HEAP_OPTS=-Xmx1G -Xms1G` trước khi chạy lệnh).*

3. **Tạo Topic:**
   `.\bin\windows\kafka-topics.bat --create --topic network-traffic --bootstrap-server localhost:9092`

## Test luồng dữ liệu (Ingestion Test)
- Đã khởi chạy thành công `kafka-console-producer` và `kafka-console-consumer`.
- Đã gửi thành công 5 mẫu JSON packet giả lập dữ liệu mạng:
  `{"srcip": "192.168.1.1", "dstip": "10.0.0.1", "proto": "tcp", "label": 0}` (x5 mẫu)

# Báo cáo thực hiện Tasks - Ngô Đức Anh Thông

###  Kiến thức tích lũy được:
- **Kafka:** Cách thiết lập Pipeline truyền tin Real-time và xử lý lỗi kết nối Producer/Consumer.
- **Spark Streaming:** Kỹ thuật parsing dữ liệu JSON thô từ Kafka Topic thành Structured Data.
- **Machine Learning (Big Data):** Sự khác biệt giữa Sklearn (Single Machine) và PySpark MLlib (Distributed Computing). Cách xử lý lỗi `maxBins` khi dữ liệu có quá nhiều phân loại.
- **DevOps cơ bản:** Cách quản lý Database (MongoDB) qua Docker và xử lý lỗi môi trường WSL trên Windows.
