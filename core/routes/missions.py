"""
Missions API Router for NIS HUB

Handles mission coordination, task assignment, and workflow management
across multiple NIS nodes and agents.
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, Request, BackgroundTasks, Query
from fastapi.responses import JSONResponse
from datetime import datetime

from models.mission_models import (
    Mission, MissionCreate, MissionUpdate, MissionStatus, 
    MissionStats, MissionQuery, CoordinationEvent, MissionType
)
from models.base_models import BaseResponse, ErrorResponse
from services.logging_service import NISHubLogger

router = APIRouter(prefix="/missions")
logger = NISHubLogger("missions_api")

async def get_redis_service(request: Request):
    """Dependency to get Redis service from app state."""
    return request.app.state.redis

async def get_ws_manager(request: Request):
    """Dependency to get WebSocket manager from app state."""
    return request.app.state.ws_manager

@router.post("/create", response_model=BaseResponse)
async def create_mission(
    mission_data: MissionCreate,
    background_tasks: BackgroundTasks,
    redis_service = Depends(get_redis_service),
    ws_manager = Depends(get_ws_manager)
):
    """
    Create a new coordinated mission.
    
    This endpoint allows nodes to create complex missions that involve
    multiple agents and coordinated tasks across different domains.
    """
    try:
        logger.api_request("POST", "/api/v1/missions/create",
                          mission_name=mission_data.name,
                          created_by=mission_data.created_by,
                          task_count=len(mission_data.tasks))
        
        # Convert Pydantic model to dict for Redis storage
        mission_dict = mission_data.dict()
        mission_dict["status"] = MissionStatus.PLANNED
        mission_dict["progress_percent"] = 0.0
        mission_dict["total_tasks"] = len(mission_data.tasks)
        mission_dict["completed_tasks"] = 0
        mission_dict["failed_tasks"] = 0
        
        # Store mission in Redis
        mission_id = await redis_service.store_mission(mission_dict)
        
        # Auto-assign nodes to tasks if enabled
        if mission_data.auto_assign_nodes:
            background_tasks.add_task(
                _auto_assign_mission_tasks,
                redis_service,
                ws_manager,
                mission_id,
                mission_data.tasks
            )
        
        # Broadcast mission creation to relevant nodes
        background_tasks.add_task(
            ws_manager.broadcast_to_all,
            {
                "message_type": "mission_created",
                "data": {
                    "mission_id": mission_id,
                    "name": mission_data.name,
                    "mission_type": mission_data.mission_type,
                    "domain": mission_data.domain,
                    "priority": mission_data.priority,
                    "created_by": mission_data.created_by,
                    "task_count": len(mission_data.tasks)
                }
            }
        )
        
        logger.info("Mission created successfully",
                   mission_id=mission_id,
                   name=mission_data.name,
                   domain=mission_data.domain,
                   task_count=len(mission_data.tasks))
        
        return BaseResponse(
            success=True,
            message=f"Mission '{mission_data.name}' created successfully with ID: {mission_id}",
            timestamp=datetime.utcnow()
        )
        
    except Exception as e:
        logger.error("Failed to create mission", 
                    mission_name=mission_data.name,
                    error=e)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create mission: {str(e)}"
        )

@router.get("/", response_model=List[Mission])
async def get_missions(
    mission_types: Optional[List[MissionType]] = Query(None),
    statuses: Optional[List[MissionStatus]] = Query(None),
    domains: Optional[List[str]] = Query(None),
    created_by: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    redis_service = Depends(get_redis_service)
):
    """
    Get list of missions with optional filtering.
    
    Returns missions that match the specified filters with pagination support.
    """
    try:
        logger.api_request("GET", "/api/v1/missions/",
                          mission_types=mission_types,
                          statuses=statuses,
                          page=page)
        
        # TODO: Implement comprehensive mission querying in RedisService
        # For now, get all missions and filter in Python
        
        # This is a placeholder implementation
        missions = []
        
        logger.info("Retrieved missions",
                   count=len(missions),
                   page=page,
                   page_size=page_size)
        
        return missions
        
    except Exception as e:
        logger.error("Failed to get missions", error=e)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve missions: {str(e)}"
        )

@router.get("/{mission_id}", response_model=Mission)
async def get_mission(
    mission_id: str,
    redis_service = Depends(get_redis_service)
):
    """
    Get detailed information about a specific mission.
    
    Returns complete mission information including tasks, participants,
    and current status.
    """
    try:
        logger.api_request("GET", f"/api/v1/missions/{mission_id}",
                          mission_id=mission_id)
        
        # Get mission data from Redis
        mission_data = await redis_service.get_mission(mission_id)
        
        if not mission_data:
            raise HTTPException(
                status_code=404,
                detail=f"Mission {mission_id} not found"
            )
        
        # Convert to Mission object
        try:
            mission = Mission(**mission_data)
            
            logger.debug("Retrieved mission info",
                        mission_id=mission_id,
                        name=mission.name,
                        status=mission.status)
            
            return mission
            
        except Exception as e:
            logger.error("Failed to parse mission data",
                        mission_id=mission_id,
                        error=e)
            raise HTTPException(
                status_code=500,
                detail=f"Failed to parse mission data: {str(e)}"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get mission",
                    mission_id=mission_id,
                    error=e)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve mission: {str(e)}"
        )

@router.put("/{mission_id}/update", response_model=BaseResponse)
async def update_mission(
    mission_id: str,
    update_data: MissionUpdate,
    background_tasks: BackgroundTasks,
    redis_service = Depends(get_redis_service),
    ws_manager = Depends(get_ws_manager)
):
    """
    Update mission status, progress, or task information.
    
    Allows nodes to update mission progress, task statuses,
    and other mission-related information.
    """
    try:
        logger.api_request("PUT", f"/api/v1/missions/{mission_id}/update",
                          mission_id=mission_id,
                          updated_by=update_data.updated_by)
        
        # Get existing mission data
        mission_data = await redis_service.get_mission(mission_id)
        
        if not mission_data:
            raise HTTPException(
                status_code=404,
                detail=f"Mission {mission_id} not found"
            )
        
        # Update fields
        update_dict = update_data.dict(exclude_unset=True)
        mission_data.update(update_dict)
        mission_data["last_updated"] = datetime.utcnow().isoformat()
        mission_data["last_updated_by"] = update_data.updated_by
        mission_data["updates_count"] = mission_data.get("updates_count", 0) + 1
        
        # Store updated mission
        await redis_service.store_mission(mission_data)
        
        # Broadcast mission update
        background_tasks.add_task(
            ws_manager.broadcast_to_all,
            {
                "message_type": "mission_updated",
                "data": {
                    "mission_id": mission_id,
                    "updated_by": update_data.updated_by,
                    "updated_fields": list(update_dict.keys()),
                    "status": mission_data.get("status"),
                    "progress_percent": mission_data.get("progress_percent"),
                    "timestamp": datetime.utcnow().isoformat()
                }
            }
        )
        
        logger.info("Mission updated successfully",
                   mission_id=mission_id,
                   updated_by=update_data.updated_by,
                   updated_fields=list(update_dict.keys()))
        
        return BaseResponse(
            success=True,
            message=f"Mission {mission_id} updated successfully",
            timestamp=datetime.utcnow()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to update mission",
                    mission_id=mission_id,
                    error=e)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update mission: {str(e)}"
        )

@router.post("/{mission_id}/start", response_model=BaseResponse)
async def start_mission(
    mission_id: str,
    background_tasks: BackgroundTasks,
    redis_service = Depends(get_redis_service),
    ws_manager = Depends(get_ws_manager),
    started_by: str = Query(..., description="ID of the node starting the mission")
):
    """
    Start executing a planned mission.
    
    Transitions a mission from PLANNED to ACTIVE status and begins
    task execution coordination.
    """
    try:
        logger.api_request("POST", f"/api/v1/missions/{mission_id}/start",
                          mission_id=mission_id,
                          started_by=started_by)
        
        # Get mission data
        mission_data = await redis_service.get_mission(mission_id)
        
        if not mission_data:
            raise HTTPException(
                status_code=404,
                detail=f"Mission {mission_id} not found"
            )
        
        current_status = mission_data.get("status")
        if current_status != MissionStatus.PLANNED:
            raise HTTPException(
                status_code=400,
                detail=f"Mission is in {current_status} status, can only start PLANNED missions"
            )
        
        # Update mission status
        mission_data["status"] = MissionStatus.ACTIVE
        mission_data["started_at"] = datetime.utcnow().isoformat()
        mission_data["coordinator_node_id"] = started_by
        
        # Store updated mission
        await redis_service.store_mission(mission_data)
        
        # Broadcast mission start
        background_tasks.add_task(
            ws_manager.broadcast_to_all,
            {
                "message_type": "mission_started",
                "data": {
                    "mission_id": mission_id,
                    "name": mission_data.get("name"),
                    "started_by": started_by,
                    "timestamp": datetime.utcnow().isoformat()
                }
            }
        )
        
        # Begin task coordination
        background_tasks.add_task(
            _begin_task_coordination,
            redis_service,
            ws_manager,
            mission_id,
            mission_data
        )
        
        logger.info("Mission started successfully",
                   mission_id=mission_id,
                   started_by=started_by)
        
        return BaseResponse(
            success=True,
            message=f"Mission {mission_id} started successfully",
            timestamp=datetime.utcnow()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to start mission",
                    mission_id=mission_id,
                    error=e)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start mission: {str(e)}"
        )

@router.post("/{mission_id}/events", response_model=BaseResponse)
async def send_coordination_event(
    mission_id: str,
    event_data: CoordinationEvent,
    background_tasks: BackgroundTasks,
    ws_manager = Depends(get_ws_manager)
):
    """
    Send coordination event for mission management.
    
    Allows nodes to send coordination messages, status updates,
    and requests related to mission execution.
    """
    try:
        logger.api_request("POST", f"/api/v1/missions/{mission_id}/events",
                          mission_id=mission_id,
                          event_type=event_data.event_type,
                          source_node=event_data.source_node_id)
        
        # Prepare event message
        message = {
            "message_type": "coordination_event",
            "data": {
                "mission_id": mission_id,
                "event_id": event_data.event_id,
                "event_type": event_data.event_type,
                "source_node_id": event_data.source_node_id,
                "message": event_data.message,
                "data": event_data.data,
                "priority": event_data.priority,
                "requires_response": event_data.requires_response,
                "timestamp": datetime.utcnow().isoformat()
            }
        }
        
        recipients_count = 0
        
        # Send to specific nodes
        if event_data.target_node_ids:
            for node_id in event_data.target_node_ids:
                background_tasks.add_task(
                    ws_manager.send_to_node,
                    node_id,
                    message
                )
                recipients_count += 1
        
        # Broadcast to all mission participants
        elif event_data.broadcast_to_all:
            recipients_count = await ws_manager.broadcast_to_all(message)
        
        logger.info("Coordination event sent",
                   mission_id=mission_id,
                   event_type=event_data.event_type,
                   source_node=event_data.source_node_id,
                   recipients=recipients_count)
        
        return BaseResponse(
            success=True,
            message=f"Coordination event sent to {recipients_count} recipients",
            timestamp=datetime.utcnow()
        )
        
    except Exception as e:
        logger.error("Failed to send coordination event",
                    mission_id=mission_id,
                    event_type=event_data.event_type,
                    error=e)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to send coordination event: {str(e)}"
        )

@router.get("/stats/summary", response_model=MissionStats)
async def get_mission_statistics(
    redis_service = Depends(get_redis_service)
):
    """
    Get mission system statistics.
    
    Returns aggregated statistics about missions, task completion rates,
    and system performance metrics.
    """
    try:
        logger.api_request("GET", "/api/v1/missions/stats/summary")
        
        # TODO: Implement comprehensive mission statistics
        # This is a placeholder implementation
        
        stats = MissionStats(
            total_missions=0,
            active_missions=0,
            completed_missions=0,
            failed_missions=0,
            missions_by_type={},
            missions_by_domain={},
            missions_by_priority={},
            avg_completion_time_hours=0.0,
            success_rate_percent=0.0,
            avg_efficiency_score=0.0,
            missions_created_last_24h=0,
            missions_completed_last_24h=0,
            total_participating_nodes=0,
            most_active_nodes=[]
        )
        
        logger.info("Mission statistics generated")
        
        return stats
        
    except Exception as e:
        logger.error("Failed to get mission statistics", error=e)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve mission statistics: {str(e)}"
        )

# Helper functions

async def _auto_assign_mission_tasks(
    redis_service,
    ws_manager,
    mission_id: str,
    tasks: List[Any]
):
    """
    Background task to automatically assign mission tasks to capable nodes.
    
    Args:
        redis_service: Redis service instance
        ws_manager: WebSocket manager instance
        mission_id: Mission identifier
        tasks: List of mission tasks
    """
    try:
        logger.info("Starting auto-assignment of mission tasks",
                   mission_id=mission_id,
                   task_count=len(tasks))
        
        # Get all available nodes
        nodes = await redis_service.get_all_nodes()
        
        # TODO: Implement sophisticated task assignment algorithm
        # This is a placeholder that would consider:
        # - Node capabilities vs task requirements
        # - Node current load and availability
        # - Geographic/domain proximity
        # - Performance history
        
        assignments = []
        for i, task in enumerate(tasks):
            if nodes and i < len(nodes):
                assigned_node = nodes[i % len(nodes)]
                assignments.append({
                    "task_id": task.task_id,
                    "assigned_node_id": assigned_node["node_id"],
                    "node_name": assigned_node.get("name")
                })
        
        # Notify assigned nodes
        for assignment in assignments:
            await ws_manager.send_to_node(
                assignment["assigned_node_id"],
                {
                    "message_type": "task_assigned",
                    "data": {
                        "mission_id": mission_id,
                        "task_id": assignment["task_id"],
                        "assignment_time": datetime.utcnow().isoformat()
                    }
                }
            )
        
        logger.info("Mission task auto-assignment completed",
                   mission_id=mission_id,
                   assignments_made=len(assignments))
        
    except Exception as e:
        logger.error("Failed to auto-assign mission tasks",
                    mission_id=mission_id,
                    error=e)

async def _begin_task_coordination(
    redis_service,
    ws_manager,
    mission_id: str,
    mission_data: Dict[str, Any]
):
    """
    Background task to begin coordinating mission task execution.
    
    Args:
        redis_service: Redis service instance
        ws_manager: WebSocket manager instance
        mission_id: Mission identifier
        mission_data: Mission data dictionary
    """
    try:
        logger.info("Beginning task coordination for mission",
                   mission_id=mission_id,
                   mission_name=mission_data.get("name"))
        
        # TODO: Implement task coordination logic
        # This would include:
        # - Dependency resolution
        # - Parallel execution management  
        # - Progress monitoring
        # - Error handling and retries
        # - Resource allocation
        
        # Broadcast mission coordination start
        await ws_manager.broadcast_to_all({
            "message_type": "mission_coordination_started",
            "data": {
                "mission_id": mission_id,
                "coordinator_message": "Mission coordination has begun",
                "timestamp": datetime.utcnow().isoformat()
            }
        })
        
        logger.info("Task coordination initiated",
                   mission_id=mission_id)
        
    except Exception as e:
        logger.error("Failed to begin task coordination",
                    mission_id=mission_id,
                    error=e) 