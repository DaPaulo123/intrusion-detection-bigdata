# Sử dụng image Python slim làm base để tối ưu dung lượng
FROM python:3.9-slim

WORKDIR /app

# Copy file requirements từ root của project
COPY requirements.txt .

# Cài đặt các thư viện cần thiết, bao gồm cả các gói phục vụ SocketIO và Cache
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir flask-socketio flask-caching redis

# Copy mã nguồn API Serving và file metrics của mô hình ML
COPY serving/backend ./backend
COPY models/model_metrics.json ./models/

# Thiết lập thư mục làm việc và đường dẫn python
ENV PYTHONPATH=/app/backend
ENV MONGO_URI=mongodb://mongodb:27017/
ENV REDIS_URL=redis://redis:6379/0

EXPOSE 5000

# Khởi chạy server
CMD ["python", "backend/app.py"]
