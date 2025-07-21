"""
Memory Models for NIS HUB

Data structures for memory synchronization, querying, and broadcast operations
between nodes in the NIS ecosystem.
"""

from typing import Dict, Any, Optional, List, Union
from datetime import datetime
from pydantic import BaseModel, Field, validator
from enum import Enum

from .base_models import Priority

class MemoryType(str, Enum):
    """Types of memory entries in the shared memory system."""
    SENSOR_DATA = "sensor_data"
    ANALYSIS_RESULT = "analysis_result"
    MODEL_OUTPUT = "model_output"
    COORDINATION_STATE = "coordination_state"
    AGENT_DECISION = "agent_decision"
    KNOWLEDGE_GRAPH = "knowledge_graph"
    TEMPORAL_SEQUENCE = "temporal_sequence"
    CROSS_DOMAIN_INSIGHT = "cross_domain_insight"

class MemoryScope(str, Enum):
    """Scope of memory accessibility."""
    PRIVATE = "private"          # Only accessible to the creating node
    DOMAIN = "domain"            # Accessible to nodes in the same domain
    PUBLIC = "public"            # Accessible to all nodes
    SUPERVISOR = "supervisor"    # Accessible to supervisor agents only

class MemoryFormat(str, Enum):
    """Data format for memory entries."""
    JSON = "json"
    NUMPY_ARRAY = "numpy_array"
    TENSOR = "tensor"
    TEXT = "text"
    BINARY = "binary"
    VECTOR_EMBEDDING = "vector_embedding"

class MemoryEntry(BaseModel):
    """Individual memory entry in the shared memory system."""
    entry_id: Optional[str] = Field(None, description="Unique entry identifier (auto-generated)")
    source_node_id: str = Field(..., description="ID of the node that created this entry")
    
    # Memory classification
    memory_type: MemoryType = Field(..., description="Type of memory entry")
    scope: MemoryScope = Field(default=MemoryScope.DOMAIN, description="Access scope")
    priority: Priority = Field(default=Priority.MEDIUM, description="Entry priority")
    
    # Content
    title: str = Field(..., description="Human-readable title", max_length=200)
    description: Optional[str] = Field(None, description="Detailed description", max_length=1000)
    data: Dict[str, Any] = Field(..., description="The actual memory data")
    data_format: MemoryFormat = Field(default=MemoryFormat.JSON, description="Data format")
    
    # Metadata
    tags: List[str] = Field(default=[], description="Searchable tags")
    domain: str = Field(..., description="Domain (e.g., 'exoplanet', 'drone', 'weather')")
    context: Dict[str, Any] = Field(default={}, description="Additional context information")
    
    # Temporal information
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    expires_at: Optional[datetime] = Field(None, description="Expiration timestamp")
    last_accessed: Optional[datetime] = Field(None, description="Last access timestamp")
    
    # Relationships
    parent_entry_id: Optional[str] = Field(None, description="Parent entry for hierarchical data")
    related_entry_ids: List[str] = Field(default=[], description="Related entry IDs")
    
    # Performance
    access_count: int = Field(default=0, description="Number of times accessed")
    size_bytes: Optional[int] = Field(None, description="Data size in bytes")
    
    @validator('tags')
    def validate_tags(cls, v):
        """Validate tags format."""
        return [tag.lower().strip() for tag in v if tag.strip()]

class MemorySync(BaseModel):
    """Memory synchronization request from a node."""
    node_id: str = Field(..., description="ID of the requesting node")
    entries: List[MemoryEntry] = Field(..., description="Memory entries to sync")
    sync_mode: str = Field(default="append", description="Sync mode: 'append', 'update', 'replace'")
    batch_id: Optional[str] = Field(None, description="Batch identifier for related entries")
    
    @validator('sync_mode')
    def validate_sync_mode(cls, v):
        """Validate sync mode."""
        allowed_modes = ["append", "update", "replace"]
        if v not in allowed_modes:
            raise ValueError(f"Sync mode must be one of: {allowed_modes}")
        return v

