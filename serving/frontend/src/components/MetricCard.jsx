import React from 'react';

const MetricCard = ({ title, value, icon, colorClass, highlight = false }) => {
  return (
    <div className={`glass-panel p-5 flex items-center justify-between relative overflow-hidden transition-all duration-300 ${highlight ? 'border-red-500/30 bg-red-500/5' : ''}`}>
      <div className="z-10 relative">
        <p className="text-gray-400 text-sm font-medium uppercase tracking-wider mb-2">{title}</p>
        <h3 className="text-3xl font-bold text-gray-100">{value}</h3>
      </div>
      <div className={`p-4 rounded-full bg-white/5 ${colorClass}`}>
        {icon}
      </div>
      
      {/* Background Pulse Effect for Urgent Alerts */}
      {highlight && (
        <div className="absolute -right-10 -top-10 w-32 h-32 bg-red-500/20 rounded-full blur-2xl animate-pulse"></div>
      )}
    </div>
  );
};

export default MetricCard;
