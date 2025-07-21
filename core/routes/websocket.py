"""
WebSocket API Router for NIS HUB

Handles WebSocket connections and real-time communication
between the HUB and connected nodes.
"""

import json
import asyncio
from typing import Optional, Dict, Any
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Request, Query
from datetime import datetime

from services.logging_service import NISHubLogger

router = APIRouter()
logger = NISHubLogger("websocket_api")

async def get_ws_manager(request: Request):
    """Dependency to get WebSocket manager from app state."""
    return request.app.state.ws_manager

async def get_redis_service(request: Request):
    """Dependency to get Redis service from app state."""
    return request.app.state.redis

@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    node_id: Optional[str] = Query(None, description="Node ID for identification"),
    node_type: Optional[str] = Query(None, description="Type of node"),
    ws_manager = Depends(get_ws_manager),
    redis_service = Depends(get_redis_service)
):
    """
    Main WebSocket endpoint for real-time communication.
    
    This endpoint handles WebSocket connections from nodes and provides
    real-time bidirectional communication for coordination and updates.
    """
    connection_id = None
    
    try:
        # Establish WebSocket connection
        connection_id = await ws_manager.connect(
            websocket=websocket,
            node_id=node_id,
            node_type=node_type
        )
        
        logger.info("WebSocket connection established",
                   connection_id=connection_id,
                   node_id=node_id,
                   node_type=node_type)
        
        # Register message handlers
        await _register_message_handlers(ws_manager, redis_service)
        
        # Main message loop
        while True:
            try:
                # Receive message from client
                message = await ws_manager.receive_message(connection_id)
                
                if message:
                    # Handle the message
                    await ws_manager.handle_message(connection_id, message)
                else:
                    # Connection was closed
                    break
                    
            except WebSocketDisconnect:
                logger.info("WebSocket client disconnected",
                           connection_id=connection_id,
                           node_id=node_id)
                break
                
            except Exception as e:
                logger.error("Error in WebSocket message loop",
                           connection_id=connection_id,
                           error=e)
                # Send error response
                await ws_manager.send_to_connection(connection_id, {
                    "message_type": "error",
                    "data": {
                        "error": "Message processing failed",
                        "details": str(e)
                    }
                })
    
    except Exception as e:
        logger.error("WebSocket connection error",
                    connection_id=connection_id,
                    node_id=node_id,
                    error=e)
    
    finally:
        # Clean up connection
        if connection_id:
            await ws_manager.disconnect(connection_id)

@router.websocket("/ws/dashboard")
async def dashboard_websocket(
    websocket: WebSocket,
    ws_manager = Depends(get_ws_manager),
    redis_service = Depends(get_redis_service)
):
    """
    WebSocket endpoint specifically for dashboard connections.
    
    Provides real-time updates for the NIS HUB dashboard including
    system status, node activities, and mission progress.
    """
    connection_id = None
    
    try:
        # Establish dashboard WebSocket connection
        connection_id = await ws_manager.connect(
            websocket=websocket,
            node_id="dashboard",
            node_type="dashboard"
        )
        
        logger.info("Dashboard WebSocket connection established",
                   connection_id=connection_id)
        
        # Send initial dashboard data
        await _send_dashboard_data(ws_manager, connection_id, redis_service)
        
        # Register dashboard-specific handlers
        await _register_dashboard_handlers(ws_manager, redis_service)
        
        # Dashboard message loop
        while True:
            try:
                message = await ws_manager.receive_message(connection_id)
                
                if message:
                    await _handle_dashboard_message(
                        ws_manager, connection_id, message, redis_service
                    )
                else:
                    break
                    
            except WebSocketDisconnect:
                logger.info("Dashboard WebSocket disconnected",
                           connection_id=connection_id)
                break
                
            except Exception as e:
                logger.error("Error in dashboard WebSocket loop",
                           connection_id=connection_id,
                           error=e)
    
    except Exception as e:
        logger.error("Dashboard WebSocket connection error",
                    connection_id=connection_id,
                    error=e)
    
    finally:
        if connection_id:
            await ws_manager.disconnect(connection_id)

# Message Handlers

