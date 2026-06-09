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
      const [batch, health, metrics] = await Promise.all([
        fetchBatchStats(),
        fetchSystemHealth(),
        fetchModelMetrics()
      ]);
      set({ 
        batchStats: batch, 
        systemHealth: health, 
        modelMetrics: metrics, 
        isLoading: false 
      });
    } catch (error) {
      console.error("Lỗi khi tải thông tin hệ thống:", error);
      set({ isLoading: false });
    }
  }
}));

export default useSystemStore;
