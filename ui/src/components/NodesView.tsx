import React, { useState } from 'react';
import { MagnifyingGlassIcon, PlusIcon, FunnelIcon } from '@heroicons/react/24/outline';
import { useWebSocket } from '../contexts/WebSocketContext';
import { NodesOverview } from './NodesOverview';

export const NodesView: React.FC = () => {
  const { nodes } = useWebSocket();
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState<string>('all');

  const filteredNodes = nodes.filter(node => {
    const matchesSearch = node.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         node.type.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesFilter = filterStatus === 'all' || node.status === filterStatus;
    return matchesSearch && matchesFilter;
  });

  const statusCounts = {
    all: nodes.length,
    online: nodes.filter(n => n.status === 'online').length,
    offline: nodes.filter(n => n.status === 'offline').length,
    syncing: nodes.filter(n => n.status === 'syncing').length,
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Node Network</h1>
          <p className="text-slate-400">Manage and monitor connected NIS nodes</p>
        </div>
        <button className="button-primary flex items-center space-x-2">
          <PlusIcon className="h-4 w-4" />
          <span>Register Node</span>
        </button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {Object.entries(statusCounts).map(([status, count]) => (
          <div key={status} className="card">
            <div className="card-content">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-slate-400 capitalize">{status} Nodes</p>
                  <p className="text-2xl font-bold text-white">{count}</p>
                </div>
                <div className={`w-3 h-3 rounded-full ${
                  status === 'online' ? 'bg-emerald-400' :
                  status === 'offline' ? 'bg-red-400' :
                  status === 'syncing' ? 'bg-yellow-400' :
                  'bg-slate-400'
                }`}></div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Filters and Search */}
      <div className="card">
        <div className="card-content">
          <div className="flex flex-col md:flex-row gap-4">
            {/* Search */}
            <div className="flex-1">
              <div className="relative">
                <MagnifyingGlassIcon className="h-5 w-5 absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400" />
                <input
                  type="text"
                  placeholder="Search nodes by name or type..."
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
                <option value="online">Online</option>
                <option value="offline">Offline</option>
                <option value="syncing">Syncing</option>
              </select>
            </div>
          </div>
        </div>
      </div>

      {/* Nodes List */}
      <div className="card">
        <div className="card-header">
          <h3 className="text-lg font-semibold text-white">
            Connected Nodes ({filteredNodes.length})
          </h3>
          <p className="text-sm text-slate-400">
            Real-time status of all registered NIS nodes
          </p>
        </div>
        <div className="card-content">
          {filteredNodes.length === 0 ? (
            <div className="text-center text-slate-400 py-12">
              <p>No nodes match your search criteria</p>
            </div>
          ) : (
            <NodesOverview nodes={filteredNodes} />
          )}
        </div>
      </div>
    </div>
  );
}; 