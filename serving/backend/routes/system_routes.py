from flask import Blueprint, jsonify
from datetime import datetime, timezone
from services.docker_service import get_docker_containers
from services.model_service import get_model_metrics, get_model_status
from config.settings import logger

system_bp = Blueprint('system_bp', __name__)

@system_bp.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "success", "data": {"status": "running", "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")}}), 200

@system_bp.route("/system/health", methods=["GET"])
def get_system_health():
    try:
        containers = get_docker_containers()
        running_count = sum(1 for c in containers if c["status"] == "running")
        total_count = len(containers)
        return jsonify({
            "status": "success",
            "data": {
                "services": containers,
                "summary": {
                    "total_services": total_count,
                    "running_services": running_count,
                    "health_percentage": round((running_count / total_count) * 100, 2) if total_count > 0 else 0
                }
            }
        }), 200
    except Exception as e:
        logger.error(f"Error in /system/health: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@system_bp.route("/system/model-metrics", methods=["GET"])
def get_model_metrics_api():
    try:
        metrics = get_model_metrics()
        return jsonify({"status": "success", "data": metrics}), 200
    except Exception as e:
        logger.error(f"Error in /system/model-metrics: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500
