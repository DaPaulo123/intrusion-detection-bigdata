# Kế Hoạch Tái Cấu Trúc & Phát Triển Backend Serving

## Mục Tiêu
Nâng cấp thư mục `serving` từ một file `app.py` nguyên khối thành kiến trúc MVC/Modular chuyên nghiệp. Bổ sung các API và **tích hợp công nghệ Real-time (WebSockets)** để phục vụ Dashboard SOC.

---

## Bước 1: Tái Cấu Trúc Mã Nguồn (Refactoring) & Chuẩn hóa
- [ ] **Tạo file `serving/api/config.py` (Bổ sung):**
  - Tập trung quản lý toàn bộ cấu hình (Biến môi trường, URL DB) tại một nơi duy nhất thay vì dùng `os.environ` rải rác.
- [ ] **Thiết lập Logging chuyên nghiệp (Bổ sung):** 
  - Loại bỏ hoàn toàn các lệnh `print()` thô sơ, thay bằng hệ thống `logging` chuẩn để lưu log lỗi ra file `.log`.
- [ ] **Tạo file `serving/api/database.py`:**
  - Chuyển logic kết nối MongoDB sang file này. Viết hàm `get_db()`.
- [ ] **Hoàn thiện file `serving/api/routes.py`:**
  - Chuyển tất cả các định nghĩa API (`@app.route`) từ `app.py` sang.
  - Chuẩn hóa format trả về (Base Response): `{"status": "success", "data": ..., "message": ...}`.
- [ ] **Dọn dẹp `serving/api/app.py`:**
  - Chỉ còn nhiệm vụ: Khởi tạo `Flask`, cấu hình `CORS` (cho cả REST và WebSockets), đăng ký `routes` và `app.run()`.

---

## Bước 2: Xây Dựng Các Mô-đun Tiện Ích (Utils) & Mock Data
- [ ] **Tạo file `serving/api/docker_utils.py`:** Dùng thư viện `subprocess` bóc tách kết quả `docker ps` để lấy danh sách container.
- [ ] **Tạo file `serving/api/model_utils.py`:** Hàm đọc thông số Accuracy, F1-Score của mô hình.
- [ ] **Tạo file `serving/scripts/seed_mock_data.py`:** Viết kịch bản tự động sinh dữ liệu giả (Mock Data) phục vụ test UI.
  - **API Cần Dữ Liệu Giả:**
    - `GET /alerts`: Cần list cảnh báo (IP nguồn, IP đích, loại tấn công, thời gian).
    - `GET /alerts/summary`: Cần thống kê số lượng DoS, Worm... để vẽ biểu đồ tròn và số vụ trong 10 phút.
    - `GET /batch/stats`: Cần thống kê giờ cao điểm và phân bố Threat Score để vẽ biểu đồ đường/cột.
  - **API KHÔNG Cần Dữ Liệu Giả (Chạy động thực tế):**
    - `GET /health`: Trạng thái sống/chết của Flask.
    - `GET /system/health`: Quét trực tiếp các container Docker thật qua lệnh `docker ps`.
    - `GET /system/model-metrics`: Đọc trực tiếp các chỉ số ML thực tế từ file kết quả đánh giá mô hình.

---

## Bước 3: Lập Trình 5 Đầu API (RESTful)
- [ ] **`PUT /alerts/<id>/status`:** Cập nhật trạng thái xử lý (vd: `pending` -> `handled`).
- [ ] **`GET /alerts/summary`:** Lấy số lượng theo `attack_cat` và đếm số đợt 10 phút qua (Dùng Aggregation).
- [ ] **`GET /batch/stats`:** Truy vấn kết quả luồng Batch để lấy giờ cao điểm.
- [ ] **`GET /system/health`:** Trả JSON danh sách dịch vụ Docker đang chạy/lỗi.
- [ ] **`GET /system/model-metrics`:** Trả về độ chính xác của mô hình mạng.

---

## Bước 4: (Bổ sung Quan Trọng) Tích hợp Real-time WebSockets
*Giải quyết bài toán: Frontend liên tục hỏi API (Polling) 5s/lần sẽ làm tắc nghẽn server và không đủ "nhanh" cho một hệ thống chống xâm nhập.*
- [ ] Cài đặt thư viện `flask-socketio`.
- [ ] Khởi tạo WebSocket Server trong `app.py`.
- [ ] Xây dựng luồng Đẩy dữ liệu (Push): Mỗi khi Streaming ML phát hiện tấn công và Insert vào MongoDB, Backend lập tức chủ động Bắn (Emit) cảnh báo thẳng về màn hình Frontend (độ trễ < 0.1s).

