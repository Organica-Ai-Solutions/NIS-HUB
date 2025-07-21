"""
NIS HUB SDK - Python Client Library

This package provides a simple and powerful SDK for connecting NIS nodes 
to the central NIS HUB coordination system.

Basic Usage:
    from nis_hub_sdk import NISNode
    
    node = NISNode(
        name="my-nis-node",
        node_type="exoplanet_analysis",
        hub_url="http://localhost:8000"
    )
    
    await node.register()
    await node.start_heartbeat()
"""

__version__ = "1.0.0"
__author__ = "Organica AI Solutions"

from .client import NISNode
from .memory import MemoryManager
from .missions import MissionCoordinator
from .config import HubConfig
from .exceptions import (
    NISHubError,
    ConnectionError,
    AuthenticationError,
    RegistrationError,
    HeartbeatError,
    MemoryError,
    MissionError
)

__all__ = [
    # Core classes
    "NISNode",
    "MemoryManager", 
    "MissionCoordinator",
    "HubConfig",
    
    # Exceptions
    "NISHubError",
    "ConnectionError",
    "AuthenticationError",
    "RegistrationError",
    "HeartbeatError",
    "MemoryError",
    "MissionError",
    
    # Version info
    "__version__",
    "__author__"
] 