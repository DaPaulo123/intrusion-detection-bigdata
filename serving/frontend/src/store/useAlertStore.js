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
      const [alertsRes, summaryRes] = await Promise.all([
        fetchAlerts(),
        fetchAlertSummary()
      ]);
      // API trả về {status, data, meta} — cần extract .data
      set({ 
        alerts: alertsRes.data || [], 
        summary: summaryRes.data || null, 
        isLoading: false 
      });
    } catch (error) {
      set({ error: error.message, isLoading: false });
    }
  },

  // Hứng dữ liệu realtime đẩy vào đầu mảng (chỉ giữ 100 record mới nhất tránh tràn RAM)
  addRealtimeAlert: (newAlert) => {
    set((state) => {
      const newAlerts = [newAlert, ...state.alerts].slice(0, 100);
      
      let newSummary = state.summary;
      if (state.summary) {
        newSummary = { ...state.summary };
        if (newAlert.status === 'pending') {
          newSummary.pending_alerts_count += 1;
        }
        // Tăng số lượng của loại tấn công tương ứng
        if (!newSummary.category_summary) {
          newSummary.category_summary = {};
        }
        const currentCount = newSummary.category_summary[newAlert.attack_cat] || 0;
        newSummary.category_summary[newAlert.attack_cat] = currentCount + 1;
      }
      
      return { alerts: newAlerts, summary: newSummary };
    });
  },

  // Cập nhật trạng thái xử lý của cảnh báo
  markAsHandled: async (id) => {
    try {
      await updateAlertStatus(id, 'handled');
      set((state) => {
        const newAlerts = state.alerts.map(alert => 
          alert.id === id ? { ...alert, status: 'handled', resolved_by: 'Admin SOC' } : alert
        );
        const newSummary = state.summary ? {
          ...state.summary,
          pending_alerts_count: Math.max(0, state.summary.pending_alerts_count - 1)
        } : null;
        return { alerts: newAlerts, summary: newSummary };
      });
    } catch (error) {
      console.error("Lỗi khi cập nhật trạng thái:", error);
    }
  }
}));

export default useAlertStore;
