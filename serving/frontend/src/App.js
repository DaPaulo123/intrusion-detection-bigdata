import React, { useEffect } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Toaster, toast } from 'react-hot-toast';
import { ShieldAlert } from 'lucide-react';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import BatchAnalytics from './pages/BatchAnalytics';
import SystemHealth from './pages/SystemHealth';
import useAlertStore from './store/useAlertStore';
import socketService from './services/socket';

function App() {
  const fetchInitialData = useAlertStore(state => state.fetchInitialData);
  const addRealtimeAlert = useAlertStore(state => state.addRealtimeAlert);

  useEffect(() => {
    // Tải dữ liệu ban đầu
    fetchInitialData();

    // Lắng nghe Socket
    socketService.on('new_alert', (newAlert) => {
      addRealtimeAlert(newAlert);
      
      // Bắn pop-up cảnh báo đỏ khi có tấn công
      toast.custom((t) => (
        <div className={`${t.visible ? 'animate-enter' : 'animate-leave'} max-w-sm w-full bg-[#111827]/90 border border-white/5 border-l-4 border-l-red-500 shadow-lg backdrop-blur-md rounded-lg pointer-events-auto flex`}>
          <div className="flex-1 w-0 p-4">
            <div className="flex items-start">
              <div className="flex-shrink-0 pt-0.5">
                <ShieldAlert className="h-5 w-5 text-red-500" />
              </div>
              <div className="ml-3 flex-1">
                <p className="text-sm font-medium text-gray-100">
                  Threat Detected: <span className="text-red-400 font-semibold">{newAlert.attack_cat}</span>
                </p>
                <p className="mt-1 text-xs text-gray-400 font-mono">
                  Source IP: {newAlert.srcip}
                </p>
              </div>
            </div>
          </div>
        </div>
      ), { duration: 4000, position: 'bottom-right' });
    });

  }, [fetchInitialData, addRealtimeAlert]);

  return (
    <>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Layout />}>
            <Route index element={<Dashboard />} />
            <Route path="batch" element={<BatchAnalytics />} />
            <Route path="system" element={<SystemHealth />} />
          </Route>
        </Routes>
      </BrowserRouter>
      
      <Toaster />
    </>
  );
}

export default App;
