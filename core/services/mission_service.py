"""
Mission Service for NIS-HUB v3.1

Handles mission coordination and multi-node task management.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class MissionService:
    """Service for managing missions and multi-node coordination."""
    
    def __init__(self, redis_service=None):
        """Initialize the mission service."""
        self.redis_service = redis_service
        logger.info("🚀 Mission Service initialized")
    
    async def create_mission(self, mission_id: str, mission_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new mission."""
        try:
            mission = {
                "mission_id": mission_id,
                "created_at": datetime.utcnow().isoformat(),
                "status": "created",
                "participants": [],
                **mission_data
            }
            
            if self.redis_service:
                await self.redis_service.set(f"mission:{mission_id}", mission)
            
            logger.info(f"Mission created: {mission_id}")
            return {"status": "success", "mission": mission}
            
        except Exception as e:
            logger.error(f"Error creating mission {mission_id}: {e}")
            return {"status": "error", "message": str(e)}
    
    async def get_mission(self, mission_id: str) -> Optional[Dict[str, Any]]:
        """Get mission information."""
        try:
            if self.redis_service:
                return await self.redis_service.get(f"mission:{mission_id}")
            return None
        except Exception as e:
            logger.error(f"Error getting mission {mission_id}: {e}")
            return None
    
    async def list_missions(self) -> List[Dict[str, Any]]:
        """List all missions."""
        try:
            if self.redis_service:
                mission_keys = await self.redis_service.keys("mission:*")
                missions = []
                for key in mission_keys:
                    mission_data = await self.redis_service.get(key)
                    if mission_data:
                        missions.append(mission_data)
                return missions
            return []
        except Exception as e:
            logger.error(f"Error listing missions: {e}")
            return []
    
    async def update_mission_status(self, mission_id: str, status: str) -> Dict[str, Any]:
        """Update mission status."""
        try:
            mission_data = await self.get_mission(mission_id)
            if mission_data:
                mission_data["status"] = status
                mission_data["last_updated"] = datetime.utcnow().isoformat()
                
                if self.redis_service:
                    await self.redis_service.set(f"mission:{mission_id}", mission_data)
                
                return {"status": "success", "mission": mission_data}
            else:
                return {"status": "error", "message": "Mission not found"}
                
        except Exception as e:
            logger.error(f"Error updating mission status {mission_id}: {e}")
            return {"status": "error", "message": str(e)}
    
    async def add_participant(self, mission_id: str, node_id: str) -> Dict[str, Any]:
        """Add a participant to a mission."""
        try:
            mission_data = await self.get_mission(mission_id)
            if mission_data:
                if node_id not in mission_data.get("participants", []):
                    mission_data.setdefault("participants", []).append(node_id)
                    mission_data["last_updated"] = datetime.utcnow().isoformat()
                    
                    if self.redis_service:
                        await self.redis_service.set(f"mission:{mission_id}", mission_data)
                
                return {"status": "success", "mission": mission_data}
            else:
                return {"status": "error", "message": "Mission not found"}
                
        except Exception as e:
            logger.error(f"Error adding participant to mission {mission_id}: {e}")
            return {"status": "error", "message": str(e)}
