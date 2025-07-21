"""
Mission Models for NIS HUB

Data structures for coordinating complex missions and workflows
across multiple NIS nodes and agents.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from pydantic import BaseModel, Field, validator
from enum import Enum

from .base_models import Priority, SystemStatus

class MissionType(str, Enum):
    """Types of missions that can be coordinated."""
    EXPLORATION = "exploration"                    # Multi-domain exploration
    ANALYSIS = "analysis"                         # Coordinated analysis task
    EMERGENCY_RESPONSE = "emergency_response"     # Emergency coordination
    DATA_COLLECTION = "data_collection"           # Systematic data gathering
    SURVEILLANCE = "surveillance"                 # Monitoring operations
    RESEARCH = "research"                         # Scientific research
    MAINTENANCE = "maintenance"                   # System maintenance
    TRAINING = "training"                         # Agent training coordination
    CUSTOM = "custom"                             # Custom mission type

class MissionStatus(str, Enum):
    """Mission execution status."""
    PLANNED = "planned"                           # Mission created but not started
    ACTIVE = "active"                             # Currently executing
    PAUSED = "paused"                             # Temporarily paused
    COMPLETED = "completed"                       # Successfully completed
    FAILED = "failed"                             # Failed to complete
    CANCELLED = "cancelled"                       # Cancelled by user/system
    EXPIRED = "expired"                           # Expired before completion

class TaskStatus(str, Enum):
    """Individual task status within a mission."""
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"

class MissionTask(BaseModel):
    """Individual task within a mission."""
    task_id: str = Field(..., description="Unique task identifier")
    name: str = Field(..., description="Task name")
    description: Optional[str] = Field(None, description="Task description")
    
    # Assignment
    assigned_node_id: Optional[str] = Field(None, description="Assigned node ID")
    required_capabilities: List[str] = Field(default=[], description="Required node capabilities")
    
    # Configuration
    task_type: str = Field(..., description="Type of task")
    parameters: Dict[str, Any] = Field(default={}, description="Task parameters")
    
    # Scheduling
    priority: Priority = Field(default=Priority.MEDIUM, description="Task priority")
    estimated_duration_minutes: Optional[int] = Field(None, description="Estimated duration")
    dependencies: List[str] = Field(default=[], description="Dependent task IDs")
    
    # Status
    status: TaskStatus = Field(default=TaskStatus.PENDING, description="Current status")
    progress_percent: float = Field(default=0.0, description="Progress percentage", ge=0, le=100)
    
    # Execution details
    started_at: Optional[datetime] = Field(None, description="Task start time")
    completed_at: Optional[datetime] = Field(None, description="Task completion time")
    result: Optional[Dict[str, Any]] = Field(None, description="Task result data")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    
    # Retry configuration
    max_retries: int = Field(default=3, description="Maximum retry attempts", ge=0)
    retry_count: int = Field(default=0, description="Current retry count", ge=0)

class MissionCreate(BaseModel):
    """Mission creation request."""
    name: str = Field(..., description="Mission name", max_length=200)
    description: Optional[str] = Field(None, description="Mission description", max_length=1000)
    
    # Classification
    mission_type: MissionType = Field(..., description="Type of mission")
    domain: str = Field(..., description="Primary domain (e.g., 'exoplanet', 'drone')")
    priority: Priority = Field(default=Priority.MEDIUM, description="Mission priority")
    
    # Tasks
    tasks: List[MissionTask] = Field(..., description="List of mission tasks", min_items=1)
    
    # Scheduling
    scheduled_start: Optional[datetime] = Field(None, description="Scheduled start time")
    deadline: Optional[datetime] = Field(None, description="Mission deadline")
    max_duration_hours: Optional[float] = Field(None, description="Maximum duration in hours", gt=0)
    
    # Configuration
    allow_parallel_execution: bool = Field(default=True, description="Allow parallel task execution")
    auto_assign_nodes: bool = Field(default=True, description="Automatically assign capable nodes")
    require_supervisor_approval: bool = Field(default=False, description="Require supervisor approval")
    
    # Metadata
    created_by: str = Field(..., description="Creator node ID or user ID")
    tags: List[str] = Field(default=[], description="Mission tags")
    metadata: Dict[str, Any] = Field(default={}, description="Additional metadata")
    
    @validator('deadline')
    def validate_deadline(cls, v, values):
        """Validate deadline is in the future."""
        if v and v <= datetime.utcnow():
            raise ValueError("Deadline must be in the future")
        return v
    
    @validator('scheduled_start')
    def validate_scheduled_start(cls, v):
        """Validate scheduled start time."""
        if v and v <= datetime.utcnow():
            raise ValueError("Scheduled start must be in the future")
        return v

class MissionUpdate(BaseModel):
    """Mission update request."""
    mission_id: str = Field(..., description="Mission ID to update")
    updated_by: str = Field(..., description="Node ID making the update")
    
    # Updatable fields
    name: Optional[str] = Field(None, description="Updated name")
    description: Optional[str] = Field(None, description="Updated description")
    priority: Optional[Priority] = Field(None, description="Updated priority")
    status: Optional[MissionStatus] = Field(None, description="Updated status")
    
    # Task updates
    task_updates: List[Dict[str, Any]] = Field(default=[], description="Task status updates")
    
    # Progress
    progress_percent: Optional[float] = Field(None, description="Overall progress", ge=0, le=100)
    progress_message: Optional[str] = Field(None, description="Progress description")
    
    # Results
    partial_results: Optional[Dict[str, Any]] = Field(None, description="Partial results")
    
    # Metadata
    metadata_updates: Dict[str, Any] = Field(default={}, description="Metadata updates")

class Mission(BaseModel):
    """Complete mission information."""
    mission_id: str = Field(..., description="Unique mission identifier")
    name: str = Field(..., description="Mission name")
    description: Optional[str] = Field(None, description="Mission description")
    
    # Classification
    mission_type: MissionType = Field(..., description="Mission type")
    domain: str = Field(..., description="Primary domain")
    priority: Priority = Field(..., description="Mission priority")
    
    # Status
    status: MissionStatus = Field(..., description="Current status")
    progress_percent: float = Field(default=0.0, description="Overall progress", ge=0, le=100)
    
    # Tasks
    tasks: List[MissionTask] = Field(..., description="Mission tasks")
    total_tasks: int = Field(..., description="Total number of tasks")
    completed_tasks: int = Field(default=0, description="Number of completed tasks")
    failed_tasks: int = Field(default=0, description="Number of failed tasks")
    
    # Participants
    participating_nodes: List[str] = Field(default=[], description="Participating node IDs")
    coordinator_node_id: Optional[str] = Field(None, description="Coordinating node ID")
    
    # Timing
    created_at: datetime = Field(..., description="Creation timestamp")
    started_at: Optional[datetime] = Field(None, description="Start timestamp")
    completed_at: Optional[datetime] = Field(None, description="Completion timestamp")
    deadline: Optional[datetime] = Field(None, description="Mission deadline")
    estimated_completion: Optional[datetime] = Field(None, description="Estimated completion")
    
    # Configuration
    allow_parallel_execution: bool = Field(default=True, description="Parallel execution allowed")
    auto_assign_nodes: bool = Field(default=True, description="Auto-assign nodes")
    
    # Results
    results: Optional[Dict[str, Any]] = Field(None, description="Mission results")
    output_artifacts: List[str] = Field(default=[], description="Output artifact IDs")
    
    # Performance metrics
    execution_time_minutes: Optional[float] = Field(None, description="Total execution time")
    efficiency_score: Optional[float] = Field(None, description="Efficiency score", ge=0, le=1)
    
    # Metadata
    created_by: str = Field(..., description="Creator")
    tags: List[str] = Field(default=[], description="Mission tags")
    metadata: Dict[str, Any] = Field(default={}, description="Additional metadata")
    
    # Audit trail
    updates_count: int = Field(default=0, description="Number of updates")
    last_updated: Optional[datetime] = Field(None, description="Last update timestamp")
    last_updated_by: Optional[str] = Field(None, description="Last updater")

class MissionQuery(BaseModel):
    """Query parameters for mission search."""
    # Filters
    mission_ids: Optional[List[str]] = Field(None, description="Specific mission IDs")
    mission_types: Optional[List[MissionType]] = Field(None, description="Mission types")
    statuses: Optional[List[MissionStatus]] = Field(None, description="Mission statuses")
    domains: Optional[List[str]] = Field(None, description="Domains")
    priorities: Optional[List[Priority]] = Field(None, description="Priorities")
    
    # Participants
    participating_nodes: Optional[List[str]] = Field(None, description="Participating nodes")
    created_by: Optional[List[str]] = Field(None, description="Mission creators")
    
    # Time filters
    created_after: Optional[datetime] = Field(None, description="Created after")
    created_before: Optional[datetime] = Field(None, description="Created before")
    deadline_before: Optional[datetime] = Field(None, description="Deadline before")
    
    # Text search
    search_text: Optional[str] = Field(None, description="Search in name/description")
    tags: Optional[List[str]] = Field(None, description="Required tags")
    
    # Pagination
    page: int = Field(default=1, description="Page number", ge=1)
    page_size: int = Field(default=20, description="Page size", ge=1, le=100)
    sort_by: str = Field(default="created_at", description="Sort field")
    sort_order: str = Field(default="desc", description="Sort order")

class MissionStats(BaseModel):
    """Mission system statistics."""
    total_missions: int = Field(..., description="Total number of missions")
    active_missions: int = Field(..., description="Currently active missions")
    completed_missions: int = Field(..., description="Completed missions")
    failed_missions: int = Field(..., description="Failed missions")
    
    # By type
    missions_by_type: Dict[str, int] = Field(..., description="Missions by type")
    missions_by_domain: Dict[str, int] = Field(..., description="Missions by domain")
    missions_by_priority: Dict[str, int] = Field(..., description="Missions by priority")
    
    # Performance
    avg_completion_time_hours: float = Field(..., description="Average completion time")
    success_rate_percent: float = Field(..., description="Success rate percentage")
    avg_efficiency_score: float = Field(..., description="Average efficiency score")
    
    # Recent activity
    missions_created_last_24h: int = Field(..., description="Missions created in last 24h")
    missions_completed_last_24h: int = Field(..., description="Missions completed in last 24h")
    
    # Resources
    total_participating_nodes: int = Field(..., description="Total participating nodes")
    most_active_nodes: List[Dict[str, Any]] = Field(..., description="Most active nodes")

class CoordinationEvent(BaseModel):
    """Event for mission coordination and communication."""
    event_id: str = Field(..., description="Unique event identifier")
    mission_id: str = Field(..., description="Related mission ID")
    source_node_id: str = Field(..., description="Node that generated the event")
    
    # Event details
    event_type: str = Field(..., description="Type of coordination event")
    message: str = Field(..., description="Event message")
    data: Dict[str, Any] = Field(default={}, description="Event data")
    
    # Targeting
    target_node_ids: Optional[List[str]] = Field(None, description="Target nodes")
    broadcast_to_all: bool = Field(default=False, description="Broadcast to all participants")
    
    # Properties
    priority: Priority = Field(default=Priority.MEDIUM, description="Event priority")
    requires_response: bool = Field(default=False, description="Requires response")
    expires_at: Optional[datetime] = Field(None, description="Event expiration")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation time")
    processed_at: Optional[datetime] = Field(None, description="Processing time")
    
    @validator('event_type')
    def validate_event_type(cls, v):
        """Validate event type."""
        allowed_types = [
            "task_assigned", "task_completed", "task_failed", "progress_update",
            "resource_request", "coordination_needed", "alert", "status_change"
        ]
        if v not in allowed_types:
            raise ValueError(f"Event type must be one of: {allowed_types}")
        return v 