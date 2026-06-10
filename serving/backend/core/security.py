from functools import wraps
from flask import request, jsonify
from config.settings import Config, logger

def require_api_key(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        api_key = request.headers.get("X-API-Key")
        if not api_key:
            auth_header = request.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                api_key = auth_header.split(" ")[1]
        
        if not api_key or api_key != Config.API_KEY:
            logger.warning(f"Từ chối truy cập trái phép từ IP: {request.remote_addr}")
            return jsonify({
                "status": "error",
                "message": "Không có quyền truy cập. Vui lòng cung cấp API Key hợp lệ qua header 'X-API-Key' hoặc 'Authorization: Bearer <Key>'."
            }), 401
        return f(*args, **kwargs)
    return decorated
