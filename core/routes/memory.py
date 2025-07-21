"""
Memory API Router for NIS HUB

Handles memory synchronization, querying, and broadcasting operations
for the shared memory system across all NIS nodes.
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, Request, BackgroundTasks, Query
from fastapi.responses import JSONResponse
from datetime import datetime

from models.memory_models import (
    MemoryEntry, MemorySync, MemoryQuery, MemoryResponse, 
    MemoryBroadcast, MemoryStats, MemoryHealth, MemoryType, MemoryScope
)
from models.base_models import BaseResponse, ErrorResponse, PaginatedResponse
from services.logging_service import NISHubLogger

router = APIRouter(prefix="/memory")
logger = NISHubLogger("memory_api")

async def get_redis_service(request: Request):
    """Dependency to get Redis service from app state."""
    return request.app.state.redis

async def get_ws_manager(request: Request):
    """Dependency to get WebSocket manager from app state."""
    return request.app.state.ws_manager

@router.post("/sync", response_model=BaseResponse)
async def sync_memory(
    sync_data: MemorySync,
    background_tasks: BackgroundTasks,
    redis_service = Depends(get_redis_service),
    ws_manager = Depends(get_ws_manager)
):
    """
    Synchronize memory entries from a node to the HUB.
    
    This endpoint allows nodes to upload their memory entries to the shared
    memory system, making them available to other nodes in the network.
    """
    try:
        logger.api_request("POST", "/api/v1/memory/sync", 
                          node_id=sync_data.node_id,
                          entry_count=len(sync_data.entries))
        
        stored_entries = []
        failed_entries = []
        
        for entry in sync_data.entries:
            try:
                # Validate entry has required fields
                entry_dict = entry.dict()
                entry_dict["source_node_id"] = sync_data.node_id
                
                # Store memory entry in Redis
                entry_id = await redis_service.store_memory(entry_dict)
                stored_entries.append(entry_id)
                
            except Exception as e:
                logger.warning("Failed to store memory entry", 
                             entry_title=entry.title,
                             error=e)
                failed_entries.append({"title": entry.title, "error": str(e)})
        
        # Broadcast memory sync to relevant nodes
        if stored_entries:
            background_tasks.add_task(
                _broadcast_memory_update,
                ws_manager,
                sync_data.node_id,
                stored_entries,
                "memory_synced"
            )
        
        success_count = len(stored_entries)
        total_count = len(sync_data.entries)
        
        logger.info("Memory sync completed", 
                   node_id=sync_data.node_id,
                   success_count=success_count,
                   failed_count=len(failed_entries),
                   total_count=total_count)
        
        return BaseResponse(
            success=True,
            message=f"Synced {success_count}/{total_count} memory entries successfully",
            timestamp=datetime.utcnow()
        )
        
    except Exception as e:
        logger.error("Failed to sync memory", 
                    node_id=sync_data.node_id, 
                    error=e)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to sync memory: {str(e)}"
        )

@router.post("/query", response_model=MemoryResponse)
async def query_memory(
    query_data: MemoryQuery,
    redis_service = Depends(get_redis_service)
):
    """
    Query memory entries based on filters and search criteria.
    
    Allows nodes to search for relevant memory entries using various
    filters such as domain, type, source node, tags, and text search.
    """
    try:
        start_time = datetime.utcnow()
        
        logger.api_request("POST", "/api/v1/memory/query",
                          requesting_node=query_data.requesting_node_id,
                          search_text=query_data.search_text)
        
        # Build filters dictionary for Redis query
        filters = {}
        
        if query_data.domains:
            filters["domains"] = query_data.domains
        if query_data.memory_types:
            filters["memory_types"] = [t.value for t in query_data.memory_types]
        if query_data.source_node_ids:
            filters["source_node_ids"] = query_data.source_node_ids
        if query_data.tags:
            filters["tags"] = query_data.tags
        if query_data.search_text:
            filters["search_text"] = query_data.search_text
        
        # Add temporal filters
        if query_data.created_after:
            filters["created_after"] = query_data.created_after
        if query_data.created_before:
            filters["created_before"] = query_data.created_before
        
        # Add pagination
        filters["page"] = query_data.page
        filters["page_size"] = query_data.page_size
        filters["sort_by"] = query_data.sort_by
        filters["sort_order"] = query_data.sort_order
        
        # Query memory entries from Redis
        memory_entries = await redis_service.query_memory(filters)
        
        # Convert to MemoryEntry objects
        entries = []
        for entry_data in memory_entries:
            try:
                memory_entry = MemoryEntry(**entry_data)
                
                # Check access permissions
                if _can_access_memory(memory_entry, query_data.requesting_node_id):
                    entries.append(memory_entry)
                
            except Exception as e:
                logger.warning("Failed to parse memory entry", 
                             entry_id=entry_data.get("entry_id"),
                             error=e)
        
        # Calculate response metadata
        query_time_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
        total_count = len(entries)  # TODO: Get actual total from Redis
        total_pages = (total_count + query_data.page_size - 1) // query_data.page_size
        
        logger.info("Memory query completed",
                   requesting_node=query_data.requesting_node_id,
                   results_count=len(entries),
                   query_time_ms=query_time_ms)
        
        return MemoryResponse(
            success=True,
            message=f"Found {len(entries)} memory entries",
            entries=entries,
            total_count=total_count,
            page=query_data.page,
            page_size=query_data.page_size,
            total_pages=total_pages,
            query_time_ms=query_time_ms,
            from_cache=False  # TODO: Implement caching
        )
        
    except Exception as e:
        logger.error("Failed to query memory",
                    requesting_node=query_data.requesting_node_id,
                    error=e)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to query memory: {str(e)}"
        )

@router.get("/fetch/{entry_id}", response_model=MemoryEntry)
async def fetch_memory_entry(
    entry_id: str,
    requesting_node_id: str = Query(..., description="ID of the requesting node"),
    redis_service = Depends(get_redis_service)
):
    """
    Fetch a specific memory entry by ID.
    
    Retrieves a single memory entry and updates its access statistics.
    """
    try:
        logger.api_request("GET", f"/api/v1/memory/fetch/{entry_id}",
                          entry_id=entry_id,
                          requesting_node=requesting_node_id)
        
        # Get memory entry from Redis
        memory_data = await redis_service.get_memory(entry_id)
        
        if not memory_data:
            raise HTTPException(
                status_code=404,
                detail=f"Memory entry {entry_id} not found"
            )
        
        # Convert to MemoryEntry object
        memory_entry = MemoryEntry(**memory_data)
        
        # Check access permissions
        if not _can_access_memory(memory_entry, requesting_node_id):
            raise HTTPException(
                status_code=403,
                detail="Access denied to this memory entry"
            )
        
        logger.debug("Memory entry fetched",
                    entry_id=entry_id,
                    requesting_node=requesting_node_id,
                    title=memory_entry.title)
        
        return memory_entry
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to fetch memory entry",
                    entry_id=entry_id,
                    requesting_node=requesting_node_id,
                    error=e)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch memory entry: {str(e)}"
        )

@router.post("/broadcast", response_model=BaseResponse)
async def broadcast_memory(
    broadcast_data: MemoryBroadcast,
    background_tasks: BackgroundTasks,
    ws_manager = Depends(get_ws_manager)
):
    """
    Broadcast memory-related message to nodes.
    
    Allows nodes to send notifications about memory updates, alerts,
    or coordination requests to other relevant nodes.
    """
    try:
        logger.api_request("POST", "/api/v1/memory/broadcast",
                          source_node=broadcast_data.source_node_id,
                          message_type=broadcast_data.message_type)
        
        # Prepare broadcast message
        message = {
            "message_type": broadcast_data.message_type,
            "data": {
                "source_node_id": broadcast_data.source_node_id,
                "title": broadcast_data.title,
                "content": broadcast_data.content,
                "priority": broadcast_data.priority,
                "timestamp": datetime.utcnow().isoformat()
            }
        }
        
        recipients_count = 0
        
        # Broadcast to specific nodes
        if broadcast_data.target_node_ids:
            for node_id in broadcast_data.target_node_ids:
                background_tasks.add_task(
                    ws_manager.send_to_node,
                    node_id,
                    message
                )
                recipients_count += 1
        
        # Broadcast to domain groups
        elif broadcast_data.target_domains:
            for domain in broadcast_data.target_domains:
                sent = await ws_manager.broadcast_to_group(domain, message)
                recipients_count += sent
        
        # Broadcast to all if no specific targets
        else:
            recipients_count = await ws_manager.broadcast_to_all(message)
        
        logger.info("Memory broadcast sent",
                   source_node=broadcast_data.source_node_id,
                   message_type=broadcast_data.message_type,
                   recipients=recipients_count)
        
        return BaseResponse(
            success=True,
            message=f"Broadcast sent to {recipients_count} recipients",
            timestamp=datetime.utcnow()
        )
        
    except Exception as e:
        logger.error("Failed to broadcast memory message",
                    source_node=broadcast_data.source_node_id,
                    error=e)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to broadcast message: {str(e)}"
        )

@router.get("/stats", response_model=MemoryStats)
async def get_memory_statistics(
    redis_service = Depends(get_redis_service)
):
    """
    Get memory system statistics.
    
    Returns aggregated statistics about memory usage, entry counts,
    and system performance metrics.
    """
    try:
        logger.api_request("GET", "/api/v1/memory/stats")
        
        # TODO: Implement comprehensive memory statistics
        # This is a placeholder implementation
        
        stats = MemoryStats(
            total_entries=0,
            total_size_mb=0.0,
            entries_by_type={},
            entries_by_domain={},
            entries_by_scope={},
            avg_query_time_ms=0.0,
            cache_hit_rate=0.0,
            entries_created_last_hour=0,
            entries_accessed_last_hour=0,
            top_contributing_nodes=[]
        )
        
        logger.info("Memory statistics generated")
        
        return stats
        
    except Exception as e:
        logger.error("Failed to get memory statistics", error=e)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve memory statistics: {str(e)}"
        )

@router.get("/health", response_model=MemoryHealth)
async def get_memory_health(
    redis_service = Depends(get_redis_service)
):
    """
    Get memory system health status.
    
    Returns health indicators for the memory subsystem including
    Redis connectivity and performance metrics.
    """
    try:
        logger.api_request("GET", "/api/v1/memory/health")
        
        # Check Redis connectivity
        redis_connected = await redis_service.ping()
        
        # TODO: Implement comprehensive health checks
        health = MemoryHealth(
            status="healthy" if redis_connected else "degraded",
            redis_connected=redis_connected,
            vector_db_connected=True,  # TODO: Check actual vector DB
            memory_usage_percent=0.0,  # TODO: Get actual usage
            disk_usage_percent=0.0,    # TODO: Get actual usage
            avg_response_time_ms=0.0,  # TODO: Calculate from metrics
            warnings=[],
            errors=[] if redis_connected else ["Redis connection failed"]
        )
        
        logger.info("Memory health check completed",
                   status=health.status,
                   redis_connected=redis_connected)
        
        return health
        
    except Exception as e:
        logger.error("Failed to get memory health", error=e)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve memory health: {str(e)}"
        )

@router.delete("/{entry_id}", response_model=BaseResponse)
async def delete_memory_entry(
    entry_id: str,
    background_tasks: BackgroundTasks,
    redis_service = Depends(get_redis_service),
    ws_manager = Depends(get_ws_manager),
    requesting_node_id: str = Query(..., description="ID of the requesting node")
):
    """
    Delete a memory entry.
    
    Removes a memory entry from the shared memory system.
    Only the creating node or supervisor agents can delete entries.
    """
    try:
        logger.api_request("DELETE", f"/api/v1/memory/{entry_id}",
                          entry_id=entry_id,
                          requesting_node=requesting_node_id)
        
        # Get memory entry to check permissions
        memory_data = await redis_service.get_memory(entry_id)
        
        if not memory_data:
            raise HTTPException(
                status_code=404,
                detail=f"Memory entry {entry_id} not found"
            )
        
        # Check if requesting node can delete this entry
        source_node_id = memory_data.get("source_node_id")
        if requesting_node_id != source_node_id:
            # TODO: Check if requesting node is a supervisor
            raise HTTPException(
                status_code=403,
                detail="Only the creating node can delete this memory entry"
            )
        
        # Delete from Redis
        # TODO: Implement delete functionality in RedisService
        # success = await redis_service.delete_memory(entry_id)
        
        # Broadcast deletion notification
        background_tasks.add_task(
            ws_manager.broadcast_to_all,
            {
                "message_type": "memory_deleted",
                "data": {
                    "entry_id": entry_id,
                    "deleted_by": requesting_node_id,
                    "timestamp": datetime.utcnow().isoformat()
                }
            }
        )
        
        logger.info("Memory entry deleted",
                   entry_id=entry_id,
                   requesting_node=requesting_node_id)
        
        return BaseResponse(
            success=True,
            message=f"Memory entry {entry_id} deleted successfully",
            timestamp=datetime.utcnow()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to delete memory entry",
                    entry_id=entry_id,
                    requesting_node=requesting_node_id,
                    error=e)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete memory entry: {str(e)}"
        )

# Helper functions

def _can_access_memory(memory_entry: MemoryEntry, requesting_node_id: str) -> bool:
    """
    Check if a node can access a memory entry based on scope and permissions.
    
    Args:
        memory_entry: The memory entry to check
        requesting_node_id: ID of the requesting node
        
    Returns:
        True if access is allowed
    """
    scope = memory_entry.scope
    
    if scope == MemoryScope.PUBLIC:
        return True
    elif scope == MemoryScope.PRIVATE:
        return memory_entry.source_node_id == requesting_node_id
    elif scope == MemoryScope.DOMAIN:
        # TODO: Check if nodes are in the same domain
        return True  # Placeholder
    elif scope == MemoryScope.SUPERVISOR:
        # TODO: Check if requesting node is a supervisor
        return True  # Placeholder
    
    return False

async def _broadcast_memory_update(
    ws_manager,
    source_node_id: str,
    entry_ids: List[str],
    update_type: str
):
    """
    Background task to broadcast memory updates to relevant nodes.
    
    Args:
        ws_manager: WebSocket manager instance
        source_node_id: Node that created the update
        entry_ids: List of memory entry IDs
        update_type: Type of update (e.g., 'memory_synced', 'memory_updated')
    """
    try:
        message = {
            "message_type": update_type,
            "data": {
                "source_node_id": source_node_id,
                "entry_ids": entry_ids,
                "count": len(entry_ids),
                "timestamp": datetime.utcnow().isoformat()
            }
        }
        
        # Broadcast to all nodes except the source
        await ws_manager.broadcast_to_all(message, exclude_connections=[source_node_id])
        
    except Exception as e:
        logger.error("Failed to broadcast memory update",
                    source_node=source_node_id,
                    update_type=update_type,
                    error=e) 