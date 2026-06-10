import React, { useState, useEffect } from 'react';
import { Bell, ShieldAlert } from 'lucide-react';
import { toast } from 'react-hot-toast';
import socketService from '../services/socket';
import useAlertStore from '../store/useAlertStore';

const Header = () => {
  const [time, setTime] = useState(new Date().toLocaleTimeString());
  const [socketConnected, setSocketConnected] = useState(false);
  const [showDropdown, setShowDropdown] = useState(false);
  
  const alerts = useAlertStore(state => state.alerts);
  const pendingCount = alerts.filter(a => a.status === 'pending').length;

  const handleNotificationClick = () => {
    setShowDropdown(!showDropdown);
  };

  useEffect(() => {
    const timer = setInterval(() => {
      setTime(new Date().toLocaleTimeString());
    }, 1000);

    socketService.on('connect', () => setSocketConnected(true));
    socketService.on('disconnect', () => setSocketConnected(false));
    
    socketService.connect();

    return () => {
      clearInterval(timer);
      socketService.disconnect();
    };
  }, []);

  return (
    <header className="h-[70px] flex items-center justify-between px-6 sticky top-0 z-40 glass-panel border-b border-white/5 rounded-none">
      <div className="flex items-center gap-3">
        <ShieldAlert size={24} className="text-accent-primary" />
        <h1 className="text-lg font-semibold text-gray-100 m-0">Intrusion Detection System</h1>
      </div>
      
      <div className="flex items-center gap-6">
        <div className="flex items-center gap-2 bg-black/20 px-3 py-1.5 rounded-full border border-white/5">
          <span className={`w-2 h-2 rounded-full ${socketConnected ? 'bg-status-low shadow-[0_0_8px_#10b981] animate-pulse' : 'bg-status-critical shadow-[0_0_8px_#ef4444]'}`}></span>
          <span className="text-sm font-medium text-gray-400">{socketConnected ? 'Streaming Active' : 'Disconnected'}</span>
        </div>
        
        <div className="font-mono font-medium text-[0.95rem] text-gray-100">
          {time}
        </div>
        
        <div className="relative">
          <button 
            onClick={handleNotificationClick}
            className="relative flex items-center justify-center w-9 h-9 rounded-full bg-transparent border-none text-gray-400 hover:text-gray-100 hover:bg-white/5 transition-all duration-200 cursor-pointer"
          >
            <Bell size={20} />
            {pendingCount > 0 && (
              <span className="absolute top-1.5 right-2 w-2 h-2 rounded-full bg-status-critical border-2 border-dark-panel"></span>
            )}
          </button>

          {showDropdown && (
            <div className="absolute right-0 mt-2 w-72 bg-dark-panel border border-white/10 p-4 rounded-xl shadow-2xl origin-top-right animate-fade-in backdrop-blur-lg">
              <h3 className="text-gray-100 font-semibold mb-3 text-sm uppercase tracking-wider">Notifications</h3>
              <div className="border-t border-white/5 pt-3">
                {pendingCount > 0 ? (
                  <div className="flex items-start gap-3">
                    <ShieldAlert className="text-yellow-500 w-5 h-5 mt-0.5" />
                    <div>
                      <p className="text-sm text-gray-200">
                        <span className="text-yellow-400 font-bold">{pendingCount}</span> threats require your attention!
                      </p>
                      <p className="text-xs text-gray-400 mt-1">Please review them in the attack logs.</p>
                    </div>
                  </div>
                ) : (
                  <div className="flex items-start gap-3">
                    <ShieldAlert className="text-status-low w-5 h-5 mt-0.5" />
                    <p className="text-sm text-gray-200 mt-0.5">System is secure. No pending alerts.</p>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};

export default Header;
