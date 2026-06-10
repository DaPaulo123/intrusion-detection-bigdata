import { create } from 'zustand';
import { fetchAlerts, fetchAlertSummary, updateAlertStatus } from '../services/api';

const useAlertStore = create((set, get) => ({
  alerts: [],
  summary: null,
  isLoading: false,
  error: null,

  // Lấy dữ liệu lần đầu
  fetchInitialData: async () => {
    set({ isLoading: true });
    try {
      const [alertsData, summaryData] = await Promise.all([
        fetchAlerts(),
        fetchAlertSummary()
      ]);
      set({ alerts: alertsData, summary: summaryData, isLoading: false });
    } catch (error) {
      set({ error: error.message, isLoading: false });
    }
  },

  // Hứng dữ liệu realtime đẩy vào đầu mảng (chỉ giữ 100 record mới nhất tránh tràn RAM)
  addRealtimeAlert: (newAlert) => {
    set((state) => ({
      alerts: [newAlert, ...state.alerts].slice(0, 100)
    }));
  },

  // Cập nhật trạng thái xử lý của cảnh báo
  markAsHandled: async (id) => {
    try {
      await updateAlertStatus(id, 'handled');
      set((state) => ({
        alerts: state.alerts.map(alert => 
          alert.id === id ? { ...alert, status: 'handled', resolved_by: 'Admin SOC' } : alert
        )
      }));
    } catch (error) {
      console.error("Lỗi khi cập nhật trạng thái:", error);
    }
  }
}));

export default useAlertStore;
