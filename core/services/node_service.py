"""
Node Service for NIS-HUB v3.1

Handles node registration, management, and coordination.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class NodeService:
    """Service for managing NIS nodes in the hub."""
    
    def __init__(self, redis_service=None):
        """Initialize the node service."""
        self.redis_service = redis_service
        logger.info("🔌 Node Service initialized")
    
    async def register_node(self, node_id: str, node_info: Dict[str, Any]) -> Dict[str, Any]:
        """Register a new node with the hub."""
        try:
            registration_data = {
                "node_id": node_id,
                "registered_at": datetime.utcnow().isoformat(),
                "status": "active",
                **node_info
            }
            
            # Store in Redis if available
            if self.redis_service:
                await self.redis_service.set(f"node:{node_id}", registration_data)
            
            logger.info(f"Node registered: {node_id}")
            return {"status": "success", "node": registration_data}
            
        except Exception as e:
            logger.error(f"Error registering node {node_id}: {e}")
            return {"status": "error", "message": str(e)}
    
    async def get_node(self, node_id: str) -> Optional[Dict[str, Any]]:
        """Get node information."""
        try:
            if self.redis_service:
                return await self.redis_service.get(f"node:{node_id}")
            return None
        except Exception as e:
            logger.error(f"Error getting node {node_id}: {e}")
            return None
    
    async def list_nodes(self) -> List[Dict[str, Any]]:
        """List all registered nodes."""
        try:
            if self.redis_service:
                node_keys = await self.redis_service.keys("node:*")
                nodes = []
                for key in node_keys:
                    node_data = await self.redis_service.get(key)
                    if node_data:
                        nodes.append(node_data)
                return nodes
            return []
        except Exception as e:
            logger.error(f"Error listing nodes: {e}")
            return []
    
    async def update_node_status(self, node_id: str, status: str) -> Dict[str, Any]:
        """Update node status."""
        try:
            node_data = await self.get_node(node_id)
            if node_data:
                node_data["status"] = status
                node_data["last_updated"] = datetime.utcnow().isoformat()
                
                if self.redis_service:
                    await self.redis_service.set(f"node:{node_id}", node_data)
                
                return {"status": "success", "node": node_data}
            else:
                return {"status": "error", "message": "Node not found"}
                
        except Exception as e:
            logger.error(f"Error updating node status {node_id}: {e}")
            return {"status": "error", "message": str(e)}
