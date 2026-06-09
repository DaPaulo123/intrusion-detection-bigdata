import React, { useEffect } from 'react';
import { 
  LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer 
} from 'recharts';
import { Database, TrendingUp, AlertOctagon } from 'lucide-react';
import useSystemStore from '../store/useSystemStore';
import MetricCard from '../components/MetricCard';

const BatchAnalytics = () => {
  const { batchStats, isLoading, fetchData } = useSystemStore();

  useEffect(() => {
    if (!batchStats) {
      fetchData();
    }
  }, [batchStats, fetchData]);

  if (isLoading || !batchStats) {
    return (
      <div className="flex-center h-full text-gray-400 flex-col gap-4">
        <div className="w-8 h-8 border-2 border-accent-primary border-t-transparent rounded-full animate-spin"></div>
        <p>Analyzing Batch Storage...</p>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-6 animate-fade-in pb-8">
      <div className="flex items-center gap-3 mb-2">
        <Database className="text-accent-primary" size={24} />
        <h2 className="text-2xl font-bold text-gray-100 m-0">Historical Batch Analytics</h2>
      </div>

      {/* Top Metric */}
      <div className="grid grid-cols-1 gap-6">
        <MetricCard 
          title="Total Records Processed (HDFS)" 
          value={new Intl.NumberFormat().format(batchStats.total_records_processed)} 
          icon={<Database size={28} />}
          colorClass="text-purple-400"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Peak Hours Line Chart */}
        <div className="glass-panel p-5 h-[400px] flex flex-col">
          <h3 className="text-gray-100 font-semibold mb-4 text-lg flex items-center gap-2">
            <TrendingUp size={20} className="text-blue-400" />
            24h Attack Volume (Peak Hours)
          </h3>
          <div className="flex-1 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={batchStats.peak_hours} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
                <XAxis 
                  dataKey="hour" 
                  stroke="#9ca3af" 
                  tickFormatter={(val) => `${val}h`} 
                  axisLine={false}
                  tickLine={false}
                />
                <YAxis stroke="#9ca3af" axisLine={false} tickLine={false} />
                <Tooltip 
                  contentStyle={{ backgroundColor: 'rgba(17, 24, 39, 0.95)', borderColor: 'rgba(255,255,255,0.1)', borderRadius: '8px' }}
                  labelFormatter={(val) => `Hour: ${val}:00`}
                />
                <Line 
                  type="monotone" 
                  dataKey="attack_count" 
                  stroke="#3b82f6" 
                  strokeWidth={3} 
                  dot={{ r: 4, fill: '#1e3a8a', stroke: '#3b82f6', strokeWidth: 2 }}
                  activeDot={{ r: 6, fill: '#60a5fa', stroke: '#fff' }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Threat Score Distribution Bar Chart */}
        <div className="glass-panel p-5 h-[400px] flex flex-col">
          <h3 className="text-gray-100 font-semibold mb-4 text-lg flex items-center gap-2">
            <AlertOctagon size={20} className="text-red-400" />
            Threat Score Distribution
          </h3>
          <div className="flex-1 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={batchStats.threat_score_distribution} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
                <XAxis 
                  dataKey="range" 
                  stroke="#9ca3af" 
                  axisLine={false}
                  tickLine={false}
                />
                <YAxis stroke="#9ca3af" axisLine={false} tickLine={false} />
                <Tooltip 
                  contentStyle={{ backgroundColor: 'rgba(17, 24, 39, 0.95)', borderColor: 'rgba(255,255,255,0.1)', borderRadius: '8px' }}
                  cursor={{ fill: 'rgba(255,255,255,0.05)' }}
                />
                <Bar 
                  dataKey="count" 
                  fill="#ef4444" 
                  radius={[4, 4, 0, 0]}
                  barSize={40}
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
};

export default BatchAnalytics;
