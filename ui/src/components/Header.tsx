import React from 'react';
import { Bars3Icon, BellIcon, CogIcon } from '@heroicons/react/24/outline';
import { useWebSocket } from '../contexts/WebSocketContext';
import type { ViewType } from '../App';

interface HeaderProps {
  currentView: ViewType;
  onToggleSidebar: () => void;
}

export const Header: React.FC<HeaderProps> = ({ currentView, onToggleSidebar }) => {
  const { isConnected, nodes, systemStats } = useWebSocket();

  const getViewTitle = (view: ViewType): string => {
    switch (view) {
      case 'dashboard':
        return 'Intelligence Dashboard';
      case 'nodes':
        return 'Node Network';
      case 'memory':
        return 'Distributed Memory';
      case 'missions':
        return 'Mission Control';
      case 'settings':
        return 'System Settings';
      default:
        return 'NIS HUB';
    }
  };

  const activeNodes = nodes.filter(node => node.status === 'online').length;

  return (
    <header className="bg-slate-800/50 backdrop-blur-sm border-b border-slate-700/50 px-6 py-4">
      <div className="flex items-center justify-between">
        {/* Left Side */}
        <div className="flex items-center space-x-4">
          <button
            onClick={onToggleSidebar}
            className="p-2 rounded-lg hover:bg-slate-700/50 transition-colors"
          >
            <Bars3Icon className="h-5 w-5 text-slate-300" />
          </button>
          
          <div className="flex items-center space-x-3">
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-gradient-to-br from-nis-blue-500 to-nis-purple-500 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-sm">N</span>
              </div>
              <div>
                <h1 className="text-xl font-bold text-white">
                  NIS HUB
                </h1>
                <p className="text-xs text-slate-400 -mt-1">
                  Neural Intelligence System
                </p>
              </div>
            </div>
            
            <div className="hidden md:block w-px h-8 bg-slate-600"></div>
            
            <div className="hidden md:block">
              <h2 className="text-lg font-semibold text-slate-200">
                {getViewTitle(currentView)}
              </h2>
            </div>
          </div>
        </div>

        {/* Right Side */}
        <div className="flex items-center space-x-4">
          {/* Connection Status */}
          <div className="flex items-center space-x-2">
            <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-emerald-400 animate-pulse-slow' : 'bg-red-400'}`}></div>
            <span className="text-sm text-slate-300">
              {isConnected ? 'Connected' : 'Disconnected'}
            </span>
          </div>

          {/* Active Nodes */}
          <div className="hidden lg:flex items-center space-x-2 bg-slate-700/50 rounded-lg px-3 py-1">
            <div className="w-2 h-2 bg-emerald-400 rounded-full"></div>
            <span className="text-sm text-slate-300">
              {activeNodes}/{nodes.length} Nodes
            </span>
          </div>

          {/* System Stats */}
          {systemStats.messages_per_second !== undefined && (
            <div className="hidden xl:flex items-center space-x-2 bg-slate-700/50 rounded-lg px-3 py-1">
              <span className="text-sm text-slate-300">
                {systemStats.messages_per_second.toFixed(1)} msg/s
              </span>
            </div>
          )}

          {/* Notifications */}
          <button className="relative p-2 rounded-lg hover:bg-slate-700/50 transition-colors">
            <BellIcon className="h-5 w-5 text-slate-300" />
            <div className="absolute -top-1 -right-1 w-3 h-3 bg-nis-blue-500 rounded-full"></div>
          </button>

          {/* Settings */}
          <button className="p-2 rounded-lg hover:bg-slate-700/50 transition-colors">
            <CogIcon className="h-5 w-5 text-slate-300" />
          </button>
        </div>
      </div>
    </header>
  );
}; 