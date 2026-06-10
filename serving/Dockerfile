# Sử dụng image Python slim làm base để tối ưu dung lượng
FROM python:3.9-slim

WORKDIR /app

# Copy file requirements từ root của project
COPY requirements.txt .

# Cài đặt các thư viện cần thiết, bao gồm cả các gói phục vụ SocketIO, Cache và ML
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir flask-socketio flask-caching redis xgboost numpy

# Copy mã nguồn API Serving và toàn bộ model artifacts
COPY serving/backend ./backend
COPY models/ ./models/

# Thiết lập thư mục làm việc và đường dẫn python
ENV PYTHONPATH=/app/backend
ENV MODEL_DIR=/app/models
ENV MONGO_URI=mongodb://mongodb:27017/
ENV REDIS_URL=redis://redis:6379/0

EXPOSE 5000

# Khởi chạy server
CMD ["python", "backend/app.py"]