async def _register_message_handlers(ws_manager, redis_service):
    """Register message handlers for different message types."""
    
    async def handle_node_registration(connection_id: str, message: Dict[str, Any]):
        """Handle node registration via WebSocket."""
        try:
            data = message.get("data", {})
            
            # Update connection with node info
            connection_info = ws_manager.get_connection_info(connection_id)
            if connection_info:
                # Register or update node in Redis
                await redis_service.register_node(data)
                
                # Send confirmation
                await ws_manager.send_to_connection(connection_id, {
                    "message_type": "registration_confirmed",
                    "data": {
                        "node_id": data.get("node_id"),
                        "status": "registered",
                        "timestamp": datetime.utcnow().isoformat()
                    }
                })
                
                logger.info("Node registered via WebSocket",
                           connection_id=connection_id,
                           node_id=data.get("node_id"))
        
        except Exception as e:
            logger.error("Failed to handle node registration",
                        connection_id=connection_id,
                        error=e)
    
    async def handle_heartbeat(connection_id: str, message: Dict[str, Any]):
        """Handle heartbeat messages."""
        try:
            data = message.get("data", {})
            node_id = data.get("node_id")
            
            if node_id:
                # Update heartbeat in Redis
                await redis_service.update_node_heartbeat(node_id, data)
                
                # Send heartbeat acknowledgment
                await ws_manager.send_to_connection(connection_id, {
                    "message_type": "heartbeat_ack",
                    "data": {
                        "timestamp": datetime.utcnow().isoformat(),
                        "status": "received"
                    }
                })
        
        except Exception as e:
            logger.error("Failed to handle heartbeat",
                        connection_id=connection_id,
                        error=e)
    
    async def handle_memory_notification(connection_id: str, message: Dict[str, Any]):
        """Handle memory update notifications."""
        try:
            data = message.get("data", {})
            
            # Broadcast memory notification to relevant nodes
            await ws_manager.broadcast_to_all(
                {
                    "message_type": "memory_notification",
                    "data": data
                },
                exclude_connections=[connection_id]
            )
            
            logger.debug("Memory notification broadcasted",
                        connection_id=connection_id)
        
        except Exception as e:
            logger.error("Failed to handle memory notification",
                        connection_id=connection_id,
                        error=e)
    
    async def handle_mission_update(connection_id: str, message: Dict[str, Any]):
        """Handle mission update messages."""
        try:
            data = message.get("data", {})
            mission_id = data.get("mission_id")
            
            if mission_id:
                # Update mission in Redis if needed
                # This could trigger additional coordination logic
                
                # Broadcast mission update
                await ws_manager.broadcast_to_all(
                    {
                        "message_type": "mission_update",
                        "data": data
                    },
                    exclude_connections=[connection_id]
                )
                
                logger.debug("Mission update broadcasted",
                           mission_id=mission_id,
                           connection_id=connection_id)
        
        except Exception as e:
            logger.error("Failed to handle mission update",
                        connection_id=connection_id,
                        error=e)
    
    async def handle_status_request(connection_id: str, message: Dict[str, Any]):
        """Handle system status requests."""
        try:
            # Get system status data
            stats = ws_manager.get_connection_stats()
            node_count = await redis_service.get_node_count()
            mission_count = await redis_service.get_mission_count()
            
            status_data = {
                "timestamp": datetime.utcnow().isoformat(),
                "connections": stats,
                "nodes": {
                    "total_registered": node_count,
                    "active_connections": stats["node_connections"]
                },
                "missions": {
                    "active": mission_count
                },
                "memory": {
                    "usage_bytes": await redis_service.get_memory_size()
                }
            }
            
            await ws_manager.send_to_connection(connection_id, {
                "message_type": "status_response",
                "data": status_data
            })
            
        except Exception as e:
            logger.error("Failed to handle status request",
                        connection_id=connection_id,
                        error=e)
    
    # Register all handlers
    ws_manager.register_message_handler("node_registration", handle_node_registration)
    ws_manager.register_message_handler("heartbeat", handle_heartbeat)
    ws_manager.register_message_handler("memory_notification", handle_memory_notification)
    ws_manager.register_message_handler("mission_update", handle_mission_update)
    ws_manager.register_message_handler("status_request", handle_status_request)

