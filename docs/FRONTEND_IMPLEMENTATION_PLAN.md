# Kế Hoạch Triển Khai Chi Tiết - Frontend SOC Dashboard

Tài liệu này đóng vai trò là checklist công việc (Task Tracker) để xây dựng lớp Frontend cho hệ thống Phát hiện xâm nhập mạng thời gian thực.
Tiến độ hiện tại: Đã cài đặt xong nền móng React (Create React App) và các thư viện cần thiết. Giao diện (UI) đang ở mức 0%.

---

## Giai đoạn 1: Nền Móng Dữ Liệu & Trạng Thái (Services & State Management)
*Mục tiêu: Thiết lập kênh giao tiếp với Backend (REST & WebSockets) và tạo kho dữ liệu dùng chung.*

- [ ] **1.1. Cấu hình Axios (`src/services/api.js`)**
  - Khởi tạo instance Axios với `baseURL` trỏ về API của Backend.
  - Viết sẵn các hàm gọi API: `fetchAlerts()`, `updateAlertStatus()`, `fetchBatchStats()`, `fetchSystemHealth()`.
- [ ] **1.2. Khởi tạo Socket.IO (`src/services/socket.js`)**
  - Khởi tạo kết nối client Socket.IO.
  - Định nghĩa các event listener (vd: `onNewAlert`).
- [ ] **1.3. Kho dữ liệu Cảnh báo (`src/store/useAlertStore.js`)**
  - Dùng `Zustand` tạo store lưu danh sách alerts hiện tại.
  - Viết action (hàm) để thêm alert mới vào đầu danh sách (dùng cho realtime).
- [ ] **1.4. Kho dữ liệu Hệ thống (`src/store/useSystemStore.js`)**
  - Lưu trạng thái các service Docker và chỉ số Model Accuracy.

---

## Giai đoạn 2: Khung Giao Diện & Phong Cách (Layout & Theming)
*Mục tiêu: Thiết lập tông màu Dark Mode / Cyber Security và khung xương của ứng dụng.*

- [ ] **2.1. Cấu hình CSS Toàn cầu (`src/index.css`)**
  - Định nghĩa các biến CSS (CSS Variables) cho màu sắc: nền tối (dark background), màu phản quang (neon blue/red), hiệu ứng kính (glassmorphism).
- [ ] **2.2. Thanh Điều Hướng (`src/components/Sidebar.jsx`)**
  - Các nút bấm chuyển trang: Streaming, Batch, System.
- [ ] **2.3. Thanh Trạng Thái (`src/components/Header.jsx`)**
  - Hiển thị logo dự án, giờ hệ thống, và icon nhấp nháy báo trạng thái kết nối WebSockets (Xanh/Đỏ).
- [ ] **2.4. Bố Cục Chính (`src/components/Layout.jsx`)**
  - Gói Sidebar và Header, để lại vùng `Outlet` ở giữa để chứa nội dung các trang.

---

## Giai đoạn 3: Phân Hệ 1 - Streaming Dashboard (Trang Chủ)
*Mục tiêu: Xây dựng màn hình quan trọng nhất, dữ liệu nhảy liên tục thời gian thực.*

- [ ] **3.1. Thẻ Thống Kê (`src/components/MetricCard.jsx`)**
  - Component hiển thị con số tổng quan (vd: Tổng cảnh báo, Số lượng Critical).
- [ ] **3.2. Biểu Đồ Thời Gian Thực (`src/components/charts/PieChartAlerts.jsx`)**
  - Sử dụng `recharts` vẽ biểu đồ phân bổ các loại tấn công. Tự động render lại mượt mà khi có data mới.
- [ ] **3.3. Bảng Cảnh Báo (`src/components/AlertTable.jsx`)**
  - Hiển thị danh sách các gói tin tấn công.
  - Có nút [Xác nhận Xử lý], bấm vào sẽ gọi `api.js` để đổi trạng thái trên MongoDB.
- [ ] **3.4. Ráp màn hình (`src/pages/Dashboard.jsx`)**
  - Tích hợp tất cả các components trên.
  - Tích hợp thư viện `react-hot-toast` để hiện Pop-up đỏ rực mỗi khi có luồng tấn công đổ về.

---

## Giai đoạn 4: Phân Hệ 2 & 3 - Phân Tích & Giám Sát Hệ Thống
*Mục tiêu: Xây dựng 2 màn hình quản trị và kiểm soát chất lượng luồng dữ liệu.*

- [ ] **4.1. Màn Hình Batch Analytics (`src/pages/BatchAnalytics.jsx`)**
  - Gọi API lấy dữ liệu luồng Batch, vẽ biểu đồ Đường (Line chart) xem xu hướng giờ cao điểm.
- [ ] **4.2. Màn Hình Sức Khỏe Hệ Thống (`src/pages/SystemHealth.jsx`)**
  - Trình bày dạng bảng/lưới trạng thái các Container (Up/Down).
  - Hiển thị thẻ điểm chất lượng Model (Accuracy, F1-Score).
- [ ] **4.3. Cấu hình Routing (`src/App.js`)**
  - Sử dụng `react-router-dom` bọc ứng dụng trong `BrowserRouter`.
  - Khai báo các Routes: `/` (Dashboard), `/batch` (BatchAnalytics), `/system` (SystemHealth).

---

## Giai đoạn 5: Tích hợp Toàn Diện & Đánh Bóng (Integration & Polish)
*Mục tiêu: Kiểm thử end-to-end đảm bảo hoạt động không lỗi và mượt mà.*

- [ ] **5.1. Kết nối với Backend (Mock Data)**
  - Chạy `app.py` Backend cùng với script giả lập luồng. Đảm bảo UI hứng dữ liệu chuẩn.
- [ ] **5.2. Tối ưu Hiệu năng (Performance)**
  - Đảm bảo khi có 10 cảnh báo/giây, màn hình không bị giật lag (sức mạnh của Zustand).
- [ ] **5.3. Tinh chỉnh CSS (Micro-animations)**
  - Hiệu ứng hover, hiệu ứng trượt lên (slide up) khi dòng dữ liệu mới xuất hiện ở Bảng.
