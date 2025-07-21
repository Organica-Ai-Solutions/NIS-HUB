import React, { useState } from 'react';
import { PlusIcon, MagnifyingGlassIcon, FunnelIcon, PlayIcon, PauseIcon, StopIcon } from '@heroicons/react/24/outline';
import { useWebSocket } from '../contexts/WebSocketContext';
import { formatDistanceToNow } from 'date-fns';

export const MissionsView: React.FC = () => {
  const { missions } = useWebSocket();
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState<string>('all');
  const [filterType, setFilterType] = useState<string>('all');

  const filteredMissions = missions.filter(mission => {
    const matchesSearch = mission.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         mission.description.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = filterStatus === 'all' || mission.status === filterStatus;
    const matchesType = filterType === 'all' || mission.type === filterType;
    return matchesSearch && matchesStatus && matchesType;
  });

  const missionCounts = {
    total: missions.length,
    active: missions.filter(m => m.status === 'active').length,
    pending: missions.filter(m => m.status === 'pending').length,
    completed: missions.filter(m => m.status === 'completed').length,
    failed: missions.filter(m => m.status === 'failed').length,
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'critical': return 'bg-red-500/20 text-red-300 border-red-500/30';
      case 'high': return 'bg-orange-500/20 text-orange-300 border-orange-500/30';
      case 'medium': return 'bg-yellow-500/20 text-yellow-300 border-yellow-500/30';
      case 'low': return 'bg-slate-500/20 text-slate-300 border-slate-500/30';
      default: return 'bg-slate-500/20 text-slate-300 border-slate-500/30';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-emerald-500/20 text-emerald-300';
      case 'pending': return 'bg-yellow-500/20 text-yellow-300';
      case 'completed': return 'bg-nis-blue-500/20 text-nis-blue-300';
      case 'failed': return 'bg-red-500/20 text-red-300';
      case 'paused': return 'bg-slate-500/20 text-slate-300';
      default: return 'bg-slate-500/20 text-slate-300';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Mission Control</h1>
          <p className="text-slate-400">Coordinate complex multi-node operations</p>
        </div>
        <button className="button-primary flex items-center space-x-2">
          <PlusIcon className="h-4 w-4" />
          <span>Create Mission</span>
        </button>
      </div>

      {/* Mission Stats */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
        {Object.entries(missionCounts).map(([status, count]) => (
          <div key={status} className="card">
            <div className="card-content">
              <div className="text-center">
                <p className="text-sm text-slate-400 capitalize">{status}</p>
                <p className="text-2xl font-bold text-white">{count}</p>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Filters */}
      <div className="card">
        <div className="card-content">
          <div className="flex flex-col md:flex-row gap-4">
            {/* Search */}
            <div className="flex-1">
              <div className="relative">
                <MagnifyingGlassIcon className="h-5 w-5 absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400" />
                <input
                  type="text"
                  placeholder="Search missions..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-nis-blue-500"
                />
              </div>
            </div>

            {/* Status Filter */}
            <div className="flex items-center space-x-2">
              <FunnelIcon className="h-5 w-5 text-slate-400" />
              <select
                value={filterStatus}
                onChange={(e) => setFilterStatus(e.target.value)}
                className="bg-slate-700 border border-slate-600 rounded-lg px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-nis-blue-500"
              >
                <option value="all">All Status</option>
                <option value="active">Active</option>
                <option value="pending">Pending</option>
                <option value="completed">Completed</option>
                <option value="failed">Failed</option>
                <option value="paused">Paused</option>
              </select>
            </div>

            {/* Type Filter */}
            <div>
              <select
                value={filterType}
                onChange={(e) => setFilterType(e.target.value)}
                className="bg-slate-700 border border-slate-600 rounded-lg px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-nis-blue-500"
              >
                <option value="all">All Types</option>
                <option value="exploration">Exploration</option>
                <option value="analysis">Analysis</option>
                <option value="coordination">Coordination</option>
                <option value="surveillance">Surveillance</option>
              </select>
            </div>
          </div>
        </div>
      </div>

      {/* Missions List */}
      <div className="space-y-4">
        {filteredMissions.length === 0 ? (
          <div className="card">
            <div className="card-content text-center text-slate-400 py-12">
              <p>No missions match your search criteria</p>
            </div>
          </div>
        ) : (
          filteredMissions.map((mission) => (
            <div key={mission.id} className="card hover:border-slate-600/50 transition-colors">
              <div className="card-content">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-2">
                      <h3 className="text-lg font-semibold text-white">{mission.name}</h3>
                      <div className={`px-3 py-1 rounded-full text-xs font-medium border ${getPriorityColor(mission.priority)}`}>
                        {mission.priority}
                      </div>
                      <div className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(mission.status)}`}>
                        {mission.status}
                      </div>
                    </div>
                    <p className="text-slate-400 mb-3">{mission.description}</p>
                    
                    {/* Progress Bar */}
                    <div className="flex items-center space-x-3 mb-3">
                      <div className="flex-1 bg-slate-600 rounded-full h-2">
                        <div 
                          className="bg-nis-blue-500 h-2 rounded-full transition-all duration-300" 
                          style={{ width: `${mission.progress}%` }}
                        ></div>
                      </div>
                      <span className="text-sm text-slate-300 min-w-0">{mission.progress}%</span>
                    </div>

                    {/* Mission Info */}
                    <div className="flex items-center space-x-6 text-xs text-slate-400">
                      <span>Type: {mission.type}</span>
                      <span>Nodes: {mission.assigned_nodes.length}</span>
                      <span>Created: {formatDistanceToNow(new Date(mission.created_at), { addSuffix: true })}</span>
                      {mission.deadline && (
                        <span>Deadline: {formatDistanceToNow(new Date(mission.deadline), { addSuffix: true })}</span>
                      )}
                    </div>
                  </div>

                  {/* Action Buttons */}
                  <div className="flex items-center space-x-2 ml-4">
                    {mission.status === 'active' && (
                      <button className="p-2 rounded-lg hover:bg-slate-700 transition-colors" title="Pause Mission">
                        <PauseIcon className="h-4 w-4 text-slate-400" />
                      </button>
                    )}
                    {mission.status === 'pending' && (
                      <button className="p-2 rounded-lg hover:bg-slate-700 transition-colors" title="Start Mission">
                        <PlayIcon className="h-4 w-4 text-emerald-400" />
                      </button>
                    )}
                    {(mission.status === 'active' || mission.status === 'pending') && (
                      <button className="p-2 rounded-lg hover:bg-slate-700 transition-colors" title="Stop Mission">
                        <StopIcon className="h-4 w-4 text-red-400" />
                      </button>
                    )}
                  </div>
                </div>

                {/* Tasks Preview */}
                {mission.tasks && mission.tasks.length > 0 && (
                  <div>
                    <h4 className="text-sm font-medium text-slate-300 mb-2">
                      Tasks ({mission.tasks.filter(t => t.status === 'completed').length}/{mission.tasks.length} completed)
                    </h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                      {mission.tasks.slice(0, 4).map((task) => (
                        <div key={task.id} className="flex items-center space-x-2 p-2 bg-slate-700/30 rounded text-xs">
                          <div className={`w-2 h-2 rounded-full ${
                            task.status === 'completed' ? 'bg-emerald-400' :
                            task.status === 'in_progress' ? 'bg-yellow-400' :
                            task.status === 'failed' ? 'bg-red-400' :
                            'bg-slate-400'
                          }`}></div>
                          <span className="text-slate-300 flex-1">{task.name}</span>
                          <span className="text-slate-400">{task.assigned_node}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}; 