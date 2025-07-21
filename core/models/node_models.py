"""
Node Models for NIS HUB

Data structures for node registration, status tracking, and heartbeat management.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, validator
from enum import Enum

from .base_models import SystemStatus, ConnectionStatus

class NodeType(str, Enum):
    """Types of NIS nodes that can connect to the HUB."""
    EXOPLANET_ANALYSIS = "exoplanet_analysis"     # NIS-X
    DRONE_CONTROL = "drone_control"               # NIS Drone
    ARCHAEOLOGICAL = "archaeological"             # NIS Archaeological
    WEATHER_ANALYSIS = "weather_analysis"         # NIS Weather
    GENERAL_AGENT = "general_agent"               # Generic NIS agent
    SUPERVISOR = "supervisor"                     # Supervisor agent
    CUSTOM = "custom"                             # Custom node type

class NodeCapability(str, Enum):
    """Capabilities that nodes can provide."""
    DATA_PROCESSING = "data_processing"
    MACHINE_LEARNING = "machine_learning"
    REAL_TIME_ANALYSIS = "real_time_analysis"
    MEMORY_STORAGE = "memory_storage"
    COORDINATION = "coordination"
    VISUALIZATION = "visualization"
    COMMUNICATION = "communication"

class NodeRegistration(BaseModel):
    """Node registration request model."""
    name: str = Field(..., description="Unique name for the node", min_length=1, max_length=100)
    node_type: NodeType = Field(..., description="Type of NIS node")
    version: str = Field(..., description="Node software version")
    endpoint: str = Field(..., description="HTTP endpoint for node communication")
    websocket_endpoint: Optional[str] = Field(None, description="WebSocket endpoint if supported")
    
    # Node capabilities and metadata
    capabilities: List[NodeCapability] = Field(default=[], description="List of node capabilities")
    description: Optional[str] = Field(None, description="Human-readable description", max_length=500)
    metadata: Dict[str, Any] = Field(default={}, description="Additional node metadata")
    
    # Configuration
    heartbeat_interval: int = Field(default=30, description="Heartbeat interval in seconds", ge=10, le=300)
    max_memory_size: Optional[int] = Field(None, description="Maximum memory size in MB")
    
    @validator('endpoint')
    def validate_endpoint(cls, v):
        """Validate endpoint URL format."""
        if not v.startswith(('http://', 'https://')):
            raise ValueError('Endpoint must be a valid HTTP/HTTPS URL')
        return v
    
    @validator('name')
    def validate_name(cls, v):
        """Validate node name format."""
        import re
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('Name must contain only alphanumeric characters, hyphens, and underscores')
        return v

class NodeHeartbeat(BaseModel):
    """Heartbeat message from registered nodes."""
    node_id: str = Field(..., description="Unique node identifier")
    status: SystemStatus = Field(..., description="Current node status")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Heartbeat timestamp")
    
    # Performance metrics
    cpu_usage: Optional[float] = Field(None, description="CPU usage percentage", ge=0, le=100)
    memory_usage: Optional[float] = Field(None, description="Memory usage percentage", ge=0, le=100)
    disk_usage: Optional[float] = Field(None, description="Disk usage percentage", ge=0, le=100)
    
    # Operational metrics
    active_tasks: int = Field(default=0, description="Number of active tasks", ge=0)
    completed_tasks: int = Field(default=0, description="Number of completed tasks", ge=0)
    error_count: int = Field(default=0, description="Number of errors since last heartbeat", ge=0)
    
    # Additional status information
    details: Dict[str, Any] = Field(default={}, description="Additional status details")

class NodeInfo(BaseModel):
    """Complete node information including registration and status."""
    # Registration information
    node_id: str = Field(..., description="Unique node identifier")
    name: str = Field(..., description="Node name")
    node_type: NodeType = Field(..., description="Type of NIS node")
    version: str = Field(..., description="Node software version")
    endpoint: str = Field(..., description="HTTP endpoint")
    websocket_endpoint: Optional[str] = Field(None, description="WebSocket endpoint")
    
    # Current status
    status: SystemStatus = Field(..., description="Current operational status")
    connection_status: ConnectionStatus = Field(..., description="Connection status to HUB")
    
    # Timestamps
    registered_at: datetime = Field(..., description="Registration timestamp")
    last_heartbeat: Optional[datetime] = Field(None, description="Last heartbeat timestamp")
    last_seen: Optional[datetime] = Field(None, description="Last activity timestamp")
    
    # Capabilities and configuration
    capabilities: List[NodeCapability] = Field(default=[], description="Node capabilities")
    description: Optional[str] = Field(None, description="Node description")
    metadata: Dict[str, Any] = Field(default={}, description="Node metadata")
    heartbeat_interval: int = Field(default=30, description="Heartbeat interval")
    
    # Performance metrics (latest from heartbeat)
    cpu_usage: Optional[float] = Field(None, description="Latest CPU usage")
    memory_usage: Optional[float] = Field(None, description="Latest memory usage")
    disk_usage: Optional[float] = Field(None, description="Latest disk usage")
    
    # Statistics
    total_tasks: int = Field(default=0, description="Total tasks processed")
    total_errors: int = Field(default=0, description="Total errors encountered")
    uptime_hours: Optional[float] = Field(None, description="Uptime in hours")

class NodeStatus(BaseModel):
    """Node status summary for dashboard display."""
    node_id: str = Field(..., description="Node identifier")
    name: str = Field(..., description="Node name")
    node_type: NodeType = Field(..., description="Node type")
    status: SystemStatus = Field(..., description="Operational status")
    connection_status: ConnectionStatus = Field(..., description="Connection status")
    last_heartbeat: Optional[datetime] = Field(None, description="Last heartbeat")
    
    # Health indicators
    is_healthy: bool = Field(..., description="Overall health status")
    response_time_ms: Optional[float] = Field(None, description="Latest response time")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class NodeUpdate(BaseModel):
    """Model for updating node configuration."""
    description: Optional[str] = Field(None, description="Updated description")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Updated metadata")
    heartbeat_interval: Optional[int] = Field(None, description="Updated heartbeat interval", ge=10, le=300)
    capabilities: Optional[List[NodeCapability]] = Field(None, description="Updated capabilities")

class NodeStatsQuery(BaseModel):
    """Query parameters for node statistics."""
    node_ids: Optional[List[str]] = Field(None, description="Specific node IDs to query")
    node_types: Optional[List[NodeType]] = Field(None, description="Node types to include")
    time_range_hours: int = Field(default=24, description="Time range for statistics", ge=1, le=168)
    include_metrics: bool = Field(default=True, description="Include performance metrics") 