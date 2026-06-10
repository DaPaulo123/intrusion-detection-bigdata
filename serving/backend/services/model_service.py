import os
import json
import numpy as np
import xgboost as xgb
from config.settings import logger

# ─── Đường dẫn tới thư mục models ──────────────────────────────────────────
# Lấy root path cục bộ: .../intrusion-detection-bigdata
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
# Cho phép override bằng biến môi trường (cần cho Docker)
MODEL_DIR = os.environ.get("MODEL_DIR", os.path.join(BASE_DIR, "models"))

# ─── Cache toàn cục cho model (lazy load) ───────────────────────────────────
_model_cache = {
    "stage1": None,
    "stage2": None,
    "feature_names": None,
    "categorical_encoders": None,
    "attack_mapping": None,       # index -> tên attack
    "attack_mapping_rev": None,   # tên attack -> index
    "loaded": False,
}


def _load_models():
    """
    Lazy-load 2 mô hình XGBoost (stage1 binary, stage2 multiclass)
    và các file metadata cần thiết cho việc dự đoán.
    Chỉ load một lần duy nhất khi API được gọi lần đầu.
    """
    if _model_cache["loaded"]:
        return True

    try:
        # 1. Load Stage 1 - Binary (Normal vs Attack)
        stage1_path = os.path.join(MODEL_DIR, "stage1_model.json")
        if not os.path.exists(stage1_path):
            logger.error(f"Không tìm thấy Stage 1 model tại: {stage1_path}")
            return False
        booster1 = xgb.Booster()
        booster1.load_model(stage1_path)
        _model_cache["stage1"] = booster1
        logger.info(f"Đã tải Stage 1 model (Binary) từ {stage1_path}")

        # 2. Load Stage 2 - Multiclass (9 loại tấn công)
        stage2_path = os.path.join(MODEL_DIR, "stage2_model.json")
        if not os.path.exists(stage2_path):
            logger.error(f"Không tìm thấy Stage 2 model tại: {stage2_path}")
            return False
        booster2 = xgb.Booster()
        booster2.load_model(stage2_path)
        _model_cache["stage2"] = booster2
        logger.info(f"Đã tải Stage 2 model (Multiclass) từ {stage2_path}")

        # 3. Load feature names
        feat_path = os.path.join(MODEL_DIR, "feature_names.json")
        if os.path.exists(feat_path):
            with open(feat_path, "r", encoding="utf-8") as f:
                feat_list = json.load(f)
                _model_cache["feature_names"] = feat_list
            logger.info(f"Đã tải danh sách {len(feat_list)} features.")

        # 4. Load categorical encoders
        enc_path = os.path.join(MODEL_DIR, "categorical_encoders.json")
        if os.path.exists(enc_path):
            with open(enc_path, "r", encoding="utf-8") as f:
                _model_cache["categorical_encoders"] = json.load(f)
            logger.info("Đã tải categorical encoders.")

        # 5. Load attack mapping (index -> name)
        map_path = os.path.join(MODEL_DIR, "attack_mapping.json")
        if os.path.exists(map_path):
            with open(map_path, "r", encoding="utf-8") as f:
                raw = json.load(f)  # {"Analysis": 0, "Backdoor": 1, ...}
                _model_cache["attack_mapping_rev"] = raw
                _model_cache["attack_mapping"] = {v: k for k, v in raw.items()}
            logger.info(f"Đã tải attack mapping: {list(raw.keys())}")

        _model_cache["loaded"] = True
        logger.info("✅ Tất cả mô hình và metadata đã sẵn sàng phục vụ Serving!")
        return True

    except Exception as e:
        logger.error(f"Lỗi khi tải mô hình ML: {e}")
        return False


