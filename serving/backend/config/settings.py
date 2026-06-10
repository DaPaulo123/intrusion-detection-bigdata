import os
import logging
from dotenv import load_dotenv

load_dotenv()

class Config:
    MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/")
    DB_NAME = "intrusion_detection"
    ALERTS_COLLECTION = "alerts"
    BATCH_STATS_COLLECTION = "batch_stats"
    REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
    SECRET_KEY = os.environ.get("SECRET_KEY", "soc_super_secret_session_key_2026")
    API_KEY = os.environ.get("API_KEY", "SOC-Super-Secret-2026")
    HOST = "0.0.0.0"
    PORT = 5000
    DEBUG = True

log_file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "serving_app.log")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(log_file_path, encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("serving_logger")
