"""
WebSocket Manager for NIS HUB

Handles real-time communication between the HUB and connected nodes
using WebSocket connections for instant coordination and updates.
"""

import json
import asyncio
from typing import Dict, List, Set, Optional, Any, Callable
from datetime import datetime
import uuid
from fastapi import WebSocket, WebSocketDisconnect
from pydantic import BaseModel

from .logging_service import NISHubLogger

class WebSocketConnection(BaseModel):
    """WebSocket connection metadata."""
    connection_id: str
    websocket: WebSocket
    node_id: Optional[str] = None
    node_type: Optional[str] = None
    connected_at: datetime
    last_ping: Optional[datetime] = None
    
    class Config:
        arbitrary_types_allowed = True

class WebSocketMessage(BaseModel):
    """Standard WebSocket message format."""
    message_type: str
    data: Dict[str, Any]
    timestamp: datetime
    source_id: Optional[str] = None
    target_ids: Optional[List[str]] = None
    requires_ack: bool = False
    message_id: Optional[str] = None

class WebSocketManager:
    """
    Manages WebSocket connections for real-time communication.
    """
    
    def __init__(self):
        """Initialize WebSocket manager."""
        self.active_connections: Dict[str, WebSocketConnection] = {}
        self.node_connections: Dict[str, str] = {}  # node_id -> connection_id
        self.connection_groups: Dict[str, Set[str]] = {}  # group -> connection_ids
        self.message_handlers: Dict[str, Callable] = {}
        
        self.logger = NISHubLogger("websocket_manager")
        
        # Start background tasks
        self._ping_task = None
        self._cleanup_task = None
    
    async def start_background_tasks(self):
        """Start background maintenance tasks."""
        self._ping_task = asyncio.create_task(self._ping_connections())
        self._cleanup_task = asyncio.create_task(self._cleanup_stale_connections())
        
        self.logger.info("WebSocket background tasks started")
    
    async def stop_background_tasks(self):
        """Stop background maintenance tasks."""
        if self._ping_task:
            self._ping_task.cancel()
        if self._cleanup_task:
            self._cleanup_task.cancel()
        
        self.logger.info("WebSocket background tasks stopped")
    
    async def connect(self, websocket: WebSocket, node_id: Optional[str] = None, node_type: Optional[str] = None) -> str:
        """
        Accept a new WebSocket connection.
        
        Args:
            websocket: WebSocket connection
            node_id: Optional node identifier
            node_type: Optional node type
            
        Returns:
            Connection ID
        """
        await websocket.accept()
        
        connection_id = self._generate_connection_id()
        connection = WebSocketConnection(
            connection_id=connection_id,
            websocket=websocket,
            node_id=node_id,
            node_type=node_type,
            connected_at=datetime.utcnow()
        )
        
        self.active_connections[connection_id] = connection
        
        # Map node to connection if node_id provided
        if node_id:
            self.node_connections[node_id] = connection_id
            
            # Add to node type group
            if node_type:
                if node_type not in self.connection_groups:
                    self.connection_groups[node_type] = set()
                self.connection_groups[node_type].add(connection_id)
        
        self.logger.info("WebSocket connection established",
                        connection_id=connection_id,
                        node_id=node_id,
                        node_type=node_type)
        
        # Send welcome message
        await self.send_to_connection(connection_id, {
            "message_type": "connection_established",
            "data": {
                "connection_id": connection_id,
                "server_time": datetime.utcnow().isoformat(),
                "message": "Welcome to NIS HUB"
            }
        })
        
        return connection_id
    
    async def disconnect(self, connection_id: str):
        """
        Handle WebSocket disconnection.
        
        Args:
            connection_id: Connection to disconnect
        """
        if connection_id in self.active_connections:
            connection = self.active_connections[connection_id]
            
            # Remove from node mapping
            if connection.node_id and connection.node_id in self.node_connections:
                del self.node_connections[connection.node_id]
            
            # Remove from groups
            if connection.node_type and connection.node_type in self.connection_groups:
                self.connection_groups[connection.node_type].discard(connection_id)
                if not self.connection_groups[connection.node_type]:
                    del self.connection_groups[connection.node_type]
            
            # Close WebSocket
            try:
                await connection.websocket.close()
            except Exception:
                pass  # Connection might already be closed
            
            # Remove from active connections
            del self.active_connections[connection_id]
            
            self.logger.info("WebSocket connection closed",
                           connection_id=connection_id,
                           node_id=connection.node_id)
    
    async def send_to_connection(self, connection_id: str, message: Dict[str, Any]) -> bool:
        """
        Send message to specific connection.
        
        Args:
            connection_id: Target connection ID
            message: Message to send
            
        Returns:
            True if sent successfully
        """
        if connection_id not in self.active_connections:
            return False
        
        connection = self.active_connections[connection_id]
        
        try:
            # Format message
            ws_message = WebSocketMessage(
                message_type=message.get("message_type", "unknown"),
                data=message.get("data", {}),
                timestamp=datetime.utcnow(),
                message_id=str(uuid.uuid4())
            )
            
            # Send message
            await connection.websocket.send_text(ws_message.json())
            
            self.logger.debug("Message sent to connection",
                            connection_id=connection_id,
                            message_type=ws_message.message_type)
            
            return True
            
        except Exception as e:
            self.logger.error("Failed to send message to connection",
                            connection_id=connection_id,
                            error=e)
            
            # Disconnect on error
            await self.disconnect(connection_id)
            return False
    
    async def send_to_node(self, node_id: str, message: Dict[str, Any]) -> bool:
        """
        Send message to specific node.
        
        Args:
            node_id: Target node ID
            message: Message to send
            
        Returns:
            True if sent successfully
        """
        if node_id not in self.node_connections:
            self.logger.warning("Node not connected", node_id=node_id)
            return False
        
        connection_id = self.node_connections[node_id]
        return await self.send_to_connection(connection_id, message)
    
    async def broadcast_to_all(self, message: Dict[str, Any], exclude_connections: Optional[List[str]] = None) -> int:
        """
        Broadcast message to all connections.
        
        Args:
            message: Message to broadcast
            exclude_connections: Connection IDs to exclude
            
        Returns:
            Number of connections message was sent to
        """
        exclude_set = set(exclude_connections or [])
        sent_count = 0
        
        for connection_id in list(self.active_connections.keys()):
            if connection_id not in exclude_set:
                if await self.send_to_connection(connection_id, message):
                    sent_count += 1
        
        self.logger.info("Message broadcasted to all",
                       message_type=message.get("message_type"),
                       recipients=sent_count)
        
        return sent_count
    
    async def broadcast_to_group(self, group: str, message: Dict[str, Any]) -> int:
        """
        Broadcast message to specific group.
        
        Args:
            group: Group name (typically node type)
            message: Message to broadcast
            
        Returns:
            Number of connections message was sent to
        """
        if group not in self.connection_groups:
            return 0
        
        sent_count = 0
        for connection_id in list(self.connection_groups[group]):
            if await self.send_to_connection(connection_id, message):
                sent_count += 1
        
        self.logger.info("Message broadcasted to group",
                       group=group,
                       message_type=message.get("message_type"),
                       recipients=sent_count)
        
        return sent_count
    
    async def receive_message(self, connection_id: str) -> Optional[Dict[str, Any]]:
        """
        Receive message from connection.
        
        Args:
            connection_id: Source connection ID
            
        Returns:
            Received message or None
        """
        if connection_id not in self.active_connections:
            return None
        
        connection = self.active_connections[connection_id]
        
        try:
            # Receive raw message
            raw_message = await connection.websocket.receive_text()
            
            # Parse message
            message_data = json.loads(raw_message)
            
            # Update last ping if it's a ping message
            if message_data.get("message_type") == "ping":
                connection.last_ping = datetime.utcnow()
                
                # Send pong response
                await self.send_to_connection(connection_id, {
                    "message_type": "pong",
                    "data": {"timestamp": datetime.utcnow().isoformat()}
                })
            
            self.logger.debug("Message received from connection",
                            connection_id=connection_id,
                            message_type=message_data.get("message_type"))
            
            return message_data
            
        except WebSocketDisconnect:
            await self.disconnect(connection_id)
            return None
        except json.JSONDecodeError as e:
            self.logger.error("Invalid JSON received",
                            connection_id=connection_id,
                            error=e)
            return None
        except Exception as e:
            self.logger.error("Error receiving message",
                            connection_id=connection_id,
                            error=e)
            await self.disconnect(connection_id)
            return None
    
    def register_message_handler(self, message_type: str, handler: Callable):
        """
        Register a handler for specific message type.
        
        Args:
            message_type: Type of message to handle
            handler: Async function to handle the message
        """
        self.message_handlers[message_type] = handler
        self.logger.info("Message handler registered", message_type=message_type)
    
    async def handle_message(self, connection_id: str, message: Dict[str, Any]):
        """
        Handle received message using registered handlers.
        
        Args:
            connection_id: Source connection ID
            message: Received message
        """
        message_type = message.get("message_type")
        
        if message_type in self.message_handlers:
            try:
                await self.message_handlers[message_type](connection_id, message)
            except Exception as e:
                self.logger.error("Error in message handler",
                                message_type=message_type,
                                connection_id=connection_id,
                                error=e)
        else:
            self.logger.warning("No handler for message type",
                              message_type=message_type,
                              connection_id=connection_id)
    
    def get_connection_info(self, connection_id: str) -> Optional[Dict[str, Any]]:
        """Get connection information."""
        if connection_id not in self.active_connections:
            return None
        
        connection = self.active_connections[connection_id]
        return {
            "connection_id": connection_id,
            "node_id": connection.node_id,
            "node_type": connection.node_type,
            "connected_at": connection.connected_at.isoformat(),
            "last_ping": connection.last_ping.isoformat() if connection.last_ping else None
        }
    
    def get_all_connections(self) -> List[Dict[str, Any]]:
        """Get information about all active connections."""
        return [
            self.get_connection_info(conn_id)
            for conn_id in self.active_connections.keys()
        ]
    
    def get_connection_stats(self) -> Dict[str, Any]:
        """Get connection statistics."""
        return {
            "total_connections": len(self.active_connections),
            "node_connections": len(self.node_connections),
            "connection_groups": {
                group: len(connections)
                for group, connections in self.connection_groups.items()
            },
            "registered_handlers": len(self.message_handlers)
        }
    
    async def _ping_connections(self):
        """Background task to ping all connections."""
        while True:
            try:
                await asyncio.sleep(30)  # Ping every 30 seconds
                
                for connection_id in list(self.active_connections.keys()):
                    await self.send_to_connection(connection_id, {
                        "message_type": "ping",
                        "data": {"timestamp": datetime.utcnow().isoformat()}
                    })
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error("Error in ping task", error=e)
    
    async def _cleanup_stale_connections(self):
        """Background task to cleanup stale connections."""
        while True:
            try:
                await asyncio.sleep(60)  # Check every minute
                
                now = datetime.utcnow()
                stale_connections = []
                
                for connection_id, connection in self.active_connections.items():
                    # Consider connection stale if no ping for 5 minutes
                    if connection.last_ping:
                        time_since_ping = (now - connection.last_ping).total_seconds()
                        if time_since_ping > 300:  # 5 minutes
                            stale_connections.append(connection_id)
                    else:
                        # No ping received yet, check connection time
                        time_since_connect = (now - connection.connected_at).total_seconds()
                        if time_since_connect > 120:  # 2 minutes without ping
                            stale_connections.append(connection_id)
                
                # Disconnect stale connections
                for connection_id in stale_connections:
                    self.logger.warning("Disconnecting stale connection",
                                      connection_id=connection_id)
                    await self.disconnect(connection_id)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error("Error in cleanup task", error=e)
    
    def _generate_connection_id(self) -> str:
        """Generate unique connection ID."""
        return f"ws_{uuid.uuid4().hex[:12]}" 