async def _register_dashboard_handlers(ws_manager, redis_service):
    """Register handlers specific to dashboard connections."""
    
    async def handle_dashboard_command(connection_id: str, message: Dict[str, Any]):
        """Handle dashboard control commands."""
        try:
            data = message.get("data", {})
            command = data.get("command")
            
            if command == "refresh_data":
                await _send_dashboard_data(ws_manager, connection_id, redis_service)
            
            elif command == "broadcast_message":
                # Allow dashboard to broadcast messages to nodes
                broadcast_data = data.get("broadcast_data", {})
                await ws_manager.broadcast_to_all(broadcast_data)
                
                await ws_manager.send_to_connection(connection_id, {
                    "message_type": "command_response",
                    "data": {"status": "broadcast_sent"}
                })
            
            elif command == "system_reset":
                # Handle system reset commands
                logger.warning("System reset requested from dashboard",
                              connection_id=connection_id)
                
                await ws_manager.send_to_connection(connection_id, {
                    "message_type": "command_response", 
                    "data": {"status": "reset_initiated"}
                })
        
        except Exception as e:
            logger.error("Failed to handle dashboard command",
                        connection_id=connection_id,
                        error=e)
    
    ws_manager.register_message_handler("dashboard_command", handle_dashboard_command)

async def _send_dashboard_data(ws_manager, connection_id: str, redis_service):
    """Send comprehensive dashboard data to connection."""
    try:
        # Get all system data for dashboard
        nodes = await redis_service.get_all_nodes()
        connection_stats = ws_manager.get_connection_stats()
        
        # TODO: Get missions, memory stats, etc.
        
        dashboard_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "system_status": "operational",
            "nodes": {
                "total": len(nodes),
                "online": connection_stats["node_connections"],
                "details": nodes[:10]  # Send first 10 for overview
            },
            "connections": connection_stats,
            "missions": {
                "active": await redis_service.get_mission_count(),
                "details": []  # TODO: Get mission details
            },
            "memory": {
                "usage_bytes": await redis_service.get_memory_size(),
                "entries_count": 0  # TODO: Get memory entry count
            }
        }
        
        await ws_manager.send_to_connection(connection_id, {
            "message_type": "dashboard_data",
            "data": dashboard_data
        })
        
        logger.debug("Dashboard data sent", connection_id=connection_id)
        
    except Exception as e:
        logger.error("Failed to send dashboard data",
                    connection_id=connection_id,
                    error=e)

async def _handle_dashboard_message(
    ws_manager, 
    connection_id: str, 
    message: Dict[str, Any], 
    redis_service
):
    """Handle messages specifically from dashboard connections."""
    try:
        message_type = message.get("message_type")
        
        if message_type == "ping":
            # Dashboard ping - respond with pong
            await ws_manager.send_to_connection(connection_id, {
                "message_type": "pong",
                "data": {"timestamp": datetime.utcnow().isoformat()}
            })
        
        elif message_type == "subscription":
            # Dashboard wants to subscribe to specific events
            data = message.get("data", {})
            event_types = data.get("event_types", [])
            
            # TODO: Implement event subscription logic
            
            await ws_manager.send_to_connection(connection_id, {
                "message_type": "subscription_confirmed",
                "data": {"subscribed_events": event_types}
            })
        
        else:
            # Use standard message handling
            await ws_manager.handle_message(connection_id, message)
        
    except Exception as e:
        logger.error("Failed to handle dashboard message",
                    connection_id=connection_id,
                    message_type=message.get("message_type"),
                    error=e)

# WebSocket event broadcasting functions

async def broadcast_node_event(ws_manager, event_type: str, node_data: Dict[str, Any]):
    """Broadcast node-related events to all connections."""
    try:
        message = {
            "message_type": "node_event",
            "data": {
                "event_type": event_type,
                "node_data": node_data,
                "timestamp": datetime.utcnow().isoformat()
            }
        }
        
        await ws_manager.broadcast_to_all(message)
        
        logger.debug("Node event broadcasted",
                    event_type=event_type,
                    node_id=node_data.get("node_id"))
        
    except Exception as e:
        logger.error("Failed to broadcast node event",
                    event_type=event_type,
                    error=e)

async def broadcast_system_alert(ws_manager, alert_type: str, alert_data: Dict[str, Any]):
    """Broadcast system alerts to all connections."""
    try:
        message = {
            "message_type": "system_alert",
            "data": {
                "alert_type": alert_type,
                "alert_data": alert_data,
                "timestamp": datetime.utcnow().isoformat(),
                "priority": "high"
            }
        }
        
        await ws_manager.broadcast_to_all(message)
        
        logger.warning("System alert broadcasted",
                      alert_type=alert_type)
        
    except Exception as e:
        logger.error("Failed to broadcast system alert",
                    alert_type=alert_type,
                    error=e) 