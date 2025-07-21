export interface Node {
  id: string;
  name: string;
  type: string;
  status: 'online' | 'offline' | 'syncing';
  endpoint: string;
  capabilities: string[];
  health_score: number;
  last_heartbeat: string;
  version: string;
  uptime: number;
  memory_usage: number;
  cpu_usage: number;
}

export interface MemoryEntry {
  id: string;
  node_id: string;
  type: 'episodic' | 'semantic' | 'procedural' | 'working';
  scope: 'local' | 'shared' | 'global';
  content: any;
  metadata: Record<string, any>;
  embedding?: number[];
  created_at: string;
  updated_at: string;
  access_count: number;
  importance_score: number;
}

export interface Mission {
  id: string;
  name: string;
  description: string;
  type: 'exploration' | 'analysis' | 'coordination' | 'surveillance';
  status: 'pending' | 'active' | 'paused' | 'completed' | 'failed';
  priority: 'low' | 'medium' | 'high' | 'critical';
  assigned_nodes: string[];
  created_at: string;
  deadline?: string;
  progress: number;
  tasks: MissionTask[];
}

export interface MissionTask {
  id: string;
  name: string;
  description: string;
  status: 'pending' | 'in_progress' | 'completed' | 'failed';
  assigned_node: string;
  dependencies: string[];
  estimated_duration: number;
  actual_duration?: number;
}

export interface SystemStats {
  total_nodes: number;
  active_nodes: number;
  total_memory_entries: number;
  memory_usage_mb: number;
  active_missions: number;
  messages_per_second: number;
  uptime: number;
}

export interface WebSocketMessage {
  type: 'node_update' | 'memory_sync' | 'mission_update' | 'system_alert';
  timestamp: string;
  data: any;
}

export interface ActivityLog {
  id: string;
  timestamp: string;
  type: 'info' | 'warning' | 'error' | 'success';
  source: string;
  message: string;
  details?: any;
} 