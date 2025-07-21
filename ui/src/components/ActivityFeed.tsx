import React from 'react';
import { useWebSocket } from '../contexts/WebSocketContext';
import { formatDistanceToNow } from 'date-fns';
import {
  InformationCircleIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  XCircleIcon,
} from '@heroicons/react/24/outline';

export const ActivityFeed: React.FC = () => {
  const { activityLogs } = useWebSocket();

  const getIcon = (type: string) => {
    switch (type) {
      case 'success':
        return CheckCircleIcon;
      case 'error':
        return XCircleIcon;
      case 'warning':
        return ExclamationTriangleIcon;
      default:
        return InformationCircleIcon;
    }
  };

  const getIconColor = (type: string) => {
    switch (type) {
      case 'success':
        return 'text-emerald-400';
      case 'error':
        return 'text-red-400';
      case 'warning':
        return 'text-yellow-400';
      default:
        return 'text-nis-blue-400';
    }
  };

  return (
    <div className="space-y-3 max-h-80 overflow-y-auto">
      {activityLogs.length === 0 ? (
        <div className="text-center text-slate-400 py-8">
          <InformationCircleIcon className="h-8 w-8 mx-auto mb-2 opacity-50" />
          <p className="text-sm">No recent activity</p>
        </div>
      ) : (
        activityLogs.map((log) => {
          const Icon = getIcon(log.type);
          const iconColor = getIconColor(log.type);
          
          return (
            <div key={log.id} className="flex items-start space-x-3 p-3 hover:bg-slate-700/30 rounded-lg transition-colors">
              <Icon className={`h-4 w-4 mt-0.5 ${iconColor} flex-shrink-0`} />
              <div className="flex-1 min-w-0">
                <p className="text-sm text-white break-words">{log.message}</p>
                <div className="flex items-center justify-between mt-1">
                  <span className="text-xs text-slate-400">{log.source}</span>
                  <span className="text-xs text-slate-400">
                    {formatDistanceToNow(new Date(log.timestamp), { addSuffix: true })}
                  </span>
                </div>
              </div>
            </div>
          );
        })
      )}
    </div>
  );
}; 