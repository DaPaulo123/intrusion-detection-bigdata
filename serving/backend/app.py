import os
import sys
import signal
import threading
import time
from flask import Flask
from flask_cors import CORS
from bson import ObjectId

from config.settings import Config, logger
from core.database import close_db
from core.extensions import cache, socketio
from routes.alert_routes import alert_bp
from routes.system_routes import system_bp
from routes.batch_routes import batch_bp
from routes.docs_routes import docs_bp
from routes.predict_routes import predict_bp
from routes.ingest_routes import ingest_bp

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = Config.SECRET_KEY

    # CORS
    CORS(app, resources={r"/*": {"origins": "*"}})
    
    # Khởi tạo Extensions
    try:
        import redis
        r = redis.Redis.from_url(Config.REDIS_URL, socket_connect_timeout=2)
        r.ping()
        logger.info("Kết nối tới Redis thành công! Kích hoạt Redis Cache.")
        cache.init_app(app, config={'CACHE_TYPE': 'RedisCache', 'CACHE_REDIS_URL': Config.REDIS_URL, 'CACHE_DEFAULT_TIMEOUT': 60})
    except Exception as re:
        logger.warning(f"Không thể kết nối tới Redis ({re}). Sử dụng SimpleCache.")
        cache.init_app(app, config={'CACHE_TYPE': 'SimpleCache', 'CACHE_DEFAULT_TIMEOUT': 60})
        
    socketio.init_app(app)

    # Đăng ký Blueprints
    app.register_blueprint(alert_bp, url_prefix="/api")
    app.register_blueprint(system_bp, url_prefix="/api")
    app.register_blueprint(batch_bp, url_prefix="/api")
    app.register_blueprint(docs_bp, url_prefix="/api")
    app.register_blueprint(predict_bp, url_prefix="/api")
    app.register_blueprint(ingest_bp, url_prefix="/api")
    
    return app

app = create_app()

last_seen_id = None
stop_event = threading.Event()

def monitor_mongodb_inserts():
    """
    Tiến trình nền giám sát MongoDB — chỉ phát WebSocket cho các alert
    được ghi trực tiếp vào MongoDB (không thông qua API predict/ingest).
    Các alert từ API predict/ingest đã tự emit WebSocket rồi nên bỏ qua.
    """
    global last_seen_id
    from core.database import collection
    
    logger.info("Bắt đầu tiến trình nền giám sát MongoDB cảnh báo mới...")
    try:
        if collection is not None:
            latest_doc = collection.find_one(sort=[("_id", -1)])
            if latest_doc:
                last_seen_id = latest_doc["_id"]
                logger.info(f"WebSocket watcher khởi động từ ID cảnh báo gần nhất: {last_seen_id}")
            else:
                logger.info("Cơ sở dữ liệu alerts trống. Watcher sẽ bắt đầu từ đầu.")
    except Exception as e:
        logger.error(f"Lỗi khởi tạo ID watcher: {e}")
        
    while not stop_event.is_set():
        try:
            if collection is not None:
                query = {}
                if last_seen_id:
                    query["_id"] = {"$gt": last_seen_id}
                
                new_alerts = list(collection.find(query).sort("_id", 1))
                for alert in new_alerts:
                    alert["id"] = str(alert["_id"])
                    del alert["_id"]
                    last_seen_id = ObjectId(alert["id"])
                    
                    # Bỏ qua các alert đã được emit từ API predict/ingest
                    # (các route đó đã tự emit WebSocket rồi)
                    source = alert.get("source", "")
                    if source in ("streaming", "batch_predict", "external", "seed_mock"):
                        continue
                    
                    logger.info(f"[WebSockets Push] Phát hiện xâm nhập mới: {alert.get('attack_cat', 'N/A')} từ {alert.get('srcip', 'N/A')}")
                    socketio.emit("new_alert", alert)
            time.sleep(0.2)
        except Exception as e:
            logger.error(f"Lỗi trong tiến trình quét alerts nền: {e}")
            time.sleep(1.0)

def graceful_shutdown(sig, frame):
    logger.info("Bắt đầu dừng server một cách an toàn (Graceful Shutdown)...")
    stop_event.set()
    close_db()
    logger.info("Đã dọn dẹp các kết nối. Tạm biệt!")
    sys.exit(0)

if __name__ == "__main__":
    try:
        signal.signal(signal.SIGINT, graceful_shutdown)
        signal.signal(signal.SIGTERM, graceful_shutdown)
    except ValueError as ve:
        logger.warning(f"Không thể đăng ký signal handlers: {ve}")

    if not app.debug or os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        watcher_thread = threading.Thread(target=monitor_mongodb_inserts, daemon=True)
        watcher_thread.start()
        
    logger.info(f"Đang khởi chạy SocketIO Flask Server tại địa chỉ: http://{Config.HOST}:{Config.PORT}")
    socketio.run(app, debug=Config.DEBUG, host=Config.HOST, port=Config.PORT, allow_unsafe_werkzeug=True)
