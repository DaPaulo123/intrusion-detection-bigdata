from flask import Blueprint, jsonify, request
from datetime import datetime, timezone
from core.database import collection
from core.extensions import socketio
from core.security import require_api_key
from config.settings import logger

ingest_bp = Blueprint('ingest_bp', __name__)


@ingest_bp.route("/alerts/ingest", methods=["POST"])
@require_api_key
def ingest_alerts():
    """
    Endpoint nhận kết quả từ luồng Streaming hoặc Batch Processing.
    Cho phép insert trực tiếp 1 hoặc nhiều alerts vào MongoDB.
    
    Body có thể là:
    - 1 object: {"srcip": "...", "attack_cat": "DoS", ...}
    - 1 mảng:  [{"srcip": "...", ...}, {"srcip": "...", ...}]
    
    Tất cả alerts sẽ được tự động phát qua WebSocket event 'new_alert'.
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"status": "error", "message": "Request body trống hoặc không phải JSON"}), 400
        
        if collection is None:
            return jsonify({"status": "error", "message": "MongoDB không khả dụng"}), 500

        # Chuẩn hóa: luôn làm việc với list
        records = data if isinstance(data, list) else [data]
        
        if len(records) > 500:
            return jsonify({"status": "error", "message": "Tối đa 500 alerts mỗi lần gọi"}), 400

        now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        
        docs_to_insert = []
        for rec in records:
            doc = {
                "srcip": rec.get("srcip", "unknown"),
                "dstip": rec.get("dstip", "unknown"),
                "proto": rec.get("proto", "unknown"),
                "service": rec.get("service", "-"),
                "state": rec.get("state", "unknown"),
                "attack_cat": rec.get("attack_cat", "Unknown"),
                "confidence": float(rec.get("confidence", 0.0)),
                "threat_score": int(rec.get("threat_score", 0)),
                "status": "pending",
                "resolved_by": None,
                "source": rec.get("source", "external"),
                "timestamp": rec.get("timestamp", now),
            }
            docs_to_insert.append(doc)
        
        # Bulk insert
        result = collection.insert_many(docs_to_insert)
        inserted_count = len(result.inserted_ids)
        
        # Đẩy WebSocket cho từng alert mới
        for i, doc_id in enumerate(result.inserted_ids):
            alert = docs_to_insert[i].copy()
            alert["id"] = str(doc_id)
            if "_id" in alert:
                del alert["_id"]
            try:
                socketio.emit("new_alert", alert)
            except Exception:
                pass
        
        logger.info(f"[Ingest] Đã nhận và lưu {inserted_count} alerts từ nguồn '{docs_to_insert[0].get('source', 'external')}'.")
        
        return jsonify({
            "status": "success",
            "message": f"Đã lưu thành công {inserted_count} alerts.",
            "data": {"inserted_count": inserted_count}
        }), 201

    except Exception as e:
        logger.error(f"Error in /alerts/ingest: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500