---

## Bước 5: Tích hợp công nghệ Enterprise (Bảo mật & Hiệu năng)
*Nếu làm đồ án bình thường thì có thể bỏ qua, nhưng để đạt chuẩn kỹ sư cấp cao (Senior/Enterprise), hệ thống cần bổ sung các lớp giáp sau:*
- [ ] **Bảo mật (JWT / API Key):** Khóa các API lại. Không thể để ai cũng gọi được lệnh `PUT /status` để phá hoại dữ liệu hệ thống. Cần lưu lại thông tin `resolved_by` (Ai là người đã xử lý cảnh báo này).
- [ ] **Xác thực dữ liệu (Validation):** Ngăn chặn Frontend truyền các dữ liệu rác (Ví dụ truyền trạng thái là `đã_xóa_sạch` thay vì `handled`).
- [ ] **Tận dụng Redis (Caching):** Mình phát hiện trong file `docker-compose.yml` của bạn **đã có sẵn container Redis**. Chúng ta tuyệt đối phải tận dụng nó! Sẽ cài thư viện `flask-caching` để lưu tạm các dữ liệu nặng (như `GET /batch/stats`), giúp tốc độ trả API giảm xuống chỉ còn 1 mili-giây.
- [ ] **Tài liệu API (Swagger UI):** Tích hợp thư viện sinh tài liệu tự động (`flasgger`), tạo ra đường link `/docs` để bất kỳ ai vào cũng biết cách gọi API của bạn.

---

## Bước 6: Container Hóa & Tối Ưu Hệ Thống Big Data (Bổ sung mới)
*Để đảm bảo hệ thống có thể vận hành ổn định trong môi trường Big Data thực tế:*
- [ ] **Tạo `Dockerfile` cho Serving API:** Tạo file cấu hình để đóng gói Flask API thành container. Điều này giúp tích hợp API trực tiếp vào `docker-compose.yml` chạy chung với Kafka/Spark, và sẵn sàng deploy lên Kubernetes (khi bạn đã có sẵn thư mục `serving/kubernetes`).
- [ ] **Đánh chỉ mục MongoDB (Database Indexing):** 
  - Do truy vấn `/alerts` liên tục sắp xếp giảm dần theo thời gian (`timestamp`), nếu dữ liệu tăng lên hàng triệu dòng sẽ gây nghẽn cổ chai.
  - Cần thêm lệnh cấu hình tạo **Index** cho trường `timestamp` và `status` khi khởi động cơ sở dữ liệu.
- [ ] **Graceful Shutdown:** Viết hàm bắt sự kiện tắt ứng dụng (SIGINT/SIGTERM) để giải phóng các kết nối MongoDB và WebSockets một cách sạch sẽ, tránh hiện tượng rò rỉ bộ nhớ (memory leak).

---

## Bước 7: Cầu Nối Giữa Streaming (Spark) & MongoDB (Tạm hoãn - Làm sau khi xong UI)
*Ghi chú kiến trúc để nhớ cách triển khai sau này khi làm luồng thật:*
- [ ] **Cách thức kết nối:** Khi tiến hành kết nối thật, ta sẽ vào file `streaming/stream_processor.py`, thay thế đoạn `.format("console")` bằng hàm ghi luồng của PySpark.
- [ ] **Hàm ghi dữ liệu:** Sử dụng hàm `.writeStream.foreachBatch(write_to_mongo)` trong PySpark. Trong hàm `write_to_mongo(df, epoch_id)`, ta dùng thư viện `pymongo` kết nối trực tiếp với MongoDB URI và gọi `insert_many` cho các dòng dữ liệu được dự đoán là tấn công (`Label = 1`).
- [ ] **Đồng bộ hóa Schema:** Đảm bảo các trường dữ liệu do Spark đẩy vào MongoDB (`srcip`, `dstip`, `attack_cat`, `timestamp`) khớp hoàn toàn với cấu hình mà Backend API sẽ đọc để vẽ giao diện.

---

## Bước 8: Khởi Tạo Môi Trường Frontend
- [ ] Thoát ra thư mục gốc (`intrusion-detection-bigdata`).
- [ ] Chạy `npm create vite@latest frontend` để sang chặng tiếp theo.theo.
