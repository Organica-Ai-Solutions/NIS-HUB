"""
NIS HUB Client

Main client class for connecting NIS nodes to the central HUB system.
Provides high-level interface for registration, heartbeat, memory sync, and missions.
"""

import asyncio
import json
import uuid
from typing import Dict, List, Optional, Any, Callable, Union
from datetime import datetime, timedelta
import logging
from pathlib import Path

import httpx
import websockets
from pydantic import BaseModel, Field
from tenacity import retry, stop_after_attempt, wait_exponential

from .config import HubConfig
from .memory import MemoryManager
from .missions import MissionCoordinator
from .exceptions import (
    NISHubError, ConnectionError, RegistrationError, 
    HeartbeatError, AuthenticationError
)

logger = logging.getLogger(__name__)

class NodeCapability(str):
    """Node capability constants."""
    DATA_PROCESSING = "data_processing"
    MACHINE_LEARNING = "machine_learning"
    REAL_TIME_ANALYSIS = "real_time_analysis"
    MEMORY_STORAGE = "memory_storage"
    COORDINATION = "coordination"
    VISUALIZATION = "visualization"
    COMMUNICATION = "communication"

class NodeType(str):
    """Node type constants."""
    EXOPLANET_ANALYSIS = "exoplanet_analysis"
    DRONE_CONTROL = "drone_control"
    ARCHAEOLOGICAL = "archaeological"
    WEATHER_ANALYSIS = "weather_analysis"
    GENERAL_AGENT = "general_agent"
    SUPERVISOR = "supervisor"
    CUSTOM = "custom"

class NodeStatus(BaseModel):
    """Node status information for heartbeat."""
    status: str = "healthy"
    cpu_usage: Optional[float] = None
    memory_usage: Optional[float] = None
    disk_usage: Optional[float] = None
    active_tasks: int = 0
    completed_tasks: int = 0
    error_count: int = 0
    details: Dict[str, Any] = Field(default_factory=dict)

