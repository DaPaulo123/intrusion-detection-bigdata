import os
import json
from config.settings import logger

def get_model_metrics():
    """
    Đọc trực tiếp các chỉ số ML thực tế từ file kết quả đánh giá mô hình.
    """
    # Đường dẫn tới file metrics
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    metrics_path = os.path.join(base_dir, "models", "model_metrics.json")
    
    # Giá trị mặc định phòng trường hợp file không tồn tại
    default_metrics = {
        "accuracy": 0.6214,
        "f1_score": 0.6887,
        "precision": 0.6545,
        "recall": 0.6214,
        "stage1_trees": 50,
        "stage2_trees": 100,
        "last_updated": "2026-06-03T18:00:00Z",
        "is_simulated": True
    }
    
    if not os.path.exists(metrics_path):
        logger.warning(f"Không tìm thấy file metrics tại {metrics_path}. Sử dụng metrics mặc định.")
        return default_metrics
        
    try:
        with open(metrics_path, "r", encoding="utf-8") as f:
            metrics = json.load(f)
            metrics["is_simulated"] = False
            logger.info("Đã tải thành công các chỉ số đánh giá mô hình từ file JSON.")
            return metrics
    except Exception as e:
        logger.error(f"Lỗi khi đọc file metrics: {e}")
        return default_metrics
