import React from 'react';
import {
  HomeIcon,
  ServerIcon,
  CircleStackIcon,
  RocketLaunchIcon,
  CogIcon,
  ChevronLeftIcon,
  ChevronRightIcon,
} from '@heroicons/react/24/outline';
import type { ViewType } from '../App';

interface SidebarProps {
  currentView: ViewType;
  onViewChange: (view: ViewType) => void;
  collapsed: boolean;
  onToggleCollapse: () => void;
}

interface MenuItem {
  id: ViewType;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
  description: string;
}

const menuItems: MenuItem[] = [
  {
    id: 'dashboard',
    label: 'Dashboard',
    icon: HomeIcon,
    description: 'System overview and metrics',
  },
  {
    id: 'nodes',
    label: 'Nodes',
    icon: ServerIcon,
    description: 'Connected NIS nodes',
  },
  {
    id: 'memory',
    label: 'Memory',
    icon: CircleStackIcon,
    description: 'Distributed memory layer',
  },
  {
    id: 'missions',
    label: 'Missions',
    icon: RocketLaunchIcon,
    description: 'Active coordination tasks',
  },
  {
    id: 'settings',
    label: 'Settings',
    icon: CogIcon,
    description: 'System configuration',
  },
];

export const Sidebar: React.FC<SidebarProps> = ({
  currentView,
  onViewChange,
  collapsed,
  onToggleCollapse,
}) => {
  return (
    <div
      className={`bg-slate-900/50 backdrop-blur-sm border-r border-slate-700/50 transition-all duration-300 ${
        collapsed ? 'w-16' : 'w-64'
      }`}
    >
      {/* Sidebar Header */}
      <div className="p-4 border-b border-slate-700/50">
        <div className="flex items-center justify-between">
          {!collapsed && (
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-gradient-to-br from-nis-blue-500 to-nis-purple-500 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-sm">N</span>
              </div>
              <div>
                <h3 className="text-sm font-semibold text-white">NIS HUB</h3>
                <p className="text-xs text-slate-400">v1.0.0</p>
              </div>
            </div>
          )}
          
          <button
            onClick={onToggleCollapse}
            className="p-1 rounded hover:bg-slate-700/50 transition-colors"
          >
            {collapsed ? (
              <ChevronRightIcon className="h-4 w-4 text-slate-400" />
            ) : (
              <ChevronLeftIcon className="h-4 w-4 text-slate-400" />
            )}
          </button>
        </div>
      </div>

      {/* Navigation Menu */}
      <nav className="p-4 space-y-2">
        {menuItems.map((item) => {
          const Icon = item.icon;
          const isActive = currentView === item.id;
          
          return (
            <button
              key={item.id}
              onClick={() => onViewChange(item.id)}
              className={`w-full flex items-center space-x-3 px-3 py-2 rounded-lg transition-colors ${
                isActive
                  ? 'bg-nis-blue-600/20 border border-nis-blue-500/30 text-nis-blue-300'
                  : 'hover:bg-slate-700/50 text-slate-300 hover:text-white'
              }`}
              title={collapsed ? item.label : undefined}
            >
              <Icon className="h-5 w-5 flex-shrink-0" />
              {!collapsed && (
                <div className="flex-1 text-left">
                  <div className="text-sm font-medium">{item.label}</div>
                  <div className="text-xs text-slate-400">{item.description}</div>
                </div>
              )}
            </button>
          );
        })}
      </nav>

      {/* System Status */}
      {!collapsed && (
        <div className="absolute bottom-4 left-4 right-4">
          <div className="bg-slate-800/50 rounded-lg p-3 border border-slate-700/50">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-medium text-slate-300">System Status</span>
              <div className="w-2 h-2 bg-emerald-400 rounded-full animate-pulse-slow"></div>
            </div>
            <div className="text-xs text-slate-400 space-y-1">
              <div className="flex justify-between">
                <span>CPU</span>
                <span>24%</span>
              </div>
              <div className="flex justify-between">
                <span>Memory</span>
                <span>1.2GB</span>
              </div>
              <div className="flex justify-between">
                <span>Uptime</span>
                <span>2d 4h</span>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}; 