class NISNode:
    """
    Main client class for connecting to NIS HUB.
    
    This class provides a high-level interface for NIS nodes to:
    - Register with the central HUB
    - Send regular heartbeats
    - Synchronize memory entries
    - Participate in coordinated missions
    - Receive real-time updates via WebSocket
    
    Example:
        node = NISNode(
            name="nis-x-exoplanet",
            node_type=NodeType.EXOPLANET_ANALYSIS,
            capabilities=[NodeCapability.DATA_PROCESSING, NodeCapability.MACHINE_LEARNING],
            hub_url="http://localhost:8000"
        )
        
        await node.register()
        await node.start_heartbeat()
        node.start_websocket()
    """
    
    def __init__(
        self,
        name: str,
        node_type: str = NodeType.GENERAL_AGENT,
        capabilities: List[str] = None,
        hub_url: str = "http://localhost:8000",
        websocket_url: Optional[str] = None,
        config: Optional[HubConfig] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        heartbeat_interval: int = 30,
        max_memory_size: Optional[int] = None
    ):
        """
        Initialize NIS node client.
        
        Args:
            name: Unique name for this node
            node_type: Type of node (see NodeType constants)
            capabilities: List of node capabilities
            hub_url: URL of the NIS HUB server
            websocket_url: WebSocket URL (auto-generated if None)
            config: Optional configuration object
            description: Human-readable description
            metadata: Additional metadata dictionary
            heartbeat_interval: Heartbeat interval in seconds
            max_memory_size: Maximum memory size in MB
        """
        self.name = name
        self.node_type = node_type
        self.capabilities = capabilities or []
        self.description = description
        self.metadata = metadata or {}
        self.heartbeat_interval = heartbeat_interval
        self.max_memory_size = max_memory_size
        
        # Configuration
        self.config = config or HubConfig(hub_url=hub_url, websocket_url=websocket_url)
        
        # Node state
        self.node_id: Optional[str] = None
        self.registered = False
        self.connected = False
        
        # HTTP client
        self.http_client = httpx.AsyncClient(timeout=30.0)
        
        # WebSocket connection
        self.websocket: Optional[websockets.WebSocketServerProtocol] = None
        self.websocket_task: Optional[asyncio.Task] = None
        
        # Heartbeat task
        self.heartbeat_task: Optional[asyncio.Task] = None
        
        # Managers
        self.memory = MemoryManager(self)
        self.missions = MissionCoordinator(self)
        
        # Event handlers
        self.message_handlers: Dict[str, Callable] = {}
        self.event_handlers: Dict[str, List[Callable]] = {}
        
        # Node status
        self.status = NodeStatus()
        
        logger.info(f"NIS Node '{name}' initialized", extra={
            "node_name": name,
            "node_type": node_type,
            "hub_url": self.config.hub_url
        })
    
    async def register(self) -> str:
        """
        Register this node with the NIS HUB.
        
        Returns:
            Node ID assigned by the HUB
            
        Raises:
            RegistrationError: If registration fails
        """
        try:
            logger.info(f"Registering node '{self.name}' with NIS HUB")
            
            # Prepare registration data
            registration_data = {
                "name": self.name,
                "node_type": self.node_type,
                "version": "1.0.0",  # TODO: Get from package version
                "endpoint": f"http://localhost:8001",  # TODO: Make configurable
                "websocket_endpoint": self.config.websocket_url,
                "capabilities": self.capabilities,
                "description": self.description,
                "metadata": self.metadata,
                "heartbeat_interval": self.heartbeat_interval,
                "max_memory_size": self.max_memory_size
            }
            
            # Send registration request
            response = await self.http_client.post(
                f"{self.config.hub_url}/api/v1/nodes/register",
                json=registration_data
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    # Extract node ID from response message
                    message = result.get("message", "")
                    if "ID:" in message:
                        self.node_id = message.split("ID:")[-1].strip()
                    else:
                        self.node_id = f"node_{uuid.uuid4().hex[:8]}"
                    
                    self.registered = True
                    
                    logger.info(f"Node registered successfully with ID: {self.node_id}")
                    
                    # Trigger registration event
                    await self._trigger_event("registered", {"node_id": self.node_id})
                    
                    return self.node_id
                else:
                    raise RegistrationError(f"Registration failed: {result.get('message')}")
            else:
                raise RegistrationError(f"HTTP {response.status_code}: {response.text}")
                
        except httpx.RequestError as e:
            logger.error(f"Connection error during registration: {e}")
            raise RegistrationError(f"Connection error: {e}")
        except Exception as e:
            logger.error(f"Unexpected error during registration: {e}")
            raise RegistrationError(f"Registration failed: {e}")
    
    async def start_heartbeat(self):
        """
        Start sending regular heartbeat signals to the HUB.
        
        Raises:
            HeartbeatError: If heartbeat setup fails
        """
        if not self.registered:
            raise HeartbeatError("Node must be registered before starting heartbeat")
        
        if self.heartbeat_task and not self.heartbeat_task.done():
            logger.warning("Heartbeat already running")
            return
        
        logger.info(f"Starting heartbeat every {self.heartbeat_interval} seconds")
        
        self.heartbeat_task = asyncio.create_task(self._heartbeat_loop())
    
    async def stop_heartbeat(self):
        """Stop the heartbeat task."""
        if self.heartbeat_task:
            self.heartbeat_task.cancel()
            try:
                await self.heartbeat_task
            except asyncio.CancelledError:
                pass
            
            logger.info("Heartbeat stopped")
    
    async def start_websocket(self):
        """
        Start WebSocket connection for real-time communication.
        
        Raises:
            ConnectionError: If WebSocket connection fails
        """
        if not self.registered:
            raise ConnectionError("Node must be registered before starting WebSocket")
        
        if self.websocket_task and not self.websocket_task.done():
            logger.warning("WebSocket already running")
            return
        
        logger.info("Starting WebSocket connection")
        
        self.websocket_task = asyncio.create_task(self._websocket_loop())
    
    async def stop_websocket(self):
        """Stop the WebSocket connection."""
        if self.websocket_task:
            self.websocket_task.cancel()
            try:
                await self.websocket_task
            except asyncio.CancelledError:
                pass
        
        if self.websocket:
            await self.websocket.close()
            self.websocket = None
            self.connected = False
        
        logger.info("WebSocket connection stopped")
    
    async def send_status_update(self, status_data: Optional[Dict[str, Any]] = None):
        """
        Send a status update via WebSocket.
        
        Args:
            status_data: Optional status data to include
        """
        if not self.websocket:
            logger.warning("No WebSocket connection for status update")
            return
        
        # Update status
        if status_data:
            for key, value in status_data.items():
                if hasattr(self.status, key):
                    setattr(self.status, key, value)
        
        message = {
            "message_type": "status_update",
            "data": {
                "node_id": self.node_id,
                "status": self.status.dict(),
                "timestamp": datetime.utcnow().isoformat()
            }
        }
        
        try:
            await self.websocket.send(json.dumps(message))
            logger.debug("Status update sent")
        except Exception as e:
            logger.error(f"Failed to send status update: {e}")
    
    def on_message(self, message_type: str):
        """
        Decorator for registering message handlers.
        
        Usage:
            @node.on_message("task_assigned")
            async def handle_task(data):
                print(f"Received task: {data}")
        """
        def decorator(func: Callable):
            self.message_handlers[message_type] = func
            return func
        return decorator
    
    def on_event(self, event_type: str):
        """
        Decorator for registering event handlers.
        
        Usage:
            @node.on_event("connected")
            async def on_connected():
                print("Connected to HUB!")
        """
        def decorator(func: Callable):
            if event_type not in self.event_handlers:
                self.event_handlers[event_type] = []
            self.event_handlers[event_type].append(func)
            return func
        return decorator
    
    async def shutdown(self):
        """Gracefully shutdown the node and cleanup resources."""
        logger.info(f"Shutting down node '{self.name}'")
        
        # Stop background tasks
        await self.stop_heartbeat()
        await self.stop_websocket()
        
        # Close HTTP client
        await self.http_client.aclose()
        
        # Trigger shutdown event
        await self._trigger_event("shutdown")
        
        logger.info("Node shutdown complete")
    
    # Internal methods
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=10))
    async def _send_heartbeat(self):
        """Send a single heartbeat to the HUB."""
        try:
            heartbeat_data = {
                "node_id": self.node_id,
                "status": self.status.status,
                "timestamp": datetime.utcnow().isoformat(),
                "cpu_usage": self.status.cpu_usage,
                "memory_usage": self.status.memory_usage,
                "disk_usage": self.status.disk_usage,
                "active_tasks": self.status.active_tasks,
                "completed_tasks": self.status.completed_tasks,
                "error_count": self.status.error_count,
                "details": self.status.details
            }
            
            response = await self.http_client.post(
                f"{self.config.hub_url}/api/v1/nodes/heartbeat",
                json=heartbeat_data
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    logger.debug("Heartbeat sent successfully")
                    await self._trigger_event("heartbeat_sent")
                else:
                    logger.warning(f"Heartbeat failed: {result.get('message')}")
            else:
                logger.error(f"Heartbeat HTTP error: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Heartbeat error: {e}")
            raise
    
    async def _heartbeat_loop(self):
        """Background task for sending regular heartbeats."""
        while True:
            try:
                await self._send_heartbeat()
                await asyncio.sleep(self.heartbeat_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Heartbeat loop error: {e}")
                await asyncio.sleep(self.heartbeat_interval)
    
    async def _websocket_loop(self):
        """Background task for WebSocket communication."""
        while True:
            try:
                ws_url = f"{self.config.websocket_url}/ws?node_id={self.node_id}&node_type={self.node_type}"
                
                async with websockets.connect(ws_url) as websocket:
                    self.websocket = websocket
                    self.connected = True
                    
                    logger.info("WebSocket connected")
                    await self._trigger_event("connected")
                    
                    # Listen for messages
                    async for message in websocket:
                        try:
                            data = json.loads(message)
                            await self._handle_websocket_message(data)
                        except json.JSONDecodeError as e:
                            logger.error(f"Invalid JSON received: {e}")
                        except Exception as e:
                            logger.error(f"Message handling error: {e}")
                            
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"WebSocket connection error: {e}")
                self.connected = False
                await self._trigger_event("disconnected")
                
                # Retry connection after delay
                await asyncio.sleep(5)
    
    async def _handle_websocket_message(self, data: Dict[str, Any]):
        """Handle incoming WebSocket messages."""
        message_type = data.get("message_type")
        message_data = data.get("data", {})
        
        logger.debug(f"Received message: {message_type}")
        
        # Call registered handler if available
        if message_type in self.message_handlers:
            try:
                await self.message_handlers[message_type](message_data)
            except Exception as e:
                logger.error(f"Message handler error for {message_type}: {e}")
        
        # Handle built-in message types
        if message_type == "connection_established":
            logger.info("Connection established with HUB")
            
        elif message_type == "task_assigned":
            logger.info(f"Task assigned: {message_data.get('task_id')}")
            await self._trigger_event("task_assigned", message_data)
            
        elif message_type == "mission_created":
            logger.info(f"New mission created: {message_data.get('mission_id')}")
            await self._trigger_event("mission_created", message_data)
            
        elif message_type == "memory_notification":
            logger.debug("Memory notification received")
            await self._trigger_event("memory_updated", message_data)
            
        elif message_type == "ping":
            # Respond to ping
            await self.websocket.send(json.dumps({
                "message_type": "pong",
                "data": {"timestamp": datetime.utcnow().isoformat()}
            }))
    
    async def _trigger_event(self, event_type: str, data: Optional[Dict[str, Any]] = None):
        """Trigger registered event handlers."""
        if event_type in self.event_handlers:
            for handler in self.event_handlers[event_type]:
                try:
                    if data:
                        await handler(data)
                    else:
                        await handler()
                except Exception as e:
                    logger.error(f"Event handler error for {event_type}: {e}")
    
    def __repr__(self) -> str:
        return f"NISNode(name='{self.name}', type='{self.node_type}', registered={self.registered})" 