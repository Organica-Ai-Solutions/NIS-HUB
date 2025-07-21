"""
Base Models for NIS HUB

Common data structures and response patterns used across the system.
"""

from typing import Any, Dict, List, Optional, Generic, TypeVar
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum

T = TypeVar('T')

class BaseResponse(BaseModel):
    """Standard response structure for all API endpoints."""
    success: bool = Field(..., description="Whether the operation was successful")
    message: str = Field(..., description="Human-readable message")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class ErrorResponse(BaseResponse):
    """Error response structure with additional error details."""
    success: bool = Field(default=False, description="Always false for error responses")
    error_code: str = Field(..., description="Machine-readable error code")
    error_details: Optional[Dict[str, Any]] = Field(None, description="Additional error context")

class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response structure for list endpoints."""
    items: List[T] = Field(..., description="List of items for current page")
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Number of items per page")
    total_pages: int = Field(..., description="Total number of pages")
    has_next: bool = Field(..., description="Whether there is a next page")
    has_previous: bool = Field(..., description="Whether there is a previous page")

class SystemStatus(str, Enum):
    """System operational status levels."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    CRITICAL = "critical"
    MAINTENANCE = "maintenance"
    OFFLINE = "offline"

class Priority(str, Enum):
    """Priority levels for missions and operations."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    EMERGENCY = "emergency"

class ConnectionStatus(str, Enum):
    """Connection status for nodes and services."""
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    ERROR = "error"
    TIMEOUT = "timeout" 