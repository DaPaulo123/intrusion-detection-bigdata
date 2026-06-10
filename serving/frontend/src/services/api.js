import axios from 'axios';

// ─── Cấu hình ──────────────────────────────────────────────────────────────
const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';
const API_KEY = process.env.REACT_APP_API_KEY || 'SOC-Super-Secret-2026';

const api = axios.create({
  baseURL: API_BASE,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
    'X-API-Key': API_KEY,
  },
});

// ─── Interceptor xử lý lỗi chung ──────────────────────────────────────────
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      console.error(`[API Error] ${error.response.status}: ${error.response.data?.message || 'Unknown error'}`);
    } else if (error.request) {
      console.error('[API Error] Không thể kết nối tới Backend. Server có đang chạy không?');
    }
    return Promise.reject(error);
  }
);

// ─── API Functions ─────────────────────────────────────────────────────────

/**
 * Lấy danh sách alerts (có phân trang)
 * @param {number} page - Trang hiện tại
 * @param {number} limit - Số bản ghi/trang
 * @param {string} [status] - Lọc theo trạng thái ('pending' | 'handled')
 */
export const fetchAlerts = async (page = 1, limit = 20, status = null) => {
  const params = { page, limit };
  if (status) params.status = status;
  const response = await api.get('/alerts', { params });
  return response.data;
};

/**
 * Lấy thống kê tổng quan alerts (category, recent 10m, pending count)
 */
export const fetchAlertSummary = async () => {
  const response = await api.get('/alerts/summary');
  return response.data;
};

/**
 * Cập nhật trạng thái xử lý của một alert
 * @param {string} id - Alert ID
 * @param {string} newStatus - 'pending' | 'handled'
 * @param {string} resolvedBy - Tên người xử lý
 */
export const updateAlertStatus = async (id, newStatus, resolvedBy = 'Admin SOC') => {
  const response = await api.put(`/alerts/${id}/status`, {
    status: newStatus,
    resolved_by: resolvedBy,
  });
  return response.data;
};

/**
 * Lấy thống kê Batch Processing (peak hours, threat distribution, ...)
 */
export const fetchBatchStats = async () => {
  const response = await api.get('/batch/stats');
  return response.data;
};

/**
 * Lấy trạng thái các Docker containers
 */
export const fetchSystemHealth = async () => {
  const response = await api.get('/system/health');
  return response.data;
};

/**
 * Lấy chỉ số hiệu năng mô hình ML (accuracy, f1, ...)
 */
export const fetchModelMetrics = async () => {
  const response = await api.get('/system/model-metrics');
  return response.data;
};

/**
 * Lấy trạng thái load model (model có sẵn sàng chưa)
 */
export const fetchModelStatus = async () => {
  const response = await api.get('/model/status');
  return response.data;
};

/**
 * Kiểm tra backend đang sống hay không
 */
export const fetchHealth = async () => {
  const response = await api.get('/health');
  return response.data;
};

export default api;
