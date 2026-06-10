import { 
  MOCK_ALERTS, 
  MOCK_SUMMARY, 
  MOCK_BATCH_STATS, 
  MOCK_SYSTEM_HEALTH, 
  MOCK_MODEL_METRICS 
} from './mockData';

// Biến cờ (flag) để chuyển đổi giữa việc gọi API thật và dùng Mock Data
// Tạm thời bật USE_MOCK = true theo yêu cầu
const USE_MOCK = true;

// Tạo delay giả lập thời gian phản hồi của mạng (ví dụ 300ms)
const delay = (ms) => new Promise(resolve => setTimeout(resolve, ms));

export const fetchAlerts = async () => {
  if (USE_MOCK) {
    await delay(300);
    return MOCK_ALERTS;
  }
  // Code gọi API thật bằng axios sau này sẽ để ở đây
  // const response = await axios.get('/api/alerts');
  // return response.data.data;
};

export const fetchAlertSummary = async () => {
  if (USE_MOCK) {
    await delay(300);
    return MOCK_SUMMARY;
  }
};

export const updateAlertStatus = async (id, newStatus) => {
  if (USE_MOCK) {
    await delay(500); // Giả lập thời gian update
    return { success: true, id, status: newStatus };
  }
};

export const fetchBatchStats = async () => {
  if (USE_MOCK) {
    await delay(400);
    return MOCK_BATCH_STATS;
  }
};

export const fetchSystemHealth = async () => {
  if (USE_MOCK) {
    await delay(200);
    return MOCK_SYSTEM_HEALTH;
  }
};

export const fetchModelMetrics = async () => {
  if (USE_MOCK) {
    await delay(200);
    return MOCK_MODEL_METRICS;
  }
};