def predict_single(record: dict) -> dict:
    """
    Dự đoán cho 1 bản ghi network traffic.
    Input: dict chứa các field raw (srcip, dstip, proto, state, dur, sbytes, ...).
    Output: dict chứa kết quả dự đoán (is_attack, attack_cat, confidence).
    """
    if not _load_models():
        return {"error": "Models not loaded", "is_attack": False, "attack_cat": "Unknown", "confidence": 0.0}

    feature_names: list = _model_cache["feature_names"] or []
    encoders: dict = _model_cache["categorical_encoders"] or {}
    attack_map: dict = _model_cache["attack_mapping"] or {}

    if not feature_names:
        return {"error": "Feature names not loaded", "is_attack": False, "attack_cat": "Unknown", "confidence": 0.0}

    # Bước 1: Encode categorical features
    encoded = {}
    for feat in feature_names:
        if feat in encoders:
            # Đây là categorical feature, cần encode string -> index
            cat_name = feat  # "state", "proto", "service"
            raw_val = str(record.get(cat_name, ""))
            # Tìm index tương ứng trong encoder (reverse lookup)
            encoder_map: dict = encoders[cat_name]  # {"0": "ACC", "1": "CLO", ...}
            found_idx = -1
            for idx_str, label in encoder_map.items():
                if label == raw_val:
                    found_idx = int(idx_str)
                    break
            # Tên feature thực tế trong model có thể là "state_index", "proto_index"...
            # Nhưng feature_names.json đã chứa tên gốc (state, proto, service)
            encoded[feat] = float(found_idx) if found_idx >= 0 else 0.0
        else:
            # Numeric feature
            val = record.get(feat, 0)
            try:
                encoded[feat] = float(val) if val is not None else 0.0
            except (ValueError, TypeError):
                encoded[feat] = 0.0

    # Bước 2: Tạo feature vector theo đúng thứ tự
    feature_vector = [encoded.get(f, 0.0) for f in feature_names]
    dmatrix = xgb.DMatrix(np.array([feature_vector]), feature_names=feature_names)

    # Bước 3: Stage 1 - Binary prediction
    stage1_model = _model_cache["stage1"]
    if stage1_model is None:
        return {"error": "Stage 1 model not loaded", "is_attack": False, "attack_cat": "Unknown", "confidence": 0.0}

    stage1_prob = stage1_model.predict(dmatrix)  # probability of attack
    is_attack_prob = float(stage1_prob[0])
    is_attack = is_attack_prob >= 0.5

    result = {
        "is_attack": is_attack,
        "attack_cat": "Normal",
        "confidence": round(1.0 - is_attack_prob if not is_attack else is_attack_prob, 4),
        "threat_score": 0,
    }

    # Bước 4: Nếu Stage 1 phát hiện Attack -> chạy Stage 2
    stage2_model = _model_cache["stage2"]
    if is_attack and stage2_model is not None:
        stage2_probs = stage2_model.predict(dmatrix)
        if stage2_probs.ndim >= 2:
            predicted_idx = int(np.argmax(stage2_probs[0]))
        else:
            predicted_idx = int(stage2_probs[0])
        attack_name = attack_map.get(str(predicted_idx), attack_map.get(predicted_idx, f"Unknown({predicted_idx})"))

        result["attack_cat"] = attack_name
        result["threat_score"] = int(min(is_attack_prob * 100, 100))

    return result


def get_model_metrics():
    """
    Đọc trực tiếp các chỉ số ML thực tế từ file kết quả đánh giá mô hình.
    Hỗ trợ cả format nested mới (stage1/stage2/overall) và format cũ (flat).
    """
    metrics_path = os.path.join(MODEL_DIR, "model_metrics.json")

    default_metrics = {
        "stage1": {
            "accuracy": 0.0, "precision": 0.0, "recall": 0.0,
            "f1": 0.0, "auc_roc": 0.0,
            "n_estimators": 100, "max_depth": 6
        },
        "stage2": {
            "accuracy": 0.0, "macro_f1": 0.0, "weighted_f1": 0.0,
            "n_estimators": 200, "max_depth": 8
        },
        "overall": {
            "accuracy": 0.0, "macro_f1": 0.0, "weighted_f1": 0.0
        },
        "is_simulated": True,
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


def get_model_status():
    """
    Trả về trạng thái load model hiện tại (đã sẵn sàng hay chưa).
    """
    loaded = _load_models()
    return {
        "models_loaded": loaded,
        "stage1_loaded": _model_cache["stage1"] is not None,
        "stage2_loaded": _model_cache["stage2"] is not None,
        "feature_count": len(_model_cache["feature_names"]) if isinstance(_model_cache["feature_names"], list) else 0,
        "attack_categories": list(_model_cache["attack_mapping"].values()) if isinstance(_model_cache["attack_mapping"], dict) else [],
    }
