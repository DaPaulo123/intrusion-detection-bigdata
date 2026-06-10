from flask import Blueprint, render_template_string

docs_bp = Blueprint('docs_bp', __name__)

@docs_bp.route("/", methods=["GET"])
@docs_bp.route("/docs", methods=["GET"])
def api_docs():
    html_content = """
    <!DOCTYPE html>
    <html lang="vi">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>SOC serving API Documentation</title>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
        <style>
            :root {
                --bg-color: #0b0f19;
                --card-bg: rgba(17, 24, 39, 0.7);
                --card-border: rgba(255, 255, 255, 0.08);
                --text-primary: #f3f4f6;
                --text-secondary: #9ca3af;
                --accent-cyan: #06b6d4;
                --accent-green: #10b981;
                --accent-purple: #8b5cf6;
                --accent-red: #ef4444;
            }
            * {
                box-sizing: border-box;
                margin: 0;
                padding: 0;
            }
            body {
                font-family: 'Inter', sans-serif;
                background-color: var(--bg-color);
                color: var(--text-primary);
                min-height: 100vh;
                padding: 2rem 1rem;
                background-image: radial-gradient(circle at 10% 20%, rgba(6, 182, 212, 0.1) 0%, transparent 40%),
                                  radial-gradient(circle at 90% 80%, rgba(139, 92, 246, 0.1) 0%, transparent 40%);
                background-attachment: fixed;
            }
            .container {
                max-width: 1100px;
                margin: 0 auto;
            }
            header {
                text-align: center;
                margin-bottom: 3rem;
                padding: 2rem;
                background: var(--card-bg);
                backdrop-filter: blur(12px);
                border: 1px solid var(--card-border);
                border-radius: 16px;
                box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
            }
            h1 {
                font-size: 2.5rem;
                font-weight: 700;
                background: linear-gradient(135deg, var(--accent-cyan), var(--accent-purple));
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                margin-bottom: 0.5rem;
            }
            .subtitle {
                color: var(--text-secondary);
                font-size: 1.1rem;
            }
            .badge-key {
                display: inline-block;
                margin-top: 1rem;
                padding: 0.4rem 0.8rem;
                background: rgba(6, 182, 212, 0.15);
                border: 1px solid rgba(6, 182, 212, 0.3);
                border-radius: 20px;
                color: var(--accent-cyan);
                font-size: 0.85rem;
                font-family: monospace;
            }
            .endpoint-card {
                background: var(--card-bg);
                backdrop-filter: blur(12px);
                border: 1px solid var(--card-border);
                border-radius: 16px;
                margin-bottom: 1.5rem;
                overflow: hidden;
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                box-shadow: 0 4px 20px rgba(0,0,0,0.2);
            }
            .endpoint-card:hover {
                transform: translateY(-2px);
                border-color: rgba(6, 182, 212, 0.3);
                box-shadow: 0 8px 30px rgba(6, 182, 212, 0.15);
            }
            .endpoint-header {
                display: flex;
                align-items: center;
                padding: 1.2rem 1.5rem;
                cursor: pointer;
                user-select: none;
            }
            .method {
                font-weight: 700;
                font-size: 0.85rem;
                padding: 0.3rem 0.8rem;
                border-radius: 6px;
                margin-right: 1rem;
                min-width: 80px;
                text-align: center;
                font-family: monospace;
            }
            .method.get {
                background: rgba(16, 185, 129, 0.15);
                color: var(--accent-green);
                border: 1px solid rgba(16, 185, 129, 0.3);
            }
            .method.put {
                background: rgba(139, 92, 246, 0.15);
                color: var(--accent-purple);
                border: 1px solid rgba(139, 92, 246, 0.3);
            }
            .method.ws {
                background: rgba(6, 182, 212, 0.15);
                color: var(--accent-cyan);
                border: 1px solid rgba(6, 182, 212, 0.3);
            }
            .path {
                font-family: monospace;
                font-size: 1.1rem;
                font-weight: 600;
                color: var(--text-primary);
                flex-grow: 1;
            }
            .description {
                color: var(--text-secondary);
                font-size: 0.95rem;
            }
            .endpoint-body {
                padding: 1.5rem;
                border-top: 1px solid var(--card-border);
                background: rgba(0, 0, 0, 0.2);
            }
            .section-title {
                font-size: 0.9rem;
                text-transform: uppercase;
                letter-spacing: 0.05em;
                color: var(--accent-cyan);
                margin-bottom: 0.8rem;
                font-weight: 600;
            }
            .table {
                width: 100%;
                border-collapse: collapse;
                margin-bottom: 1.2rem;
            }
            .table th, .table td {
                padding: 0.75rem 1rem;
                text-align: left;
                border-bottom: 1px solid rgba(255, 255, 255, 0.05);
            }
            .table th {
                color: var(--text-secondary);
                font-size: 0.85rem;
                font-weight: 600;
            }
            .table td {
                font-size: 0.9rem;
            }
            .table td.param-name {
                font-family: monospace;
                color: var(--text-primary);
                font-weight: 600;
            }
            .table td.param-type {
                font-family: monospace;
                color: var(--accent-purple);
            }
            .json-block {
                background: #070a13;
                border: 1px solid var(--card-border);
                border-radius: 8px;
                padding: 1rem;
                font-family: 'Fira Code', 'Courier New', Courier, monospace;
                font-size: 0.85rem;
                overflow-x: auto;
                color: #e5e7eb;
                max-height: 350px;
            }
            .auth-badge {
                background: rgba(239, 68, 68, 0.15);
                color: var(--accent-red);
                border: 1px solid rgba(239, 68, 68, 0.3);
                font-size: 0.75rem;
                padding: 0.2rem 0.5rem;
                border-radius: 4px;
                margin-left: 0.5rem;
                font-weight: 500;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <h1>SOC Intrusion Detection API</h1>
                <p class="subtitle">Hệ thống phân phối dữ liệu phân tích xâm nhập mạng thời gian thực</p>
                <div class="badge-key">API KEY Mẫu: SOC-Super-Secret-2026</div>
            </header>

            <!-- API List -->
            
            <!-- GET /health -->
            <div class="endpoint-card">
                <div class="endpoint-header">
                    <span class="method get">GET</span>
                    <span class="path">/api/health</span>
                    <span class="description">Kiểm tra trạng thái sống của dịch vụ API</span>
                </div>
                <div class="endpoint-body">
                    <div class="section-title">Response mẫu (200 OK)</div>
                    <pre class="json-block">{
  "status": "success",
  "data": {
    "status": "running",
    "timestamp": "2026-06-04T02:56:00Z"
  }
}</pre>
                </div>
            </div>

            <!-- GET /alerts -->
            <div class="endpoint-card">
                <div class="endpoint-header">
                    <span class="method get">GET</span>
                    <span class="path">/api/alerts</span>
                    <span class="description">Lấy danh sách các cảnh báo xâm nhập (có phân trang)</span>
                </div>
                <div class="endpoint-body">
                    <div class="section-title">Tham số Query</div>
                    <table class="table">
                        <thead>
                            <tr>
                                <th>Tham số</th>
                                <th>Kiểu</th>
                                <th>Bắt buộc</th>
                                <th>Mô tả</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td class="param-name">page</td>
                                <td class="param-type">Integer</td>
                                <td>Không (Mặc định: 1)</td>
                                <td>Trang cần tải dữ liệu</td>
                            </tr>
                            <tr>
                                <td class="param-name">limit</td>
                                <td class="param-type">Integer</td>
                                <td>Không (Mặc định: 20)</td>
                                <td>Số dòng dữ liệu tối đa trả về trên mỗi trang</td>
                            </tr>
                            <tr>
                                <td class="param-name">status</td>
                                <td class="param-type">String</td>
                                <td>Không</td>
                                <td>Lọc theo trạng thái ('pending' hoặc 'handled')</td>
                            </tr>
                        </tbody>
                    </table>
                    
                    <div class="section-title">Response mẫu (200 OK)</div>
                    <pre class="json-block">{
  "status": "success",
  "data": [
    {
      "id": "65b2a5b28d6c7028b0fde8b1",
      "srcip": "192.168.1.105",
      "dstip": "10.0.0.1",
      "proto": "tcp",
      "attack_cat": "DoS",
      "confidence": 0.9412,
      "threat_score": 85,
      "status": "pending",
      "resolved_by": null,
      "timestamp": "2026-06-04T02:50:00Z"
    }
  ],
  "meta": {
    "current_page": 1,
    "limit": 20,
    "total_pages": 3,
    "total_records": 58
  }
}</pre>
                </div>
            </div>

            <!-- PUT /alerts/<id>/status -->
            <div class="endpoint-card">
                <div class="endpoint-header">
                    <span class="method put">PUT</span>
                    <span class="path">/api/alerts/&lt;id&gt;/status</span>
                    <span class="description">Cập nhật trạng thái xử lý cảnh báo</span>
                    <span class="auth-badge">Yêu cầu API Key</span>
                </div>
                <div class="endpoint-body">
                    <div class="section-title">Headers bắt buộc</div>
                    <table class="table">
                        <thead>
                            <tr>
                                <th>Header</th>
                                <th>Giá trị ví dụ</th>
                                <th>Mô tả</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td class="param-name">X-API-Key</td>
                                <td>SOC-Super-Secret-2026</td>
                                <td>Mã khóa bảo vệ API đầu cuối ghi dữ liệu</td>
                            </tr>
                        </tbody>
                    </table>

                    <div class="section-title">Request Body (JSON)</div>
                    <pre class="json-block">{
  "status": "handled",
  "resolved_by": "Nguyễn Văn SOC"
}</pre>

                    <div class="section-title">Response mẫu (200 OK)</div>
                    <pre class="json-block">{
  "status": "success",
  "message": "Cập nhật trạng thái cảnh báo thành công.",
  "data": {
    "id": "65b2a5b28d6c7028b0fde8b1",
    "status": "handled",
    "resolved_by": "Nguyễn Văn SOC"
  }
}</pre>
                </div>
            </div>

            <!-- GET /alerts/summary -->
            <div class="endpoint-card">
                <div class="endpoint-header">
                    <span class="method get">GET</span>
                    <span class="path">/api/alerts/summary</span>
                    <span class="description">Lấy thống kê nhanh về các mối nguy và số lượng trong 10 phút</span>
                </div>
                <div class="endpoint-body">
                    <div class="section-title">Response mẫu (200 OK)</div>
                    <pre class="json-block">{
  "status": "success",
  "data": {
    "category_summary": {
      "DoS": 24,
      "Normal": 15,
      "Exploits": 10,
      "Fuzzers": 6,
      "Worms": 3
    },
    "recent_10m_attacks": 8,
    "pending_alerts_count": 42,
    "timestamp": "2026-06-04T02:56:10Z"
  }
}</pre>
                </div>
            </div>

            <!-- GET /batch/stats -->
            <div class="endpoint-card">
                <div class="endpoint-header">
                    <span class="method get">GET</span>
                    <span class="path">/api/batch/stats</span>
                    <span class="description">Lấy thông tin tổng hợp phân tích sâu offline (Có Redis Cache)</span>
                </div>
                <div class="endpoint-body">
                    <div class="section-title">Response mẫu (200 OK)</div>
                    <pre class="json-block">{
  "status": "success",
  "data": {
    "total_records_processed": 145890,
    "last_batch_run": "2026-06-04T02:56:00Z",
    "peak_hours": [
      { "hour": 0, "attack_count": 45 },
      { "hour": 9, "attack_count": 210 }
    ],
    "threat_score_distribution": [
      { "range": "0-10", "count": 10 },
      { "range": "91-100", "count": 310 }
    ],
    "category_summary": [
      { "attack_cat": "DoS", "count": 12450 }
    ]
  }
}</pre>
                </div>
            </div>

            <!-- GET /system/health -->
            <div class="endpoint-card">
                <div class="endpoint-header">
                    <span class="method get">GET</span>
                    <span class="path">/api/system/health</span>
                    <span class="description">Kiểm tra trạng thái container của hệ sinh thái Docker BigData</span>
                </div>
                <div class="endpoint-body">
                    <div class="section-title">Response mẫu (200 OK)</div>
                    <pre class="json-block">{
  "status": "success",
  "data": {
    "services": [
      {
        "container_name": "kafka",
        "image": "confluentinc/cp-kafka:7.4.0",
        "name": "Kafka Broker",
        "status": "running",
        "uptime": "Up 2 hours"
      },
      {
        "container_name": "redis",
        "image": "redis:7",
        "name": "Redis Cache",
        "status": "running",
        "uptime": "Up 2 hours"
      }
    ],
    "summary": {
      "health_percentage": 100.0,
      "running_services": 8,
      "total_services": 8
    }
  }
}</pre>
                </div>
            </div>

            <!-- GET /system/model-metrics -->
            <div class="endpoint-card">
                <div class="endpoint-header">
                    <span class="method get">GET</span>
                    <span class="path">/api/system/model-metrics</span>
                    <span class="description">Đọc trực tiếp các thông số kỹ thuật của mô hình ML Two-Stage</span>
                </div>
                <div class="endpoint-body">
                    <div class="section-title">Response mẫu (200 OK)</div>
                    <pre class="json-block">{
  "status": "success",
  "data": {
    "accuracy": 0.6214,
    "f1_score": 0.6887,
    "precision": 0.6545,
    "recall": 0.6214,
    "stage1_trees": 50,
    "stage2_trees": 100,
    "last_updated": "2026-06-03T18:00:00Z"
  }
}</pre>
                </div>
            </div>

            <!-- POST /predict -->
            <div class="endpoint-card">
                <div class="endpoint-header">
                    <span class="method put">POST</span>
                    <span class="path">/api/predict</span>
                    <span class="description">Dự đoán 1 bản ghi traffic qua mô hình XGBoost 2 giai đoạn</span>
                </div>
                <div class="endpoint-body">
                    <div class="section-title">Request Body (JSON) - 1 bản ghi network traffic</div>
                    <pre class="json-block">{
  "srcip": "192.168.1.105",
  "dstip": "10.0.0.1",
  "proto": "tcp",
  "state": "FIN",
  "service": "http",
  "dur": 0.121478,
  "sbytes": 100,
  "dbytes": 6000,
  "spkts": 4,
  "dpkts": 6,
  "sload": 300.5,
  "dload": 500.2,
  "threat_score": 75
}</pre>
                    <div class="section-title">Response mẫu (200 OK)</div>
                    <pre class="json-block">{
  "status": "success",
  "data": {
    "is_attack": true,
    "attack_cat": "DoS",
    "confidence": 0.9512,
    "threat_score": 95,
    "alert_id": "65b2a5b28d6c7028b0fde8b1"
  }
}</pre>
                </div>
            </div>

            <!-- POST /predict/batch -->
            <div class="endpoint-card">
                <div class="endpoint-header">
                    <span class="method put">POST</span>
                    <span class="path">/api/predict/batch</span>
                    <span class="description">Dự đoán hàng loạt (tối đa 100 bản ghi)</span>
                </div>
                <div class="endpoint-body">
                    <div class="section-title">Request Body (JSON Array)</div>
                    <pre class="json-block">[
  {"srcip": "192.168.1.105", "proto": "tcp", "dur": 0.12, ...},
  {"srcip": "10.0.0.15", "proto": "udp", "dur": 0.05, ...}
]</pre>
                    <div class="section-title">Response mẫu (200 OK)</div>
                    <pre class="json-block">{
  "status": "success",
  "data": {
    "total_records": 2,
    "attacks_detected": 1,
    "predictions": [
      {"srcip": "192.168.1.105", "is_attack": true, "attack_cat": "DoS", "confidence": 0.95},
      {"srcip": "10.0.0.15", "is_attack": false, "attack_cat": "Normal", "confidence": 0.88}
    ]
  }
}</pre>
                </div>
            </div>

            <!-- POST /alerts/ingest -->
            <div class="endpoint-card">
                <div class="endpoint-header">
                    <span class="method put">POST</span>
                    <span class="path">/api/alerts/ingest</span>
                    <span class="description">Nhận kết quả từ luồng Streaming/Batch, insert trực tiếp vào MongoDB</span>
                    <span class="auth-badge">Yêu cầu API Key</span>
                </div>
                <div class="endpoint-body">
                    <div class="section-title">Request Body (1 object hoặc mảng)</div>
                    <pre class="json-block">[
  {
    "srcip": "192.168.1.105",
    "dstip": "10.0.0.1",
    "proto": "tcp",
    "attack_cat": "DoS",
    "confidence": 0.95,
    "threat_score": 92,
    "source": "streaming"
  }
]</pre>
                    <div class="section-title">Response mẫu (201 Created)</div>
                    <pre class="json-block">{
  "status": "success",
  "message": "Đã lưu thành công 1 alerts.",
  "data": {"inserted_count": 1}
}</pre>
                </div>
            </div>

            <!-- GET /model/status -->
            <div class="endpoint-card">
                <div class="endpoint-header">
                    <span class="method get">GET</span>
                    <span class="path">/api/model/status</span>
                    <span class="description">Kiểm tra trạng thái sẵn sàng của mô hình ML (đã load chưa)</span>
                </div>
                <div class="endpoint-body">
                    <div class="section-title">Response mẫu (200 OK)</div>
                    <pre class="json-block">{
  "status": "success",
  "data": {
    "models_loaded": true,
    "stage1_loaded": true,
    "stage2_loaded": true,
    "feature_count": 50,
    "attack_categories": ["Analysis", "Backdoor", "DoS", "Exploits", "Fuzzers", "Generic", "Reconnaissance", "Shellcode", "Worms"]
  }
}</pre>
                </div>
            </div>

            <!-- WebSocket Stream -->
            <div class="endpoint-card" style="border-left: 4px solid var(--accent-cyan);">
                <div class="endpoint-header">
                    <span class="method ws">WS</span>
                    <span class="path">Kênh WebSockets: /</span>
                    <span class="description">Lắng nghe luồng cảnh báo xâm nhập thời gian thực</span>
                </div>
                <div class="endpoint-body">
                    <div class="section-title">Sự kiện lắng nghe (Listen Events)</div>
                    <table class="table">
                        <thead>
                            <tr>
                                <th>Tên Sự Kiện</th>
                                <th>Dữ Liệu Nhận</th>
                                <th>Mô tả</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td class="param-name">new_alert</td>
                                <td class="param-type">Object (Alert)</td>
                                <td>Được bắn tự động từ Backend ngay khi có một cuộc xâm nhập mới lưu vào DB (độ trễ &lt; 0.1s).</td>
                            </tr>
                            <tr>
                                <td class="param-name">alert_status_updated</td>
                                <td class="param-type">Object (Status)</td>
                                <td>Được bắn khi một quản trị viên khác bấm nút Xác nhận Đã Xử Lý. Giúp đồng bộ giao diện SOC ngay lập tức.</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>

        </div>
    </body>
    </html>
    """
    return render_template_string(html_content)

