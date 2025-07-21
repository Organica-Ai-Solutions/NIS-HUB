import React from 'react';
import {
  ServerIcon,
  CircleStackIcon,
  RocketLaunchIcon,
  ClockIcon,
  ArrowTrendingUpIcon,
  ExclamationTriangleIcon,
} from '@heroicons/react/24/outline';
import { useWebSocket } from '../contexts/WebSocketContext';
import { ActivityFeed } from './ActivityFeed';
import { MetricsChart } from './MetricsChart';
import { NodesOverview } from './NodesOverview';

export const Dashboard: React.FC = () => {
  const { nodes, memoryEntries, missions, systemStats, isConnected } = useWebSocket();

  const activeNodes = nodes.filter(node => node.status === 'online').length;
  const activeMissions = missions.filter(mission => mission.status === 'active').length;
  const totalMemoryEntries = memoryEntries.length;

  const stats = [
    {
      label: 'Active Nodes',
      value: `${activeNodes}/${nodes.length}`,
      icon: ServerIcon,
      color: 'bg-emerald-500',
      change: '+12%',
      trend: 'up',
    },
    {
      label: 'Memory Entries',
      value: totalMemoryEntries.toLocaleString(),
      icon: CircleStackIcon,
      color: 'bg-nis-blue-500',
      change: '+24%',
      trend: 'up',
    },
    {
      label: 'Active Missions',
      value: activeMissions,
      icon: RocketLaunchIcon,
      color: 'bg-nis-purple-500',
      change: '+8%',
      trend: 'up',
    },
    {
      label: 'Uptime',
      value: '99.98%',
      icon: ClockIcon,
      color: 'bg-amber-500',
      change: '+0.02%',
      trend: 'up',
    },
  ];

  const criticalAlerts = [
    {
      id: '1',
      type: 'warning',
      message: 'Node NIS-X-Exoplanet memory usage at 85%',
      timestamp: '2 minutes ago',
    },
    {
      id: '2',
      type: 'info',
      message: 'Mission Mars-Surface-Analysis completed successfully',
      timestamp: '15 minutes ago',
    },
  ];

  return (
    <div className="space-y-6">
      {/* Connection Status Banner */}
      {!isConnected && (
        <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-4">
          <div className="flex items-center space-x-2">
            <ExclamationTriangleIcon className="h-5 w-5 text-red-400" />
            <span className="text-red-300 font-medium">
              Disconnected from NIS HUB - Attempting to reconnect...
            </span>
          </div>
        </div>
      )}

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat) => {
          const Icon = stat.icon;
          return (
            <div key={stat.label} className="card">
              <div className="card-content">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-slate-400 mb-1">{stat.label}</p>
                    <p className="text-2xl font-bold text-white">{stat.value}</p>
                    <div className="flex items-center space-x-1 mt-1">
                      <ArrowTrendingUpIcon className="h-3 w-3 text-emerald-400" />
                      <span className="text-xs text-emerald-400">{stat.change}</span>
                    </div>
                  </div>
                  <div className={`w-12 h-12 ${stat.color} rounded-lg flex items-center justify-center`}>
                    <Icon className="h-6 w-6 text-white" />
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Nodes Overview */}
        <div className="lg:col-span-2 card">
          <div className="card-header">
            <h3 className="text-lg font-semibold text-white">Node Network Status</h3>
            <p className="text-sm text-slate-400">Real-time overview of connected NIS nodes</p>
          </div>
          <div className="card-content">
            <NodesOverview nodes={nodes.slice(0, 5)} />
          </div>
        </div>

        {/* Activity Feed */}
        <div className="card">
          <div className="card-header">
            <h3 className="text-lg font-semibold text-white">Live Activity</h3>
            <p className="text-sm text-slate-400">Real-time system events</p>
          </div>
          <div className="card-content">
            <ActivityFeed />
          </div>
        </div>
      </div>

      {/* Charts and Analytics */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* System Metrics */}
        <div className="card">
          <div className="card-header">
            <h3 className="text-lg font-semibold text-white">System Metrics</h3>
            <p className="text-sm text-slate-400">Performance over time</p>
          </div>
          <div className="card-content">
            <MetricsChart />
          </div>
        </div>

        {/* Mission Status */}
        <div className="card">
          <div className="card-header">
            <h3 className="text-lg font-semibold text-white">Mission Status</h3>
            <p className="text-sm text-slate-400">Active coordination tasks</p>
          </div>
          <div className="card-content">
            <div className="space-y-4">
              {missions.slice(0, 4).map((mission) => (
                <div key={mission.id} className="flex items-center justify-between p-3 bg-slate-700/30 rounded-lg">
                  <div className="flex-1">
                    <h4 className="font-medium text-white">{mission.name}</h4>
                    <p className="text-sm text-slate-400">{mission.description}</p>
                    <div className="flex items-center space-x-2 mt-1">
                      <div className="w-full bg-slate-600 rounded-full h-1.5">
                        <div 
                          className="bg-nis-blue-500 h-1.5 rounded-full" 
                          style={{ width: `${mission.progress}%` }}
                        ></div>
                      </div>
                      <span className="text-xs text-slate-400">{mission.progress}%</span>
                    </div>
                  </div>
                  <div className={`status-indicator ${
                    mission.status === 'active' ? 'status-online' :
                    mission.status === 'pending' ? 'status-syncing' :
                    'status-offline'
                  }`}>
                    {mission.status}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Critical Alerts */}
      {criticalAlerts.length > 0 && (
        <div className="card">
          <div className="card-header">
            <h3 className="text-lg font-semibold text-white">Critical Alerts</h3>
            <p className="text-sm text-slate-400">System notifications requiring attention</p>
          </div>
          <div className="card-content">
            <div className="space-y-3">
              {criticalAlerts.map((alert) => (
                <div key={alert.id} className="flex items-start space-x-3 p-3 bg-slate-700/30 rounded-lg">
                  <ExclamationTriangleIcon className={`h-5 w-5 mt-0.5 ${
                    alert.type === 'warning' ? 'text-yellow-400' : 'text-nis-blue-400'
                  }`} />
                  <div className="flex-1">
                    <p className="text-sm text-white">{alert.message}</p>
                    <p className="text-xs text-slate-400 mt-1">{alert.timestamp}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}; 