class MemoryQuery(BaseModel):
    """Query structure for retrieving memory entries."""
    requesting_node_id: str = Field(..., description="ID of the requesting node")
    
    # Query filters
    entry_ids: Optional[List[str]] = Field(None, description="Specific entry IDs to retrieve")
    source_node_ids: Optional[List[str]] = Field(None, description="Filter by source nodes")
    memory_types: Optional[List[MemoryType]] = Field(None, description="Filter by memory types")
    domains: Optional[List[str]] = Field(None, description="Filter by domains")
    tags: Optional[List[str]] = Field(None, description="Filter by tags (AND logic)")
    
    # Text search
    search_text: Optional[str] = Field(None, description="Full-text search in title/description")
    
    # Temporal filters
    created_after: Optional[datetime] = Field(None, description="Created after timestamp")
    created_before: Optional[datetime] = Field(None, description="Created before timestamp")
    accessed_after: Optional[datetime] = Field(None, description="Last accessed after timestamp")
    
    # Vector similarity search
    vector_query: Optional[List[float]] = Field(None, description="Vector for similarity search")
    similarity_threshold: float = Field(default=0.7, description="Similarity threshold", ge=0, le=1)
    
    # Pagination and limits
    page: int = Field(default=1, description="Page number", ge=1)
    page_size: int = Field(default=20, description="Page size", ge=1, le=100)
    sort_by: str = Field(default="created_at", description="Sort field")
    sort_order: str = Field(default="desc", description="Sort order: 'asc' or 'desc'")
    
    # Response options
    include_data: bool = Field(default=True, description="Include full data in response")
    include_metadata: bool = Field(default=True, description="Include metadata")
    
    @validator('sort_order')
    def validate_sort_order(cls, v):
        """Validate sort order."""
        if v not in ["asc", "desc"]:
            raise ValueError("Sort order must be 'asc' or 'desc'")
        return v

class MemoryResponse(BaseModel):
    """Response structure for memory queries."""
    success: bool = Field(..., description="Whether the query was successful")
    message: str = Field(..., description="Response message")
    
    # Results
    entries: List[MemoryEntry] = Field(..., description="Retrieved memory entries")
    total_count: int = Field(..., description="Total number of matching entries")
    
    # Pagination
    page: int = Field(..., description="Current page")
    page_size: int = Field(..., description="Page size")
    total_pages: int = Field(..., description="Total pages")
    
    # Query metadata
    query_time_ms: float = Field(..., description="Query execution time")
    from_cache: bool = Field(default=False, description="Whether results came from cache")

class MemoryBroadcast(BaseModel):
    """Broadcast message to distribute memory updates to relevant nodes."""
    source_node_id: str = Field(..., description="ID of the broadcasting node")
    message_type: str = Field(..., description="Type of broadcast message")
    
    # Target specification
    target_node_ids: Optional[List[str]] = Field(None, description="Specific target nodes")
    target_domains: Optional[List[str]] = Field(None, description="Target domains")
    target_capabilities: Optional[List[str]] = Field(None, description="Target capabilities")
    
    # Content
    title: str = Field(..., description="Broadcast title")
    content: Dict[str, Any] = Field(..., description="Broadcast content")
    priority: Priority = Field(default=Priority.MEDIUM, description="Message priority")
    
    # Options
    requires_acknowledgment: bool = Field(default=False, description="Whether ACK is required")
    expires_at: Optional[datetime] = Field(None, description="Message expiration")
    
    @validator('message_type')
    def validate_message_type(cls, v):
        """Validate message type."""
        allowed_types = [
            "memory_update", "analysis_complete", "alert", 
            "coordination_request", "status_change", "custom"
        ]
        if v not in allowed_types:
            raise ValueError(f"Message type must be one of: {allowed_types}")
        return v

class MemoryStats(BaseModel):
    """Memory system statistics."""
    total_entries: int = Field(..., description="Total number of memory entries")
    total_size_mb: float = Field(..., description="Total memory size in MB")
    
    # By type
    entries_by_type: Dict[str, int] = Field(..., description="Entry count by memory type")
    entries_by_domain: Dict[str, int] = Field(..., description="Entry count by domain")
    entries_by_scope: Dict[str, int] = Field(..., description="Entry count by scope")
    
    # Performance
    avg_query_time_ms: float = Field(..., description="Average query time")
    cache_hit_rate: float = Field(..., description="Cache hit rate percentage")
    
    # Recent activity
    entries_created_last_hour: int = Field(..., description="Entries created in last hour")
    entries_accessed_last_hour: int = Field(..., description="Entries accessed in last hour")
    
    # Top contributors
    top_contributing_nodes: List[Dict[str, Any]] = Field(..., description="Top nodes by entry count")

class MemoryHealth(BaseModel):
    """Memory system health status."""
    status: str = Field(..., description="Overall health status")
    redis_connected: bool = Field(..., description="Redis connection status")
    vector_db_connected: bool = Field(..., description="Vector database connection status")
    
    # Performance indicators
    memory_usage_percent: float = Field(..., description="Memory usage percentage")
    disk_usage_percent: float = Field(..., description="Disk usage percentage")
    avg_response_time_ms: float = Field(..., description="Average response time")
    
    # Issues
    warnings: List[str] = Field(default=[], description="System warnings")
    errors: List[str] = Field(default=[], description="System errors") 