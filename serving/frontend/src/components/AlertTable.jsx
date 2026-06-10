import React from 'react';
import { CheckCircle2, AlertTriangle, ShieldCheck } from 'lucide-react';

const AlertTable = ({ alerts, markAsHandled }) => {
  return (
    <div className="glass-panel overflow-hidden flex flex-col h-[450px]">
      <div className="p-5 border-b border-white/5 flex justify-between items-center bg-black/10">
        <h3 className="text-gray-100 font-semibold text-lg flex items-center gap-2">
          <AlertTriangle size={20} className="text-accent-primary" />
          Real-time Attack Logs
        </h3>
        <span className="text-xs font-semibold bg-blue-500/10 text-blue-400 px-3 py-1.5 rounded-full border border-blue-500/20">
          Showing latest {alerts.length} records
        </span>
      </div>
      
      <div className="overflow-x-auto flex-1 custom-scrollbar">
        <table className="w-full text-left border-collapse whitespace-nowrap">
          <thead className="sticky top-0 bg-dark-panel z-10 backdrop-blur-md">
            <tr className="text-gray-400 text-[0.8rem] uppercase tracking-wider border-b border-white/5">
              <th className="p-4 font-semibold">Time</th>
              <th className="p-4 font-semibold">Source IP</th>
              <th className="p-4 font-semibold">Destination IP</th>
              <th className="p-4 font-semibold">Attack Type</th>
              <th className="p-4 font-semibold w-40">Threat Score</th>
              <th className="p-4 font-semibold text-center">Status</th>
              <th className="p-4 font-semibold text-right pr-6 sticky right-0 bg-[#0b0f19] shadow-[-10px_0_15px_-5px_rgba(0,0,0,0.3)] z-20">Action</th>
            </tr>
          </thead>
          <tbody>
            {alerts.map((alert) => (
              <tr key={alert.id} className="border-b border-white/5 hover:bg-white/5 transition-colors group">
                <td className="p-4 text-sm text-gray-300 font-mono">
                  {new Date(alert.timestamp).toLocaleTimeString()}
                </td>
                <td className="p-4 text-sm text-gray-300 font-mono">{alert.srcip}</td>
                <td className="p-4 text-sm text-gray-300 font-mono">{alert.dstip}</td>
                <td className="p-4 text-sm">
                  <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-red-500/10 text-red-400 border border-red-500/20 font-medium text-xs">
                    <AlertTriangle size={12} />
                    {alert.attack_cat}
                  </span>
                </td>
                <td className="p-4 text-sm">
                  <div className="flex items-center gap-3">
                    <span className={`font-mono font-bold w-6 ${alert.threat_score >= 80 ? 'text-red-400' : alert.threat_score >= 50 ? 'text-yellow-400' : 'text-green-400'}`}>
                      {alert.threat_score}
                    </span>
                    <div className="w-full bg-black/40 rounded-full h-1.5 border border-white/5">
                      <div 
                        className={`h-1.5 rounded-full ${alert.threat_score >= 80 ? 'bg-red-500 shadow-[0_0_8px_#ef4444]' : alert.threat_score >= 50 ? 'bg-yellow-500 shadow-[0_0_8px_#eab308]' : 'bg-green-500'}`} 
                        style={{ width: `${alert.threat_score}%` }}
                      ></div>
                    </div>
                  </div>
                </td>
                <td className="p-4 text-sm text-center">
                  {alert.status === 'pending' ? (
                    <span className="text-yellow-400 font-semibold text-[10px] uppercase bg-yellow-400/10 px-2.5 py-1 rounded border border-yellow-400/20 tracking-wider">Pending</span>
                  ) : (
                    <span className="text-green-400 font-semibold text-[10px] uppercase bg-green-400/10 px-2.5 py-1 rounded border border-green-400/20 tracking-wider">Handled</span>
                  )}
                </td>
                <td className="p-4 text-sm text-right pr-6 sticky right-0 bg-[#0b0f19] group-hover:bg-[#161d2d] shadow-[-10px_0_15px_-5px_rgba(0,0,0,0.3)] z-10 transition-colors">
                  {alert.status === 'pending' ? (
                    <button 
                      onClick={() => markAsHandled(alert.id)}
                      className="inline-flex items-center gap-1.5 bg-accent-primary hover:bg-accent-hover text-white px-3 py-1.5 rounded text-xs font-semibold transition-all shadow-lg hover:shadow-accent-primary/30"
                    >
                      <CheckCircle2 size={14} /> Handle
                    </button>
                  ) : (
                    <span className="inline-flex items-center gap-1.5 text-green-500 text-xs font-medium">
                      <ShieldCheck size={14} /> by {alert.resolved_by}
                    </span>
                  )}
                </td>
              </tr>
            ))}
            {alerts.length === 0 && (
              <tr>
                <td colSpan="7" className="p-12 text-center text-gray-500 flex flex-col items-center gap-3">
                  <div className="w-8 h-8 border-2 border-accent-primary border-t-transparent rounded-full animate-spin"></div>
                  Waiting for incoming streams...
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default AlertTable;
