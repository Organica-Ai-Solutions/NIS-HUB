"""
Mission coordination for NIS HUB SDK.

Handles mission creation, participation, and task management.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from .exceptions import MissionError

logger = logging.getLogger(__name__)


class MissionCoordinator:
    """
    Manages mission operations for a NIS node.
    
    Provides methods for creating missions, participating in missions,
    and managing task assignments.
    """
    
    def __init__(self, node):
        """
        Initialize mission coordinator.
        
        Args:
            node: Reference to the parent NISNode instance
        """
        self.node = node
        self.active_missions: Dict[str, Any] = {}
        self.assigned_tasks: Dict[str, Any] = {}
        
    async def create_mission(
        self,
        name: str,
        mission_type: str,
        domain: str,
        tasks: List[Dict[str, Any]],
        description: Optional[str] = None,
        priority: str = "medium",
        auto_assign_nodes: bool = True
    ) -> str:
        """
        Create a new coordinated mission.
        
        Args:
            name: Mission name
            mission_type: Type of mission
            domain: Primary domain
            tasks: List of mission tasks
            description: Mission description
            priority: Mission priority
            auto_assign_nodes: Whether to auto-assign capable nodes
            
        Returns:
            Mission ID
            
        Raises:
            MissionError: If mission creation fails
        """
        try:
            if not self.node.registered:
                raise MissionError("Node must be registered before creating missions")
            
            mission_data = {
                "name": name,
                "description": description,
                "mission_type": mission_type,
                "domain": domain,
                "priority": priority,
                "tasks": tasks,
                "auto_assign_nodes": auto_assign_nodes,
                "created_by": self.node.node_id
            }
            
            response = await self.node.http_client.post(
                f"{self.node.config.hub_url}/api/v1/missions/create",
                json=mission_data
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    # Extract mission ID from response
                    message = result.get("message", "")
                    if "ID:" in message:
                        mission_id = message.split("ID:")[-1].strip()
                    else:
                        mission_id = f"mission_{datetime.utcnow().timestamp()}"
                    
                    logger.info(f"Mission created: {mission_id}")
                    return mission_id
                else:
                    raise MissionError(f"Mission creation failed: {result.get('message')}")
            else:
                raise MissionError(f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            logger.error(f"Mission creation error: {e}")
            raise MissionError(f"Failed to create mission: {e}")
    
    async def get_mission(self, mission_id: str) -> Optional[Dict[str, Any]]:
        """
        Get mission details.
        
        Args:
            mission_id: Mission identifier
            
        Returns:
            Mission data or None if not found
        """
        try:
            response = await self.node.http_client.get(
                f"{self.node.config.hub_url}/api/v1/missions/{mission_id}"
            )
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                return None
            else:
                raise MissionError(f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            logger.error(f"Mission retrieval error: {e}")
            raise MissionError(f"Failed to get mission: {e}")
    
    async def update_mission_progress(
        self,
        mission_id: str,
        progress_percent: Optional[float] = None,
        status: Optional[str] = None,
        task_updates: Optional[List[Dict[str, Any]]] = None,
        progress_message: Optional[str] = None
    ):
        """
        Update mission progress.
        
        Args:
            mission_id: Mission identifier
            progress_percent: Overall progress percentage
            status: Updated mission status
            task_updates: Task status updates
            progress_message: Progress description
        """
        try:
            update_data = {
                "mission_id": mission_id,
                "updated_by": self.node.node_id
            }
            
            if progress_percent is not None:
                update_data["progress_percent"] = progress_percent
            if status is not None:
                update_data["status"] = status
            if task_updates is not None:
                update_data["task_updates"] = task_updates
            if progress_message is not None:
                update_data["progress_message"] = progress_message
            
            response = await self.node.http_client.put(
                f"{self.node.config.hub_url}/api/v1/missions/{mission_id}/update",
                json=update_data
            )
            
            if response.status_code == 200:
                logger.info(f"Mission {mission_id} updated")
            else:
                logger.error(f"Mission update failed: HTTP {response.status_code}")
                
        except Exception as e:
            logger.error(f"Mission update error: {e}")
    
    async def start_mission(self, mission_id: str):
        """
        Start executing a planned mission.
        
        Args:
            mission_id: Mission identifier
        """
        try:
            response = await self.node.http_client.post(
                f"{self.node.config.hub_url}/api/v1/missions/{mission_id}/start",
                params={"started_by": self.node.node_id}
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Mission started: {result.get('message')}")
                self.active_missions[mission_id] = {"started_at": datetime.utcnow()}
            else:
                logger.error(f"Mission start failed: HTTP {response.status_code}")
                
        except Exception as e:
            logger.error(f"Mission start error: {e}")
    
    async def send_coordination_event(
        self,
        mission_id: str,
        event_type: str,
        message: str,
        data: Optional[Dict[str, Any]] = None,
        target_nodes: Optional[List[str]] = None,
        priority: str = "medium"
    ):
        """
        Send coordination event for mission management.
        
        Args:
            mission_id: Mission identifier
            event_type: Type of coordination event
            message: Event message
            data: Additional event data
            target_nodes: Target node IDs
            priority: Event priority
        """
        try:
            event_data = {
                "event_id": f"event_{datetime.utcnow().timestamp()}",
                "mission_id": mission_id,
                "source_node_id": self.node.node_id,
                "event_type": event_type,
                "message": message,
                "data": data or {},
                "target_node_ids": target_nodes,
                "priority": priority,
                "requires_response": False,
                "broadcast_to_all": target_nodes is None
            }
            
            response = await self.node.http_client.post(
                f"{self.node.config.hub_url}/api/v1/missions/{mission_id}/events",
                json=event_data
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Coordination event sent: {result.get('message')}")
            else:
                logger.error(f"Event send failed: HTTP {response.status_code}")
                
        except Exception as e:
            logger.error(f"Coordination event error: {e}")
    
    def handle_task_assignment(self, task_data: Dict[str, Any]):
        """
        Handle incoming task assignment.
        
        Args:
            task_data: Task assignment data
        """
        task_id = task_data.get("task_id")
        mission_id = task_data.get("mission_id")
        
        if task_id:
            self.assigned_tasks[task_id] = {
                "mission_id": mission_id,
                "assigned_at": datetime.utcnow(),
                "status": "assigned",
                **task_data
            }
            
            logger.info(f"Task assigned: {task_id} for mission {mission_id}")
    
    def complete_task(self, task_id: str, result: Optional[Dict[str, Any]] = None):
        """
        Mark a task as completed.
        
        Args:
            task_id: Task identifier
            result: Task result data
        """
        if task_id in self.assigned_tasks:
            self.assigned_tasks[task_id]["status"] = "completed"
            self.assigned_tasks[task_id]["completed_at"] = datetime.utcnow()
            if result:
                self.assigned_tasks[task_id]["result"] = result
            
            logger.info(f"Task completed: {task_id}")
    
    def get_active_missions(self) -> List[str]:
        """Get list of active mission IDs."""
        return list(self.active_missions.keys())
    
    def get_assigned_tasks(self) -> List[str]:
        """Get list of assigned task IDs."""
        return list(self.assigned_tasks.keys()) 