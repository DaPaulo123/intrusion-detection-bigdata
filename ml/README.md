# Phần 4: Huấn luyện Mô hình Học Máy Thực tiễn (Machine Learning)

Trong kiến trúc Network Intrusion Detection System (IDS), **Phân hệ Học Máy** đóng vai trò là "Bộ não". Nó dùng tri thức đã học để có thể phân định ranh giới giữa một gói tin Bình thường (Normal) và một gói tin có dấu hiệu Tấn công (Attack).

## 1. Setup Data và Thư viện
Phần này ứng dụng các thư viện phổ biến xử lý dữ liệu lớn: `pandas` để nạp tập dataset **UNSW-NB15** và thư viện `scikit-learn` để xây dựng mô hình. Các gói này thiết lập trong thư mục gốc `requirements.txt`.

## 2. Thuật toán `rf_model.py`
Script mô phỏng một luồng tạo sinh AI bao gồm:
- **Nạp Dữ liệu**: Load toàn bộ file đánh giá `UNSW_NB15_testing-set.csv` (với 175,341 bản ghi).
- **Tiền xử lý (Preprocessing)**: Loại bỏ ID và Label phụ. Tự động mã hóa (Label Encoding) các trường dữ liệu chuỗi (như Giao thức TCP/UDP, Tên Dịch vụ HTTP/SSH, Trạng thái) về dạng ma trận số.
- **Chia tập (Splitting)**: Chia 80% Data cho huấn luyện (Training), 20% Data cho làm bài kiểm tra (Testing/Evaluation).
- **Training**: Đưa dữ liệu qua một "Khu rừng ngẫu nhiên" - Thuật toán **Random Forest Classifier** (`n_estimators=50`).

## 3. Mở chạy Mô hình trên máy tính
```bash
cd ml
python rf_model.py
```

## 4. Kết quả Phân tích (Log Output Capture)
Dưới đây là một ảnh chụp minh họa Terminal trong ca thử nghiệm, phô diễn sức mạnh phân loại của mô hình trên tập dữ liệu UNSW-NB15:

![Random Forest ML Execution Output](../docs/images/ml_randomforest_results.png)
