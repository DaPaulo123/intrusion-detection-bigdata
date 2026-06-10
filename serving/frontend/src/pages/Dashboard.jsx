import React, { useMemo } from 'react';
import { ShieldAlert, Activity, CheckCircle2 } from 'lucide-react';
import useAlertStore from '../store/useAlertStore';
import MetricCard from '../components/MetricCard';
import PieChartAlerts from '../components/charts/PieChartAlerts';
import AlertTable from '../components/AlertTable';

const Dashboard = () => {
  const { alerts, summary, isLoading, markAsHandled } = useAlertStore();

  // Tính toán dữ liệu thống kê từ alerts realtime & summary backend
  const stats = useMemo(() => {
    // Nếu có summary từ backend, ưu tiên hiển thị số thực tế
    const total = summary ? Object.values(summary.category_summary || {}).reduce((a, b) => a + b, 0) : alerts.length;
    const pending = summary ? summary.pending_alerts_count : alerts.filter(a => a.status === 'pending').length;
    const handled = total - pending;
    
    // Phân nhóm theo loại tấn công (Khởi tạo sẵn 10 nhóm để luôn hiện đủ Legend)
    const categoryCount = {
      "Normal": 0, "Analysis": 0, "Backdoor": 0, "DoS": 0, "Exploits": 0, 
      "Fuzzers": 0, "Generic": 0, "Reconnaissance": 0, "Shellcode": 0, "Worms": 0
    };

    if (summary && summary.category_summary) {
      Object.keys(summary.category_summary).forEach(key => {
        categoryCount[key] = summary.category_summary[key];
      });
    } else {
      alerts.forEach(a => {
        if (categoryCount[a.attack_cat] !== undefined) {
          categoryCount[a.attack_cat]++;
        } else {
          categoryCount[a.attack_cat] = 1;
        }
      });
    }
    
    const pieData = Object.keys(categoryCount).map(key => ({
      name: key,
      value: categoryCount[key]
    })).sort((a, b) => b.value - a.value);

    return { total, pending, handled, pieData };
  }, [alerts, summary]);

  if (isLoading && alerts.length === 0) {
    return (
      <div className="flex-center h-full text-gray-400 flex-col gap-4">
        <div className="w-8 h-8 border-2 border-accent-primary border-t-transparent rounded-full animate-spin"></div>
        <p>Initializing SOC Dashboard...</p>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-6 animate-fade-in pb-8">
      {/* Top row: Metric Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <MetricCard 
          title="Total Threats Detected" 
          value={stats.total} 
          icon={<ShieldAlert size={28} />}
          colorClass="text-blue-400"
        />
        <MetricCard 
          title="Pending Alerts" 
          value={stats.pending} 
          icon={<Activity size={28} />}
          colorClass="text-red-400"
          highlight={stats.pending > 0}
        />
        <MetricCard 
          title="Threats Handled" 
          value={stats.handled} 
          icon={<CheckCircle2 size={28} />}
          colorClass="text-green-400"
        />
      </div>

      {/* Middle/Bottom Layout */}
      <div className="grid grid-cols-1 xl:grid-cols-4 gap-6">
        <div className="xl:col-span-1">
          <PieChartAlerts data={stats.pieData} />
        </div>
        <div className="xl:col-span-3 overflow-hidden">
          <AlertTable alerts={alerts} markAsHandled={markAsHandled} />
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
