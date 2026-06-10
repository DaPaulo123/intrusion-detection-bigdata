import React from 'react';
import { NavLink } from 'react-router-dom';
import { Activity, BarChart3, Server } from 'lucide-react';

const Sidebar = () => {
  const navItems = [
    { path: '/', name: 'Streaming', icon: <Activity size={20} /> },
    { path: '/batch', name: 'Batch Analytics', icon: <BarChart3 size={20} /> },
    { path: '/system', name: 'System Health', icon: <Server size={20} /> }
  ];

  return (
    <aside className="fixed left-0 top-0 w-[220px] h-screen flex flex-col z-50 glass-panel border-r border-white/5 rounded-none">
      <div className="p-6 border-b border-white/5 mb-5">
        <h2 className="text-accent-primary text-xl font-bold tracking-wide uppercase">
          SOC Dashboard
        </h2>
      </div>
      <nav className="flex flex-col px-3 gap-2">
        {navItems.map((item) => (
          <NavLink 
            key={item.path} 
            to={item.path} 
            className={({ isActive }) => 
              `flex items-center gap-3 px-4 py-3 rounded-lg font-medium transition-all duration-200 ${
                isActive 
                  ? 'bg-blue-500/15 text-accent-primary border-l-4 border-accent-primary' 
                  : 'text-gray-400 hover:bg-dark-hover hover:text-gray-100'
              }`
            }
          >
            {item.icon}
            <span>{item.name}</span>
          </NavLink>
        ))}
      </nav>
    </aside>
  );
};

export default Sidebar;
