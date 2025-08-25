"""
Memory Service for NIS-HUB v3.1

Handles shared memory management and synchronization between nodes.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class MemoryService:
    """Service for managing shared memory in the hub."""
    
    def __init__(self, redis_service=None):
        """Initialize the memory service."""
        self.redis_service = redis_service
        logger.info("🧠 Memory Service initialized")
    
    async def store_memory(self, memory_id: str, memory_data: Dict[str, Any]) -> Dict[str, Any]:
        """Store a memory entry."""
        try:
            stored_data = {
                "memory_id": memory_id,
                "stored_at": datetime.utcnow().isoformat(),
                "data": memory_data
            }
            
            if self.redis_service:
                await self.redis_service.set(f"memory:{memory_id}", stored_data)
            
            logger.info(f"Memory stored: {memory_id}")
            return {"status": "success", "memory": stored_data}
            
        except Exception as e:
            logger.error(f"Error storing memory {memory_id}: {e}")
            return {"status": "error", "message": str(e)}
    
    async def get_memory(self, memory_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a memory entry."""
        try:
            if self.redis_service:
                return await self.redis_service.get(f"memory:{memory_id}")
            return None
        except Exception as e:
            logger.error(f"Error getting memory {memory_id}: {e}")
            return None
    
    async def list_memories(self) -> List[Dict[str, Any]]:
        """List all memory entries."""
        try:
            if self.redis_service:
                memory_keys = await self.redis_service.keys("memory:*")
                memories = []
                for key in memory_keys:
                    memory_data = await self.redis_service.get(key)
                    if memory_data:
                        memories.append(memory_data)
                return memories
            return []
        except Exception as e:
            logger.error(f"Error listing memories: {e}")
            return []
    
    async def delete_memory(self, memory_id: str) -> Dict[str, Any]:
        """Delete a memory entry."""
        try:
            if self.redis_service:
                deleted = await self.redis_service.delete(f"memory:{memory_id}")
                if deleted:
                    return {"status": "success", "message": "Memory deleted"}
                else:
                    return {"status": "error", "message": "Memory not found"}
            return {"status": "error", "message": "Redis service not available"}
        except Exception as e:
            logger.error(f"Error deleting memory {memory_id}: {e}")
            return {"status": "error", "message": str(e)}
