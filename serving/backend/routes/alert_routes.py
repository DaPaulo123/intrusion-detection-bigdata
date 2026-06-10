from flask import Blueprint, jsonify, request
from datetime import datetime, timedelta, timezone
import pymongo
from bson import ObjectId
from core.database import collection
from core.security import require_api_key
from core.extensions import socketio
from config.settings import logger

alert_bp = Blueprint('alert_bp', __name__)

@alert_bp.route("/alerts", methods=["GET"])
def get_alerts():
    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
        status_filter = request.args.get('status')
        skip = (page - 1) * limit
        
        if collection is None:
            return jsonify({"status": "error", "message": "DB not available"}), 500
            
        query = {}
        if status_filter: query["status"] = status_filter
            
        total_records = collection.count_documents(query)
        total_pages = (total_records + limit - 1) // limit if total_records > 0 else 1
        
        alerts_cursor = collection.find(query).sort("timestamp", pymongo.DESCENDING).skip(skip).limit(limit)
        alerts = []
        for doc in alerts_cursor:
            doc["id"] = str(doc["_id"])
            del doc["_id"]
            alerts.append(doc)
            
        return jsonify({
            "status": "success",
            "data": alerts,
            "meta": {"total_records": total_records, "total_pages": total_pages, "current_page": page, "limit": limit}
        }), 200
    except Exception as e:
        logger.error(f"Error in /alerts: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@alert_bp.route("/alerts/<alert_id>/status", methods=["PUT"])
@require_api_key
def update_alert_status(alert_id):
    try:
        data = request.get_json() or {}
        status = data.get("status")
        resolved_by = data.get("resolved_by")
        
        if status not in ["pending", "handled"]:
            return jsonify({"status": "error", "message": "Invalid status"}), 400
        if not resolved_by or not str(resolved_by).strip():
            return jsonify({"status": "error", "message": "resolved_by is required"}), 400
        if collection is None:
            return jsonify({"status": "error", "message": "DB not available"}), 500
            
        result = collection.update_one(
            {"_id": ObjectId(alert_id)},
            {"$set": {"status": status, "resolved_by": resolved_by.strip(), "resolved_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")}}
        )
        if result.matched_count == 0:
            return jsonify({"status": "error", "message": "Alert not found"}), 404
            
        try:
            socketio.emit("alert_status_updated", {"id": alert_id, "status": status, "resolved_by": resolved_by.strip()})
        except Exception as se:
            logger.warning(f"Could not emit WS: {se}")
            
        return jsonify({"status": "success", "message": "Updated", "data": {"id": alert_id, "status": status, "resolved_by": resolved_by}}), 200
    except Exception as e:
        logger.error(f"Error in PUT /alerts: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@alert_bp.route("/alerts/summary", methods=["GET"])
def get_alerts_summary():
    try:
        if collection is None:
            return jsonify({"status": "error", "message": "DB not available"}), 500
            
        pipeline = [{"$group": {"_id": "$attack_cat", "count": {"$sum": 1}}}, {"$sort": {"count": -1}}]
        agg_results = list(collection.aggregate(pipeline))
        category_summary = {item["_id"]: item["count"] for item in agg_results}
        
        ten_minutes_ago = (datetime.now(timezone.utc) - timedelta(minutes=10)).isoformat().replace("+00:00", "Z")
        recent_attacks_count = collection.count_documents({"attack_cat": {"$ne": "Normal"}, "timestamp": {"$gte": ten_minutes_ago}})
        pending_count = collection.count_documents({"status": "pending"})
        
        return jsonify({
            "status": "success",
            "data": {
                "category_summary": category_summary,
                "recent_10m_attacks": recent_attacks_count,
                "pending_alerts_count": pending_count,
                "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
            }
        }), 200
    except Exception as e:
        logger.error(f"Error in /alerts/summary: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500
