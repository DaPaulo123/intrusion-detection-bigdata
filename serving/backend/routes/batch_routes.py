from flask import Blueprint, jsonify
from core.database import batch_collection
from core.extensions import cache
from config.settings import logger

batch_bp = Blueprint('batch_bp', __name__)

@batch_bp.route("/batch/stats", methods=["GET"])
@cache.cached(timeout=30)
def get_batch_stats():
    try:
        if batch_collection is None:
            return jsonify({"status": "error", "message": "DB not available"}), 500
        stats = batch_collection.find_one({}, {"_id": 0})
        if not stats:
            return jsonify({"status": "error", "message": "No data"}), 404
        return jsonify({"status": "success", "data": stats}), 200
    except Exception as e:
        logger.error(f"Error in /batch/stats: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500
