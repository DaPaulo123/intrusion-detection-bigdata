from pymongo import MongoClient, DESCENDING, ASCENDING
from config.settings import Config, logger

client = None
db = None
collection = None
batch_collection = None

try:
    logger.info(f"Đang thiết lập kết nối tới MongoDB tại: {Config.MONGO_URI}")
    client = MongoClient(Config.MONGO_URI, serverSelectionTimeoutMS=5000)
    client.admin.command('ping')
    db = client[Config.DB_NAME]
    collection = db[Config.ALERTS_COLLECTION]
    batch_collection = db[Config.BATCH_STATS_COLLECTION]
    
    logger.info("Đang tạo chỉ mục (indexing) cho collection alerts...")
    collection.create_index([("timestamp", DESCENDING)])
    collection.create_index([("status", ASCENDING)])
    logger.info("Kết nối MongoDB và khởi tạo chỉ mục thành công!")
except Exception as e:
    logger.error(f"Lỗi kết nối cơ sở dữ liệu MongoDB: {e}")

def close_db():
    global client
    if client:
        logger.info("Đang đóng kết nối MongoDB...")
        client.close()
        logger.info("Đã đóng kết nối MongoDB.")
