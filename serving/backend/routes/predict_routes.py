from flask import Blueprint, jsonify, request
from datetime import datetime, timezone
from core.database import collection
from core.extensions import socketio
from services.model_service import predict_single, get_model_status
from config.settings import logger

predict_bp = Blueprint('predict_bp', __name__)


@predict_bp.route("/predict", methods=["POST"])
def predict():
    """
    Nhận 1 bản ghi network traffic (JSON), chạy dự đoán qua 2-stage XGBoost,
    và trả về kết quả phân loại.
    
    Nếu phát hiện tấn công (is_attack=True), tự động lưu alert vào MongoDB
    và phát real-time qua WebSocket.
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"status": "error", "message": "Request body trống hoặc không phải JSON"}), 400

        # Chạy dự đoán
        result = predict_single(data)

        if "error" in result:
            return jsonify({"status": "error", "message": result["error"]}), 500

        response = {
            "status": "success",
            "data": {
                "is_attack": result["is_attack"],
                "attack_cat": result["attack_cat"],
                "confidence": result["confidence"],
                "threat_score": result.get("threat_score", 0),
            }
        }

        # Nếu phát hiện tấn công -> tự lưu alert vào MongoDB + đẩy WebSocket
        if result["is_attack"] and collection is not None:
            alert_doc = {
                "srcip": data.get("srcip", "unknown"),
                "dstip": data.get("dstip", "unknown"),
                "proto": data.get("proto", "unknown"),
                "service": data.get("service", "-"),
                "state": data.get("state", "unknown"),
                "attack_cat": result["attack_cat"],
                "confidence": result["confidence"],
                "threat_score": result.get("threat_score", 0),
                "status": "pending",
                "resolved_by": None,
                "source": "streaming",
                "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            }
            insert_result = collection.insert_one(alert_doc)
            alert_doc["id"] = str(insert_result.inserted_id)
            del alert_doc["_id"]

            # Đẩy real-time qua WebSocket
            try:
                socketio.emit("new_alert", alert_doc)
                logger.info(f"[Predict→WS] Phát hiện {result['attack_cat']} từ {alert_doc['srcip']}")
            except Exception as ws_err:
                logger.warning(f"Không thể emit WebSocket: {ws_err}")

            response["data"]["alert_id"] = alert_doc["id"]

        return jsonify(response), 200

    except Exception as e:
        logger.error(f"Error in /predict: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@predict_bp.route("/predict/batch", methods=["POST"])
def predict_batch():
    """
    Nhận một mảng bản ghi network traffic, chạy dự đoán cho từng bản ghi.
    Tự động lưu tất cả các attack vào MongoDB và phát WebSocket.
    """
    try:
        data = request.get_json()
        if not data or not isinstance(data, list):
            return jsonify({"status": "error", "message": "Body phải là một mảng JSON"}), 400

        if len(data) > 100:
            return jsonify({"status": "error", "message": "Tối đa 100 bản ghi mỗi lần gọi"}), 400

        results = []
        alerts_to_insert = []

        for record in data:
            result = predict_single(record)
            prediction = {
                "srcip": record.get("srcip", "unknown"),
                "dstip": record.get("dstip", "unknown"),
                "is_attack": result["is_attack"],
                "attack_cat": result["attack_cat"],
                "confidence": result["confidence"],
                "threat_score": result.get("threat_score", 0),
            }
            results.append(prediction)

            # Thu thập các alert tấn công
            if result["is_attack"]:
                alerts_to_insert.append({
                    "srcip": record.get("srcip", "unknown"),
                    "dstip": record.get("dstip", "unknown"),
                    "proto": record.get("proto", "unknown"),
                    "service": record.get("service", "-"),
                    "state": record.get("state", "unknown"),
                    "attack_cat": result["attack_cat"],
                    "confidence": result["confidence"],
                    "threat_score": result.get("threat_score", 0),
                    "status": "pending",
                    "resolved_by": None,
                    "source": "batch_predict",
                    "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                })

        # Bulk insert tất cả alerts vào MongoDB
        inserted_count = 0
        if alerts_to_insert and collection is not None:
            insert_result = collection.insert_many(alerts_to_insert)
            inserted_count = len(insert_result.inserted_ids)

            # Đẩy WebSocket cho từng alert
            for i, doc_id in enumerate(insert_result.inserted_ids):
                alert = alerts_to_insert[i]
                alert["id"] = str(doc_id)
                if "_id" in alert:
                    del alert["_id"]
                try:
                    socketio.emit("new_alert", alert)
                except Exception:
                    pass

            logger.info(f"[PredictBatch] Đã insert {inserted_count} alerts vào MongoDB.")

        return jsonify({
            "status": "success",
            "data": {
                "predictions": results,
                "total_records": len(data),
                "attacks_detected": inserted_count,
            }
        }), 200

    except Exception as e:
        logger.error(f"Error in /predict/batch: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@predict_bp.route("/model/status", methods=["GET"])
def model_status():
    """
    Kiểm tra trạng thái load model hiện tại.
    """
    try:
        status = get_model_status()
        return jsonify({"status": "success", "data": status}), 200
    except Exception as e:
        logger.error(f"Error in /model/status: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500
