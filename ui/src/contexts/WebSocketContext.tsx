import React, { createContext, useContext, useEffect, useState } from 'react';
import type { ReactNode } from 'react';
import io, { Socket } from 'socket.io-client';
import type { WebSocketMessage, Node, MemoryEntry, Mission, ActivityLog } from '../types';

interface WebSocketContextType {
  socket: Socket | null;
  isConnected: boolean;
  nodes: Node[];
  memoryEntries: MemoryEntry[];
  missions: Mission[];
  activityLogs: ActivityLog[];
  systemStats: any;
  sendMessage: (type: string, data: any) => void;
}

const WebSocketContext = createContext<WebSocketContextType | undefined>(undefined);

export const useWebSocket = () => {
  const context = useContext(WebSocketContext);
  if (!context) {
    throw new Error('useWebSocket must be used within a WebSocketProvider');
  }
  return context;
};

interface WebSocketProviderProps {
  children: ReactNode;
}

export const WebSocketProvider: React.FC<WebSocketProviderProps> = ({ children }) => {
  const [socket, setSocket] = useState<Socket | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [nodes, setNodes] = useState<Node[]>([]);
  const [memoryEntries, setMemoryEntries] = useState<MemoryEntry[]>([]);
  const [missions, setMissions] = useState<Mission[]>([]);
  const [activityLogs, setActivityLogs] = useState<ActivityLog[]>([]);
  const [systemStats, setSystemStats] = useState({});

  useEffect(() => {
    // Connect to WebSocket server
    const newSocket = io('ws://localhost:8000', {
      transports: ['websocket'],
      autoConnect: true,
    });

    newSocket.on('connect', () => {
      console.log('Connected to NIS HUB WebSocket');
      setIsConnected(true);
      
      // Add connection activity log
      const connectionLog: ActivityLog = {
        id: Date.now().toString(),
        timestamp: new Date().toISOString(),
        type: 'success',
        source: 'WebSocket',
        message: 'Connected to NIS HUB successfully',
      };
      setActivityLogs(prev => [connectionLog, ...prev.slice(0, 99)]);
    });

    newSocket.on('disconnect', () => {
      console.log('Disconnected from NIS HUB WebSocket');
      setIsConnected(false);
      
      // Add disconnection activity log
      const disconnectionLog: ActivityLog = {
        id: Date.now().toString(),
        timestamp: new Date().toISOString(),
        type: 'warning',
        source: 'WebSocket',
        message: 'Disconnected from NIS HUB',
      };
      setActivityLogs(prev => [disconnectionLog, ...prev.slice(0, 99)]);
    });

    newSocket.on('node_update', (data: Node) => {
      setNodes(prev => {
        const existing = prev.findIndex(node => node.id === data.id);
        if (existing >= 0) {
          const updated = [...prev];
          updated[existing] = data;
          return updated;
        } else {
          return [data, ...prev];
        }
      });

      // Add activity log
      const activityLog: ActivityLog = {
        id: Date.now().toString(),
        timestamp: new Date().toISOString(),
        type: data.status === 'online' ? 'success' : data.status === 'offline' ? 'error' : 'info',
        source: data.name,
        message: `Node status updated: ${data.status}`,
        details: data,
      };
      setActivityLogs(prev => [activityLog, ...prev.slice(0, 99)]);
    });

    newSocket.on('memory_sync', (data: MemoryEntry) => {
      setMemoryEntries(prev => {
        const existing = prev.findIndex(entry => entry.id === data.id);
        if (existing >= 0) {
          const updated = [...prev];
          updated[existing] = data;
          return updated;
        } else {
          return [data, ...prev.slice(0, 999)]; // Keep last 1000 entries
        }
      });

      // Add activity log
      const activityLog: ActivityLog = {
        id: Date.now().toString(),
        timestamp: new Date().toISOString(),
        type: 'info',
        source: 'Memory',
        message: `Memory entry synchronized: ${data.type}`,
        details: data,
      };
      setActivityLogs(prev => [activityLog, ...prev.slice(0, 99)]);
    });

    newSocket.on('mission_update', (data: Mission) => {
      setMissions(prev => {
        const existing = prev.findIndex(mission => mission.id === data.id);
        if (existing >= 0) {
          const updated = [...prev];
          updated[existing] = data;
          return updated;
        } else {
          return [data, ...prev];
        }
      });

      // Add activity log
      const activityLog: ActivityLog = {
        id: Date.now().toString(),
        timestamp: new Date().toISOString(),
        type: data.status === 'completed' ? 'success' : data.status === 'failed' ? 'error' : 'info',
        source: 'Mission',
        message: `Mission ${data.name}: ${data.status}`,
        details: data,
      };
      setActivityLogs(prev => [activityLog, ...prev.slice(0, 99)]);
    });

    newSocket.on('system_stats', (data: any) => {
      setSystemStats(data);
    });

    setSocket(newSocket);

    return () => {
      newSocket.close();
    };
  }, []);

  const sendMessage = (type: string, data: any) => {
    if (socket && isConnected) {
      socket.emit(type, data);
    }
  };

  const contextValue: WebSocketContextType = {
    socket,
    isConnected,
    nodes,
    memoryEntries,
    missions,
    activityLogs,
    systemStats,
    sendMessage,
  };

  return (
    <WebSocketContext.Provider value={contextValue}>
      {children}
    </WebSocketContext.Provider>
  );
}; 