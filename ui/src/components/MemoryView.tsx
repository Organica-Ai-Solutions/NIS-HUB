import React, { useState } from 'react';
import { MagnifyingGlassIcon, FunnelIcon, EyeIcon } from '@heroicons/react/24/outline';
import { useWebSocket } from '../contexts/WebSocketContext';
import { formatDistanceToNow } from 'date-fns';

export const MemoryView: React.FC = () => {
  const { memoryEntries } = useWebSocket();
  const [searchTerm, setSearchTerm] = useState('');
  const [filterType, setFilterType] = useState<string>('all');
  const [filterScope, setFilterScope] = useState<string>('all');

  const filteredEntries = memoryEntries.filter(entry => {
    const matchesSearch = JSON.stringify(entry.content).toLowerCase().includes(searchTerm.toLowerCase()) ||
                         entry.node_id.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesType = filterType === 'all' || entry.type === filterType;
    const matchesScope = filterScope === 'all' || entry.scope === filterScope;
    return matchesSearch && matchesType && matchesScope;
  });

  const memoryCounts = {
    total: memoryEntries.length,
    episodic: memoryEntries.filter(e => e.type === 'episodic').length,
    semantic: memoryEntries.filter(e => e.type === 'semantic').length,
    procedural: memoryEntries.filter(e => e.type === 'procedural').length,
    working: memoryEntries.filter(e => e.type === 'working').length,
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Distributed Memory</h1>
          <p className="text-slate-400">Explore the shared knowledge layer across all nodes</p>
        </div>
      </div>

      {/* Memory Type Stats */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
        {Object.entries(memoryCounts).map(([type, count]) => (
          <div key={type} className="card">
            <div className="card-content">
              <div className="text-center">
                <p className="text-sm text-slate-400 capitalize">{type}</p>
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
                  placeholder="Search memory content..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-nis-blue-500"
                />
              </div>
            </div>

            {/* Type Filter */}
            <div className="flex items-center space-x-2">
              <FunnelIcon className="h-5 w-5 text-slate-400" />
              <select
                value={filterType}
                onChange={(e) => setFilterType(e.target.value)}
                className="bg-slate-700 border border-slate-600 rounded-lg px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-nis-blue-500"
              >
                <option value="all">All Types</option>
                <option value="episodic">Episodic</option>
                <option value="semantic">Semantic</option>
                <option value="procedural">Procedural</option>
                <option value="working">Working</option>
              </select>
            </div>

            {/* Scope Filter */}
            <div>
              <select
                value={filterScope}
                onChange={(e) => setFilterScope(e.target.value)}
                className="bg-slate-700 border border-slate-600 rounded-lg px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-nis-blue-500"
              >
                <option value="all">All Scopes</option>
                <option value="local">Local</option>
                <option value="shared">Shared</option>
                <option value="global">Global</option>
              </select>
            </div>
          </div>
        </div>
      </div>

      {/* Memory Entries */}
      <div className="card">
        <div className="card-header">
          <h3 className="text-lg font-semibold text-white">
            Memory Entries ({filteredEntries.length})
          </h3>
          <p className="text-sm text-slate-400">
            Distributed knowledge across the NIS network
          </p>
        </div>
        <div className="card-content">
          {filteredEntries.length === 0 ? (
            <div className="text-center text-slate-400 py-12">
              <p>No memory entries match your search criteria</p>
            </div>
          ) : (
            <div className="space-y-4">
              {filteredEntries.slice(0, 20).map((entry) => (
                <div key={entry.id} className="p-4 bg-slate-700/30 rounded-lg hover:bg-slate-700/50 transition-colors">
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex items-center space-x-3">
                      <div className={`px-2 py-1 rounded text-xs font-medium ${
                        entry.type === 'episodic' ? 'bg-emerald-500/20 text-emerald-300' :
                        entry.type === 'semantic' ? 'bg-nis-blue-500/20 text-nis-blue-300' :
                        entry.type === 'procedural' ? 'bg-nis-purple-500/20 text-nis-purple-300' :
                        'bg-yellow-500/20 text-yellow-300'
                      }`}>
                        {entry.type}
                      </div>
                      <div className={`px-2 py-1 rounded text-xs font-medium ${
                        entry.scope === 'global' ? 'bg-red-500/20 text-red-300' :
                        entry.scope === 'shared' ? 'bg-orange-500/20 text-orange-300' :
                        'bg-slate-500/20 text-slate-300'
                      }`}>
                        {entry.scope}
                      </div>
                    </div>
                    <button className="p-1 rounded hover:bg-slate-600/50 transition-colors">
                      <EyeIcon className="h-4 w-4 text-slate-400" />
                    </button>
                  </div>

                  <div className="mb-3">
                    <p className="text-sm text-white line-clamp-2">
                      {typeof entry.content === 'string' ? entry.content : JSON.stringify(entry.content).slice(0, 200)}...
                    </p>
                  </div>

                  <div className="flex items-center justify-between text-xs text-slate-400">
                    <div className="flex items-center space-x-4">
                      <span>Node: {entry.node_id}</span>
                      <span>Accessed: {entry.access_count} times</span>
                      <span>Importance: {(entry.importance_score * 100).toFixed(0)}%</span>
                    </div>
                    <span>
                      {formatDistanceToNow(new Date(entry.created_at), { addSuffix: true })}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}; 