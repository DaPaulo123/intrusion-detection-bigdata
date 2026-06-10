import { create } from 'zustand';
import { fetchBatchStats, fetchSystemHealth, fetchModelMetrics } from '../services/api';

const useSystemStore = create((set) => ({
  batchStats: null,
  systemHealth: null,
  modelMetrics: null,
  isLoading: false,

  fetchData: async () => {
    set({ isLoading: true });
    try {
      const [batchRes, healthRes, metricsRes] = await Promise.all([
        fetchBatchStats(),
        fetchSystemHealth(),
        fetchModelMetrics()
      ]);
      // API trả về {status, data} — cần extract .data
      set({ 
        batchStats: batchRes.data || null, 
        systemHealth: healthRes.data || null, 
        modelMetrics: metricsRes.data || null, 
        isLoading: false 
      });
    } catch (error) {
      console.error("Lỗi khi tải thông tin hệ thống:", error);
      set({ isLoading: false });
    }
  }
}));

export default useSystemStore;
