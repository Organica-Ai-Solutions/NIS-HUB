"""
Nodes API Router for NIS HUB

Handles node registration, heartbeat monitoring, and status management.
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Request, BackgroundTasks
from fastapi.responses import JSONResponse
from datetime import datetime

from models.node_models import (
    NodeRegistration, NodeHeartbeat, NodeInfo, NodeStatus, 
    NodeUpdate, NodeStatsQuery, NodeType
)
from models.base_models import BaseResponse, ErrorResponse
from services.logging_service import NISHubLogger

router = APIRouter(prefix="/nodes")
logger = NISHubLogger("nodes_api")

async def get_redis_service(request: Request):
    """Dependency to get Redis service from app state."""
    return request.app.state.redis

async def get_ws_manager(request: Request):
    """Dependency to get WebSocket manager from app state."""
    return request.app.state.ws_manager

@router.post("/register", response_model=BaseResponse)
async def register_node(
    node_data: NodeRegistration,
    background_tasks: BackgroundTasks,
    redis_service = Depends(get_redis_service),
    ws_manager = Depends(get_ws_manager)
):
    """
    Register a new NIS node with the HUB.
    
    This endpoint allows NIS nodes to register themselves with the central HUB,
    providing their capabilities, endpoints, and configuration.
    """
    try:
        logger.api_request("POST", "/api/v1/nodes/register", node_name=node_data.name)
        
        # Convert Pydantic model to dict for Redis storage
        node_dict = node_data.dict()
        
        # Register node in Redis
        node_id = await redis_service.register_node(node_dict)
        
        # Broadcast node registration to other nodes
        background_tasks.add_task(
            ws_manager.broadcast_to_all,
            {
                "message_type": "node_registered",
                "data": {
                    "node_id": node_id,
                    "name": node_data.name,
                    "node_type": node_data.node_type,
                    "capabilities": node_data.capabilities
                }
            }
        )
        
        logger.info("Node registered successfully", 
                   node_id=node_id, 
                   name=node_data.name,
                   node_type=node_data.node_type)
        
        return BaseResponse(
            success=True,
            message=f"Node '{node_data.name}' registered successfully with ID: {node_id}",
            timestamp=datetime.utcnow()
        )
        
    except Exception as e:
        logger.error("Failed to register node", error=e)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to register node: {str(e)}"
        )

@router.post("/heartbeat", response_model=BaseResponse)
async def node_heartbeat(
    heartbeat_data: NodeHeartbeat,
    background_tasks: BackgroundTasks,
    redis_service = Depends(get_redis_service),
    ws_manager = Depends(get_ws_manager)
):
    """
    Receive and process node heartbeat.
    
    Nodes should send regular heartbeat signals to indicate they are alive
    and operational. This endpoint updates the node's status and metrics.
    """
    try:
        logger.api_request("POST", "/api/v1/nodes/heartbeat", node_id=heartbeat_data.node_id)
        
        # Update heartbeat in Redis
        success = await redis_service.update_node_heartbeat(
            heartbeat_data.node_id,
            heartbeat_data.dict()
        )
        
        if not success:
            raise HTTPException(
                status_code=404,
                detail=f"Node {heartbeat_data.node_id} not found"
            )
        
        # Broadcast heartbeat status if there are issues
        if heartbeat_data.status not in ["healthy", "operational"]:
            background_tasks.add_task(
                ws_manager.broadcast_to_all,
                {
                    "message_type": "node_status_alert",
                    "data": {
                        "node_id": heartbeat_data.node_id,
                        "status": heartbeat_data.status,
                        "timestamp": heartbeat_data.timestamp.isoformat()
                    }
                }
            )
        
        logger.debug("Heartbeat processed", 
                    node_id=heartbeat_data.node_id,
                    status=heartbeat_data.status)
        
        return BaseResponse(
            success=True,
            message="Heartbeat received and processed",
            timestamp=datetime.utcnow()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to process heartbeat", 
                    node_id=heartbeat_data.node_id, 
                    error=e)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process heartbeat: {str(e)}"
        )

@router.get("/status", response_model=List[NodeStatus])
async def get_all_nodes_status(
    node_types: Optional[List[NodeType]] = None,
    include_inactive: bool = False,
    redis_service = Depends(get_redis_service)
):
    """
    Get status of all registered nodes.
    
    Returns a list of all nodes with their current status information.
    Can be filtered by node type and include/exclude inactive nodes.
    """
    try:
        logger.api_request("GET", "/api/v1/nodes/status")
        
        # Get all nodes from Redis
        nodes = await redis_service.get_all_nodes()
        
        node_statuses = []
        for node_data in nodes:
            # Filter by node type if specified
            if node_types and node_data.get("node_type") not in node_types:
                continue
            
            # Convert to NodeStatus model
            try:
                node_status = NodeStatus(
                    node_id=node_data["node_id"],
                    name=node_data["name"],
                    node_type=node_data["node_type"],
                    status=node_data.get("status", "unknown"),
                    connection_status=node_data.get("connection_status", "unknown"),
                    last_heartbeat=datetime.fromisoformat(node_data["last_seen"]) if node_data.get("last_seen") else None,
                    is_healthy=node_data.get("status") in ["healthy", "operational"],
                    response_time_ms=node_data.get("response_time_ms")
                )
                node_statuses.append(node_status)
                
            except Exception as e:
                logger.warning("Failed to parse node data", 
                             node_id=node_data.get("node_id"),
                             error=e)
                continue
        
        logger.info("Retrieved node statuses", count=len(node_statuses))
        
        return node_statuses
        
    except Exception as e:
        logger.error("Failed to get node statuses", error=e)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve node statuses: {str(e)}"
        )

@router.get("/{node_id}", response_model=NodeInfo)
async def get_node_info(
    node_id: str,
    redis_service = Depends(get_redis_service)
):
    """
    Get detailed information about a specific node.
    
    Returns complete node information including registration details,
    current status, capabilities, and performance metrics.
    """
    try:
        logger.api_request("GET", f"/api/v1/nodes/{node_id}", node_id=node_id)
        
        # Get node data from Redis
        node_data = await redis_service.get_node(node_id)
        
        if not node_data:
            raise HTTPException(
                status_code=404,
                detail=f"Node {node_id} not found"
            )
        
        # Convert to NodeInfo model
        try:
            node_info = NodeInfo(**node_data)
            
            logger.debug("Retrieved node info", 
                        node_id=node_id,
                        name=node_info.name)
            
            return node_info
            
        except Exception as e:
            logger.error("Failed to parse node data", 
                        node_id=node_id, 
                        error=e)
            raise HTTPException(
                status_code=500,
                detail=f"Failed to parse node data: {str(e)}"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get node info", 
                    node_id=node_id, 
                    error=e)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve node information: {str(e)}"
        )

@router.put("/{node_id}", response_model=BaseResponse)
async def update_node(
    node_id: str,
    update_data: NodeUpdate,
    background_tasks: BackgroundTasks,
    redis_service = Depends(get_redis_service),
    ws_manager = Depends(get_ws_manager)
):
    """
    Update node configuration and metadata.
    
    Allows updating node description, metadata, heartbeat interval,
    and capabilities without requiring re-registration.
    """
    try:
        logger.api_request("PUT", f"/api/v1/nodes/{node_id}", node_id=node_id)
        
        # Get existing node data
        node_data = await redis_service.get_node(node_id)
        
        if not node_data:
            raise HTTPException(
                status_code=404,
                detail=f"Node {node_id} not found"
            )
        
        # Update fields
        update_dict = update_data.dict(exclude_unset=True)
        node_data.update(update_dict)
        node_data["last_updated"] = datetime.utcnow().isoformat()
        
        # Store updated data
        await redis_service.register_node(node_data)  # This will update existing
        
        # Broadcast node update
        background_tasks.add_task(
            ws_manager.broadcast_to_all,
            {
                "message_type": "node_updated",
                "data": {
                    "node_id": node_id,
                    "updated_fields": list(update_dict.keys()),
                    "timestamp": datetime.utcnow().isoformat()
                }
            }
        )
        
        logger.info("Node updated successfully", 
                   node_id=node_id,
                   updated_fields=list(update_dict.keys()))
        
        return BaseResponse(
            success=True,
            message=f"Node {node_id} updated successfully",
            timestamp=datetime.utcnow()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to update node", 
                    node_id=node_id, 
                    error=e)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update node: {str(e)}"
        )

@router.delete("/{node_id}", response_model=BaseResponse)
async def unregister_node(
    node_id: str,
    background_tasks: BackgroundTasks,
    redis_service = Depends(get_redis_service),
    ws_manager = Depends(get_ws_manager)
):
    """
    Unregister a node from the HUB.
    
    Removes the node from the registry and notifies other nodes
    about the disconnection.
    """
    try:
        logger.api_request("DELETE", f"/api/v1/nodes/{node_id}", node_id=node_id)
        
        # Get node info before deletion
        node_data = await redis_service.get_node(node_id)
        
        if not node_data:
            raise HTTPException(
                status_code=404,
                detail=f"Node {node_id} not found"
            )
        
        # Remove node from Redis
        success = await redis_service.remove_node(node_id)
        
        if not success:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to remove node {node_id}"
            )
        
        # Broadcast node removal
        background_tasks.add_task(
            ws_manager.broadcast_to_all,
            {
                "message_type": "node_unregistered",
                "data": {
                    "node_id": node_id,
                    "name": node_data.get("name"),
                    "timestamp": datetime.utcnow().isoformat()
                }
            }
        )
        
        logger.info("Node unregistered successfully", 
                   node_id=node_id,
                   name=node_data.get("name"))
        
        return BaseResponse(
            success=True,
            message=f"Node {node_id} unregistered successfully",
            timestamp=datetime.utcnow()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to unregister node", 
                    node_id=node_id, 
                    error=e)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to unregister node: {str(e)}"
        )

@router.get("/stats/summary")
async def get_node_statistics(
    redis_service = Depends(get_redis_service)
):
    """
    Get summary statistics about all nodes.
    
    Returns aggregated statistics about node types, statuses,
    and system health metrics.
    """
    try:
        logger.api_request("GET", "/api/v1/nodes/stats/summary")
        
        # Get all nodes
        nodes = await redis_service.get_all_nodes()
        
        # Calculate statistics
        stats = {
            "total_nodes": len(nodes),
            "nodes_by_type": {},
            "nodes_by_status": {},
            "healthy_nodes": 0,
            "recent_registrations": 0,
            "active_nodes": 0
        }
        
        now = datetime.utcnow()
        one_hour_ago = now.timestamp() - 3600
        
        for node in nodes:
            # Count by type
            node_type = node.get("node_type", "unknown")
            stats["nodes_by_type"][node_type] = stats["nodes_by_type"].get(node_type, 0) + 1
            
            # Count by status
            status = node.get("status", "unknown")
            stats["nodes_by_status"][status] = stats["nodes_by_status"].get(status, 0) + 1
            
            # Count healthy nodes
            if status in ["healthy", "operational"]:
                stats["healthy_nodes"] += 1
            
            # Count recent registrations
            registered_at = node.get("registered_at")
            if registered_at:
                try:
                    reg_time = datetime.fromisoformat(registered_at).timestamp()
                    if reg_time > one_hour_ago:
                        stats["recent_registrations"] += 1
                except Exception:
                    pass
            
            # Count active nodes (recent heartbeat)
            last_seen = node.get("last_seen")
            if last_seen:
                try:
                    seen_time = datetime.fromisoformat(last_seen).timestamp()
                    if seen_time > one_hour_ago:
                        stats["active_nodes"] += 1
                except Exception:
                    pass
        
        # Add health percentage
        stats["health_percentage"] = (stats["healthy_nodes"] / stats["total_nodes"] * 100) if stats["total_nodes"] > 0 else 0
        
        logger.info("Generated node statistics", 
                   total_nodes=stats["total_nodes"],
                   healthy_nodes=stats["healthy_nodes"])
        
        return stats
        
    except Exception as e:
        logger.error("Failed to get node statistics", error=e)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve node statistics: {str(e)}"
        ) 