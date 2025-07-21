import React from 'react';
import { ServerIcon, CpuChipIcon, CircleStackIcon } from '@heroicons/react/24/outline';
import { formatDistanceToNow } from 'date-fns';
import type { Node } from '../types';

interface NodesOverviewProps {
  nodes: Node[];
}

export const NodesOverview: React.FC<NodesOverviewProps> = ({ nodes }) => {
  if (nodes.length === 0) {
    return (
      <div className="text-center text-slate-400 py-8">
        <ServerIcon className="h-8 w-8 mx-auto mb-2 opacity-50" />
        <p className="text-sm">No nodes connected</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {nodes.map((node) => (
        <div key={node.id} className="p-4 bg-slate-700/30 rounded-lg hover:bg-slate-700/50 transition-colors">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center space-x-3">
              <div className={`w-3 h-3 rounded-full ${
                node.status === 'online' ? 'bg-emerald-400 animate-pulse-slow' :
                node.status === 'syncing' ? 'bg-yellow-400' :
                'bg-red-400'
              }`}></div>
              <div>
                <h4 className="font-medium text-white">{node.name}</h4>
                <p className="text-sm text-slate-400">{node.type}</p>
              </div>
            </div>
            <div className={`status-indicator ${
              node.status === 'online' ? 'status-online' :
              node.status === 'syncing' ? 'status-syncing' :
              'status-offline'
            }`}>
              {node.status}
            </div>
          </div>

          {/* Node Metrics */}
          <div className="grid grid-cols-3 gap-4 mb-3">
            <div className="flex items-center space-x-2">
              <CpuChipIcon className="h-4 w-4 text-slate-400" />
              <div>
                <p className="text-xs text-slate-400">CPU</p>
                <p className="text-sm text-white">{node.cpu_usage || 0}%</p>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <CircleStackIcon className="h-4 w-4 text-slate-400" />
              <div>
                <p className="text-xs text-slate-400">Memory</p>
                <p className="text-sm text-white">{node.memory_usage || 0}%</p>
              </div>
            </div>
            <div>
              <p className="text-xs text-slate-400">Health</p>
              <div className="flex items-center space-x-2">
                <div className="w-12 bg-slate-600 rounded-full h-1.5">
                  <div 
                    className={`h-1.5 rounded-full ${
                      node.health_score >= 80 ? 'bg-emerald-500' :
                      node.health_score >= 60 ? 'bg-yellow-500' :
                      'bg-red-500'
                    }`} 
                    style={{ width: `${node.health_score || 0}%` }}
                  ></div>
                </div>
                <span className="text-sm text-white">{node.health_score || 0}%</span>
              </div>
            </div>
          </div>

          {/* Node Info */}
          <div className="flex items-center justify-between text-xs text-slate-400">
            <span>v{node.version || '1.0.0'}</span>
            <span>
              Last seen {formatDistanceToNow(new Date(node.last_heartbeat || Date.now()), { addSuffix: true })}
            </span>
          </div>

          {/* Capabilities */}
          {node.capabilities && node.capabilities.length > 0 && (
            <div className="mt-3 flex flex-wrap gap-1">
              {node.capabilities.slice(0, 3).map((capability) => (
                <span
                  key={capability}
                  className="px-2 py-1 bg-nis-blue-500/20 text-nis-blue-300 text-xs rounded-md"
                >
                  {capability}
                </span>
              ))}
              {node.capabilities.length > 3 && (
                <span className="px-2 py-1 bg-slate-600 text-slate-300 text-xs rounded-md">
                  +{node.capabilities.length - 3} more
                </span>
              )}
            </div>
          )}
        </div>
      ))}
    </div>
  );
}; 