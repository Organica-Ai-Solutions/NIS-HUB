"""
Configuration management for NIS HUB SDK.
"""

from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class NISHubConfig(BaseModel):
    """Configuration for connecting to NIS HUB."""
    
    hub_url: str = Field(default="http://localhost:8000", description="NIS HUB server URL")
    websocket_url: Optional[str] = Field(None, description="WebSocket URL (auto-generated if None)")
    api_key: Optional[str] = Field(None, description="API key for authentication")
    timeout: int = Field(default=30, description="Request timeout in seconds")
    retry_attempts: int = Field(default=3, description="Number of retry attempts")
    heartbeat_interval: int = Field(default=30, description="Heartbeat interval in seconds")
    
    # Protocol-specific configuration
    protocol_config: Dict[str, Any] = Field(default_factory=dict, description="Protocol-specific configuration")
    
    # NIS v3.1 unified pipeline configuration
    enable_consciousness: bool = Field(default=True, description="Enable consciousness validation")
    enable_pinn_validation: bool = Field(default=True, description="Enable PINN physics validation")
    enable_kan_interpretation: bool = Field(default=True, description="Enable KAN interpretation")
    enable_safety_check: bool = Field(default=True, description="Enable safety validation")
    
    def __post_init__(self):
        """Post-initialization to set derived values."""
        if self.websocket_url is None:
            # Convert HTTP URL to WebSocket URL
            self.websocket_url = self.hub_url.replace("http://", "ws://").replace("https://", "wss://")
    
    class Config:
        """Pydantic configuration."""
        validate_assignment = True 