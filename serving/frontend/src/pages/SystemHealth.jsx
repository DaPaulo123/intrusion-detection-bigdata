import React, { useEffect } from 'react';
import { Server, Cpu, CheckCircle2, XCircle, BrainCircuit } from 'lucide-react';
import useSystemStore from '../store/useSystemStore';

const SystemHealth = () => {
  const { systemHealth, modelMetrics, isLoading, fetchData } = useSystemStore();

  useEffect(() => {
    if (!systemHealth || !modelMetrics) {
      fetchData();
    }
  }, [systemHealth, modelMetrics, fetchData]);

  if (isLoading || !systemHealth || !modelMetrics) {
    return (
      <div className="flex-center h-full text-gray-400 flex-col gap-4">
        <div className="w-8 h-8 border-2 border-accent-primary border-t-transparent rounded-full animate-spin"></div>
        <p>Scanning Infrastructure Health...</p>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-8 animate-fade-in pb-8">
      
      {/* Infrastructure Nodes Section */}
      <section>
        <div className="flex items-center gap-3 mb-6">
          <Server className="text-accent-primary" size={24} />
          <h2 className="text-2xl font-bold text-gray-100 m-0">Infrastructure Nodes</h2>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {systemHealth.services.map((service, idx) => (
            <div key={idx} className="glass-panel p-5 flex flex-col relative overflow-hidden group">
              <div className={`absolute top-0 left-0 w-1 h-full ${service.status === 'running' ? 'bg-status-low' : 'bg-status-critical'}`}></div>
              
              <div className="flex justify-between items-start mb-4">
                <div className="flex items-center gap-3">
                  <div className="p-2.5 rounded-lg bg-white/5 border border-white/5">
                    <Cpu size={20} className="text-gray-300" />
                  </div>
                  <div>
                    <h3 className="text-gray-100 font-semibold text-lg uppercase tracking-wide">{service.name}</h3>
                    <p className="text-xs text-gray-400 font-mono mt-1">Node ID: {Math.random().toString(36).substr(2, 6).toUpperCase()}</p>
                  </div>
                </div>
                
                {service.status === 'running' ? (
                  <CheckCircle2 size={24} className="text-status-low" />
                ) : (
                  <XCircle size={24} className="text-status-critical" />
                )}
              </div>
              
              <div className="mt-auto grid grid-cols-2 gap-4 border-t border-white/5 pt-4">
                <div>
                  <p className="text-xs text-gray-500 uppercase font-semibold mb-1">Status</p>
                  <p className={`text-sm font-semibold capitalize ${service.status === 'running' ? 'text-status-low' : 'text-status-critical'}`}>
                    {service.status}
                  </p>
                </div>
                <div>
                  <p className="text-xs text-gray-500 uppercase font-semibold mb-1">Uptime</p>
                  <p className="text-sm font-mono text-gray-300">{service.uptime}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Machine Learning Model Performance Section */}
      <section className="mt-4">
        <div className="flex items-center gap-3 mb-6">
          <BrainCircuit className="text-purple-400" size={24} />
          <h2 className="text-2xl font-bold text-gray-100 m-0">Model Performance Metrics</h2>
        </div>
        
        <div className="glass-panel p-8 grid grid-cols-2 md:grid-cols-4 gap-8">
          
          <div className="flex flex-col items-center justify-center text-center p-4 rounded-xl bg-black/20 border border-white/5">
            <div className="relative mb-4">
              <svg className="w-24 h-24 transform -rotate-90">
                <circle cx="48" cy="48" r="40" stroke="currentColor" strokeWidth="6" fill="transparent" className="text-gray-700" />
                <circle cx="48" cy="48" r="40" stroke="currentColor" strokeWidth="6" fill="transparent" 
                  strokeDasharray={251.2} 
                  strokeDashoffset={251.2 - (251.2 * modelMetrics.accuracy)} 
                  className="text-green-400 transition-all duration-1000" 
                />
              </svg>
              <div className="absolute inset-0 flex items-center justify-center">
                <span className="text-xl font-bold text-gray-100">{(modelMetrics.accuracy * 100).toFixed(1)}%</span>
              </div>
            </div>
            <h4 className="text-sm uppercase tracking-wider text-gray-400 font-semibold">Accuracy</h4>
          </div>

          <div className="flex flex-col items-center justify-center text-center p-4 rounded-xl bg-black/20 border border-white/5">
            <div className="relative mb-4">
              <svg className="w-24 h-24 transform -rotate-90">
                <circle cx="48" cy="48" r="40" stroke="currentColor" strokeWidth="6" fill="transparent" className="text-gray-700" />
                <circle cx="48" cy="48" r="40" stroke="currentColor" strokeWidth="6" fill="transparent" 
                  strokeDasharray={251.2} 
                  strokeDashoffset={251.2 - (251.2 * modelMetrics.precision)} 
                  className="text-blue-400 transition-all duration-1000" 
                />
              </svg>
              <div className="absolute inset-0 flex items-center justify-center">
                <span className="text-xl font-bold text-gray-100">{(modelMetrics.precision * 100).toFixed(1)}%</span>
              </div>
            </div>
            <h4 className="text-sm uppercase tracking-wider text-gray-400 font-semibold">Precision</h4>
          </div>

          <div className="flex flex-col items-center justify-center text-center p-4 rounded-xl bg-black/20 border border-white/5">
            <div className="relative mb-4">
              <svg className="w-24 h-24 transform -rotate-90">
                <circle cx="48" cy="48" r="40" stroke="currentColor" strokeWidth="6" fill="transparent" className="text-gray-700" />
                <circle cx="48" cy="48" r="40" stroke="currentColor" strokeWidth="6" fill="transparent" 
                  strokeDasharray={251.2} 
                  strokeDashoffset={251.2 - (251.2 * modelMetrics.recall)} 
                  className="text-purple-400 transition-all duration-1000" 
                />
              </svg>
              <div className="absolute inset-0 flex items-center justify-center">
                <span className="text-xl font-bold text-gray-100">{(modelMetrics.recall * 100).toFixed(1)}%</span>
              </div>
            </div>
            <h4 className="text-sm uppercase tracking-wider text-gray-400 font-semibold">Recall</h4>
          </div>

          <div className="flex flex-col items-center justify-center text-center p-4 rounded-xl bg-black/20 border border-white/5">
            <div className="relative mb-4">
              <svg className="w-24 h-24 transform -rotate-90">
                <circle cx="48" cy="48" r="40" stroke="currentColor" strokeWidth="6" fill="transparent" className="text-gray-700" />
                <circle cx="48" cy="48" r="40" stroke="currentColor" strokeWidth="6" fill="transparent" 
                  strokeDasharray={251.2} 
                  strokeDashoffset={251.2 - (251.2 * modelMetrics.f1_score)} 
                  className="text-yellow-400 transition-all duration-1000" 
                />
              </svg>
              <div className="absolute inset-0 flex items-center justify-center">
                <span className="text-xl font-bold text-gray-100">{(modelMetrics.f1_score * 100).toFixed(1)}%</span>
              </div>
            </div>
            <h4 className="text-sm uppercase tracking-wider text-gray-400 font-semibold">F1 Score</h4>
          </div>

        </div>
        
        <p className="text-right text-xs text-gray-500 mt-3 font-mono">
          Last Model Retraining: {new Date(modelMetrics.last_trained).toLocaleString()}
        </p>
      </section>

    </div>
  );
};

export default SystemHealth;
