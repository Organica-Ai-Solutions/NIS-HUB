"""
Memory management for NIS HUB SDK.

Handles memory synchronization and querying operations.
"""

import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from .exceptions import MemoryError

logger = logging.getLogger(__name__)


class MemoryManager:
    """
    Manages memory operations for a NIS node.
    
    Provides methods for syncing memory entries to the HUB,
    querying shared memory, and managing local memory cache.
    """
    
    def __init__(self, node):
        """
        Initialize memory manager.
        
        Args:
            node: Reference to the parent NISNode instance
        """
        self.node = node
        self.local_cache: Dict[str, Any] = {}
        
    async def sync_entries(self, entries: List[Dict[str, Any]], sync_mode: str = "append") -> bool:
        """
        Sync memory entries to the HUB.
        
        Args:
            entries: List of memory entries to sync
            sync_mode: Sync mode ('append', 'update', 'replace')
            
        Returns:
            True if sync successful
            
        Raises:
            MemoryError: If sync fails
        """
        try:
            if not self.node.registered:
                raise MemoryError("Node must be registered before syncing memory")
            
            sync_data = {
                "node_id": self.node.node_id,
                "entries": entries,
                "sync_mode": sync_mode,
                "batch_id": f"batch_{datetime.utcnow().timestamp()}"
            }
            
            response = await self.node.http_client.post(
                f"{self.node.config.hub_url}/api/v1/memory/sync",
                json=sync_data
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    logger.info(f"Synced {len(entries)} memory entries")
                    return True
                else:
                    raise MemoryError(f"Sync failed: {result.get('message')}")
            else:
                raise MemoryError(f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            logger.error(f"Memory sync error: {e}")
            raise MemoryError(f"Failed to sync memory: {e}")
    
    async def query_memory(
        self,
        domains: Optional[List[str]] = None,
        memory_types: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        search_text: Optional[str] = None,
        page: int = 1,
        page_size: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Query memory entries from the HUB.
        
        Args:
            domains: Filter by domains
            memory_types: Filter by memory types
            tags: Filter by tags
            search_text: Text search query
            page: Page number
            page_size: Page size
            
        Returns:
            List of matching memory entries
            
        Raises:
            MemoryError: If query fails
        """
        try:
            if not self.node.registered:
                raise MemoryError("Node must be registered before querying memory")
            
            query_data = {
                "requesting_node_id": self.node.node_id,
                "domains": domains,
                "memory_types": memory_types,
                "tags": tags,
                "search_text": search_text,
                "page": page,
                "page_size": page_size
            }
            
            response = await self.node.http_client.post(
                f"{self.node.config.hub_url}/api/v1/memory/query",
                json=query_data
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    entries = result.get("entries", [])
                    logger.debug(f"Retrieved {len(entries)} memory entries")
                    return entries
                else:
                    raise MemoryError(f"Query failed: {result.get('message')}")
            else:
                raise MemoryError(f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            logger.error(f"Memory query error: {e}")
            raise MemoryError(f"Failed to query memory: {e}")
    
    async def fetch_entry(self, entry_id: str) -> Optional[Dict[str, Any]]:
        """
        Fetch a specific memory entry by ID.
        
        Args:
            entry_id: ID of the memory entry
            
        Returns:
            Memory entry data or None if not found
        """
        try:
            response = await self.node.http_client.get(
                f"{self.node.config.hub_url}/api/v1/memory/fetch/{entry_id}",
                params={"requesting_node_id": self.node.node_id}
            )
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                return None
            else:
                raise MemoryError(f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            logger.error(f"Memory fetch error: {e}")
            raise MemoryError(f"Failed to fetch memory entry: {e}")
    
    async def broadcast_notification(
        self,
        message_type: str,
        title: str,
        content: Dict[str, Any],
        target_domains: Optional[List[str]] = None,
        priority: str = "medium"
    ):
        """
        Broadcast a memory-related notification.
        
        Args:
            message_type: Type of message
            title: Notification title
            content: Notification content
            target_domains: Target domains (None for all)
            priority: Message priority
        """
        try:
            broadcast_data = {
                "source_node_id": self.node.node_id,
                "message_type": message_type,
                "title": title,
                "content": content,
                "target_domains": target_domains,
                "priority": priority
            }
            
            response = await self.node.http_client.post(
                f"{self.node.config.hub_url}/api/v1/memory/broadcast",
                json=broadcast_data
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Broadcast sent: {result.get('message')}")
            else:
                logger.error(f"Broadcast failed: HTTP {response.status_code}")
                
        except Exception as e:
            logger.error(f"Broadcast error: {e}")
    
    def cache_entry(self, entry_id: str, data: Dict[str, Any]):
        """Cache a memory entry locally."""
        self.local_cache[entry_id] = {
            "data": data,
            "cached_at": datetime.utcnow().isoformat()
        }
        
        # Limit cache size
        if len(self.local_cache) > 100:
            # Remove oldest entry
            oldest_key = min(
                self.local_cache.keys(),
                key=lambda k: self.local_cache[k]["cached_at"]
            )
            del self.local_cache[oldest_key]
    
    def get_cached_entry(self, entry_id: str) -> Optional[Dict[str, Any]]:
        """Get a cached memory entry."""
        if entry_id in self.local_cache:
            return self.local_cache[entry_id]["data"]
        return None
    
    def clear_cache(self):
        """Clear the local memory cache."""
        self.local_cache.clear()
        logger.info("Memory cache cleared") 