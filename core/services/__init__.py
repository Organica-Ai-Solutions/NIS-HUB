"""
NIS HUB Core Services

This package contains all service classes for the NIS HUB system,
including Redis management, WebSocket handling, logging, and NIS Protocol v3.1 services.
"""

from .redis_service import RedisService
from .websocket_manager import WebSocketManager
from .logging_service import setup_logging, get_logger
from .node_service import NodeService
from .memory_service import MemoryService
from .mission_service import MissionService

# NIS Protocol v3.1 Services
from .consciousness_service import ConsciousnessService
from .pinn_service import PINNService
from .kan_service import KANService
from .bitnet_service import BitNetService
from .protocol_bridge_service import ProtocolBridgeService
from .mcp_adapter import MCPAdapter
from .atoa_handler import ATOAHandler
from .openai_tools_bridge import OpenAIToolsBridge

__all__ = [
    # Core services
    "RedisService",
    "WebSocketManager",
    "setup_logging",
    "get_logger",
    "NodeService",
    "MemoryService",
    "MissionService",
    
    # NIS Protocol v3.1 services
    "ConsciousnessService",
    "PINNService", 
    "KANService",
    "BitNetService",
    "ProtocolBridgeService",
    
    # External protocol services
    "MCPAdapter",
    "ATOAHandler",
    "OpenAIToolsBridge"
] 