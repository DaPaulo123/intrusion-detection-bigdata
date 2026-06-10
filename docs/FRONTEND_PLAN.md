# Kế Hoạch Triển Khai Frontend Dashboard (SOC - Security Operations Center)

Đánh giá tổng quan: Ý tưởng 3 màn hình của bạn là chuẩn mực của một hệ thống SOC (Security Operations Center). Nó bao trọn từ Real-time, Batch đến DevOps/MLOps.

---

## 1. Danh Sách Các Đầu Giao Tiếp (API & Sockets)
1. **`GET /alerts` (REST)**
2. **`PUT /alerts/<id>/status` (REST)**
3. **`GET /alerts/summary` (REST)**
4. **`GET /batch/stats` (REST)**
5. **`GET /system/health` (REST)**
6. **`GET /system/model-metrics` (REST)**
7. **(Bổ sung Quan Trọng) Kênh WebSockets (`/alerts/stream`):** Thay vì dùng REST lấy dữ liệu nhiều lần, luồng Streaming sẽ mở một đường ống Socket trực tiếp để Backend "nhồi" dữ liệu thẳng lên màn hình ngay khi có xâm nhập.

---

## 2. Thiết Kế 3 Module & Áp Dụng Công Nghệ

### Module 1: Streaming Dashboard (Giám sát Real-time)
- **Giao diện:** Thẻ đếm tấn công 10p, Biểu đồ Pie Chart phân loại, Bảng cảnh báo có nút **[Xác nhận đã xử lý]**.
- **(Nâng cấp) Công nghệ gọi dữ liệu:** 
  - Bỏ cơ chế Polling (gọi 5s/lần). Chuyển sang lắng nghe **WebSockets (`socket.io-client`)**.
  - **Trải nghiệm người dùng (UX):** Khi có tấn công, hàng dữ liệu mới sẽ tự động trượt lên đầu bảng (Smooth Animation). Có thêm hệ thống Pop-up (Toast) báo động đỏ ở góc màn hình.
- **Tương tác:** Ấn nút xử lý sẽ gọi `PUT /alerts/<id>/status`.

### Module 2: Batch Analytics Dashboard (Phân tích chuyên sâu)
- **Giao diện:** Biểu đồ đường (Giờ cao điểm) và Biểu đồ cột (Threat Score).
- **Công nghệ:** Dùng `GET /batch/stats`. (Bổ sung: Dữ liệu này sẽ được lưu tạm vào State cục bộ của trình duyệt để không phải gọi lại API nếu người dùng bấm chuyển qua lại giữa các Tab).

### Module 3: System & Model Overview (Kiểm soát "Sức Khỏe")
- **Giao diện:** Bảng trạng thái Xanh/Đỏ của Node Docker. Thẻ điểm Accuracy. Text báo cáo tự động.
- **Công nghệ:** Dùng `GET /system/health` và `GET /system/model-metrics`. 

---

## 3. Kiến Trúc & Tech Stack Chi Tiết (Hoàn Hảo Hơn)

Để làm được một ứng dụng Web hạng nặng (Single Page Application) mà không bị giật lag khi dữ liệu đổ về liên tục, chúng ta phải bổ sung các "vũ khí" sau:
- **Core:** `ReactJS` + `Vite` (Khởi động siêu nhanh).
- **Routing (Mới):** `React Router DOM`. Quản lý đường dẫn ảo (vd: `/streaming`, `/batch`, `/system`), giúp chuyển Tab mượt mà không tải lại trang.
- **State Management (Mới):** `Zustand`. Giúp quản lý danh sách cảnh báo Real-time tập trung ở một nơi, các Component khác (Bảng, Biểu đồ, Số liệu) đều tự động cập nhật đồng bộ mà không cần truyền dữ liệu rườm rà.
- **Real-time (Mới):** `socket.io-client` (Để hứng luồng dữ liệu WebSockets).
- **Charts:** `Recharts` (Đẹp, mượt, dễ phối màu Dark Mode).
- **Styling:** `Vanilla CSS` + CSS Variables (Chủ đạo: Glassmorphism nền tối, chữ Neon).
- **Thông báo (Mới):** `react-hot-toast` (Tạo pop-up cảnh báo nguy hiểm siêu mượt).
