"""
Redis Service for NIS HUB

Handles distributed memory, caching, and pub/sub communication
between nodes using Redis as the backend.
"""

import json
import asyncio
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
import redis.asyncio as redis
from redis.asyncio import Redis, ConnectionPool
import pickle
import hashlib

from .logging_service import NISHubLogger

class RedisService:
    """
    Redis service for NIS HUB shared memory and communication.
    """
    
    def __init__(self, 
                 host: str = "localhost",
                 port: int = 6379,
                 db: int = 0,
                 password: Optional[str] = None,
                 max_connections: int = 20):
        """
        Initialize Redis service.
        
        Args:
            host: Redis host
            port: Redis port
            db: Redis database number
            password: Redis password
            max_connections: Maximum connections in pool
        """
        self.host = host
        self.port = port
        self.db = db
        self.password = password
        self.max_connections = max_connections
        
        self.pool: Optional[ConnectionPool] = None
        self.redis: Optional[Redis] = None
        self.pubsub: Optional[redis.client.PubSub] = None
        
        self.logger = NISHubLogger("redis_service")
        
    async def get_node_count(self) -> int:
        """Get count of registered nodes."""
        try:
            if self.redis:
                keys = await self.redis.keys("node:*")
                return len(keys)
            return 0
        except Exception as e:
            self.logger.error(f"Error getting node count: {e}")
            return 0
    
    async def get_mission_count(self) -> int:
        """Get count of active missions."""
        try:
            if self.redis:
                keys = await self.redis.keys("mission:*")
                return len(keys)
            return 0
        except Exception as e:
            self.logger.error(f"Error getting mission count: {e}")
            return 0
    
    async def get_memory_size(self) -> str:
        """Get total memory size used."""
        try:
            if self.redis:
                keys = await self.redis.keys("memory:*")
                total_size = 0
                for key in keys:
                    size = await self.redis.memory_usage(key)
                    if size:
                        total_size += size
                
                # Convert to human readable format
                if total_size < 1024:
                    return f"{total_size}B"
                elif total_size < 1024 * 1024:
                    return f"{total_size/1024:.1f}KB"
                else:
                    return f"{total_size/(1024*1024):.1f}MB"
            return "0B"
        except Exception as e:
            self.logger.error(f"Error getting memory size: {e}")
            return "0B"
        
        # Key prefixes for different data types
        self.PREFIXES = {
            "node": "nis:node:",
            "memory": "nis:memory:",
            "mission": "nis:mission:",
            "heartbeat": "nis:heartbeat:",
            "stats": "nis:stats:",
            "lock": "nis:lock:",
            "session": "nis:session:",
            "cache": "nis:cache:"
        }
    
    async def initialize(self) -> bool:
        """
        Initialize Redis connection pool and test connectivity.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            self.logger.info("Initializing Redis connection")
            
            # Create connection pool
            self.pool = ConnectionPool(
                host=self.host,
                port=self.port,
                db=self.db,
                password=self.password,
                max_connections=self.max_connections,
                decode_responses=True
            )
            
            # Create Redis instance
            self.redis = Redis(connection_pool=self.pool)
            
            # Test connection
            await self.redis.ping()
            
            # Initialize pub/sub
            self.pubsub = self.redis.pubsub()
            
            self.logger.info("Redis connection initialized successfully",
                           host=self.host, port=self.port, db=self.db)
            
            return True
            
        except Exception as e:
            self.logger.error("Failed to initialize Redis connection", error=e)
            return False
    
    async def close(self):
        """Close Redis connections."""
        try:
            if self.pubsub:
                await self.pubsub.close()
            if self.redis:
                await self.redis.close()
            if self.pool:
                await self.pool.disconnect()
            
            self.logger.info("Redis connections closed")
            
        except Exception as e:
            self.logger.error("Error closing Redis connections", error=e)
    
    async def ping(self) -> bool:
        """Test Redis connectivity."""
        try:
            if self.redis:
                await self.redis.ping()
                return True
            return False
        except Exception:
            return False
    
    # Node Management
    async def register_node(self, node_data: Dict[str, Any]) -> str:
        """
        Register a node in Redis.
        
        Args:
            node_data: Node information dictionary
            
        Returns:
            Node ID
        """
        try:
            node_id = node_data.get("node_id") or self._generate_node_id(node_data["name"])
            node_key = f"{self.PREFIXES['node']}{node_id}"
            
            # Add timestamps
            node_data["registered_at"] = datetime.utcnow().isoformat()
            node_data["last_seen"] = datetime.utcnow().isoformat()
            node_data["node_id"] = node_id
            
            # Store node data
            await self.redis.hset(node_key, mapping=self._serialize_dict(node_data))
            
            # Add to active nodes set
            await self.redis.sadd("nis:active_nodes", node_id)
            
            # Set expiration for heartbeat monitoring
            await self.redis.expire(node_key, 300)  # 5 minutes
            
            self.logger.info("Node registered", node_id=node_id, name=node_data.get("name"))
            
            return node_id
            
        except Exception as e:
            self.logger.error("Failed to register node", error=e)
            raise
    
    async def update_node_heartbeat(self, node_id: str, heartbeat_data: Dict[str, Any]) -> bool:
        """
        Update node heartbeat information.
        
        Args:
            node_id: Node identifier
            heartbeat_data: Heartbeat information
            
        Returns:
            True if successful
        """
        try:
            node_key = f"{self.PREFIXES['node']}{node_id}"
            heartbeat_key = f"{self.PREFIXES['heartbeat']}{node_id}"
            
            # Update last seen timestamp
            await self.redis.hset(node_key, "last_seen", datetime.utcnow().isoformat())
            
            # Store heartbeat data
            await self.redis.hset(heartbeat_key, mapping=self._serialize_dict(heartbeat_data))
            
            # Reset expiration
            await self.redis.expire(node_key, 300)
            await self.redis.expire(heartbeat_key, 300)
            
            return True
            
        except Exception as e:
            self.logger.error("Failed to update heartbeat", node_id=node_id, error=e)
            return False
    
    async def get_node(self, node_id: str) -> Optional[Dict[str, Any]]:
        """Get node information."""
        try:
            node_key = f"{self.PREFIXES['node']}{node_id}"
            node_data = await self.redis.hgetall(node_key)
            
            if node_data:
                return self._deserialize_dict(node_data)
            return None
            
        except Exception as e:
            self.logger.error("Failed to get node", node_id=node_id, error=e)
            return None
    
    async def get_all_nodes(self) -> List[Dict[str, Any]]:
        """Get all registered nodes."""
        try:
            active_nodes = await self.redis.smembers("nis:active_nodes")
            nodes = []
            
            for node_id in active_nodes:
                node_data = await self.get_node(node_id)
                if node_data:
                    nodes.append(node_data)
            
            return nodes
            
        except Exception as e:
            self.logger.error("Failed to get all nodes", error=e)
            return []
    
    async def remove_node(self, node_id: str) -> bool:
        """Remove a node from the registry."""
        try:
            node_key = f"{self.PREFIXES['node']}{node_id}"
            heartbeat_key = f"{self.PREFIXES['heartbeat']}{node_id}"
            
            await self.redis.delete(node_key, heartbeat_key)
            await self.redis.srem("nis:active_nodes", node_id)
            
            self.logger.info("Node removed", node_id=node_id)
            return True
            
        except Exception as e:
            self.logger.error("Failed to remove node", node_id=node_id, error=e)
            return False
    
    # Memory Management
    async def store_memory(self, memory_data: Dict[str, Any]) -> str:
        """
        Store memory entry in Redis.
        
        Args:
            memory_data: Memory entry data
            
        Returns:
            Memory entry ID
        """
        try:
            entry_id = memory_data.get("entry_id") or self._generate_memory_id()
            memory_key = f"{self.PREFIXES['memory']}{entry_id}"
            
            # Add timestamps and ID
            memory_data["entry_id"] = entry_id
            memory_data["created_at"] = datetime.utcnow().isoformat()
            memory_data["last_accessed"] = datetime.utcnow().isoformat()
            
            # Store memory data
            await self.redis.hset(memory_key, mapping=self._serialize_dict(memory_data))
            
            # Add to domain index
            domain = memory_data.get("domain", "unknown")
            await self.redis.sadd(f"nis:memory:domain:{domain}", entry_id)
            
            # Add to type index
            memory_type = memory_data.get("memory_type", "unknown")
            await self.redis.sadd(f"nis:memory:type:{memory_type}", entry_id)
            
            # Add to source node index
            source_node = memory_data.get("source_node_id")
            if source_node:
                await self.redis.sadd(f"nis:memory:node:{source_node}", entry_id)
            
            # Set expiration if specified
            if "expires_at" in memory_data and memory_data["expires_at"]:
                expire_time = datetime.fromisoformat(memory_data["expires_at"])
                ttl = int((expire_time - datetime.utcnow()).total_seconds())
                if ttl > 0:
                    await self.redis.expire(memory_key, ttl)
            
            self.logger.info("Memory stored", entry_id=entry_id, domain=domain, type=memory_type)
            
            return entry_id
            
        except Exception as e:
            self.logger.error("Failed to store memory", error=e)
            raise
    
    async def get_memory(self, entry_id: str) -> Optional[Dict[str, Any]]:
        """Get memory entry by ID."""
        try:
            memory_key = f"{self.PREFIXES['memory']}{entry_id}"
            memory_data = await self.redis.hgetall(memory_key)
            
            if memory_data:
                # Update access count and timestamp
                await self.redis.hincrby(memory_key, "access_count", 1)
                await self.redis.hset(memory_key, "last_accessed", datetime.utcnow().isoformat())
                
                return self._deserialize_dict(memory_data)
            return None
            
        except Exception as e:
            self.logger.error("Failed to get memory", entry_id=entry_id, error=e)
            return None
    
    async def query_memory(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Query memory entries with filters."""
        try:
            # Build query based on filters
            candidate_ids = set()
            
            # Filter by domain
            if "domains" in filters and filters["domains"]:
                domain_ids = set()
                for domain in filters["domains"]:
                    domain_set = await self.redis.smembers(f"nis:memory:domain:{domain}")
                    domain_ids.update(domain_set)
                candidate_ids = domain_ids if not candidate_ids else candidate_ids.intersection(domain_ids)
            
            # Filter by memory type
            if "memory_types" in filters and filters["memory_types"]:
                type_ids = set()
                for memory_type in filters["memory_types"]:
                    type_set = await self.redis.smembers(f"nis:memory:type:{memory_type}")
                    type_ids.update(type_set)
                candidate_ids = type_ids if not candidate_ids else candidate_ids.intersection(type_ids)
            
            # Filter by source node
            if "source_node_ids" in filters and filters["source_node_ids"]:
                node_ids = set()
                for node_id in filters["source_node_ids"]:
                    node_set = await self.redis.smembers(f"nis:memory:node:{node_id}")
                    node_ids.update(node_set)
                candidate_ids = node_ids if not candidate_ids else candidate_ids.intersection(node_ids)
            
            # If no filters specified, get all memory entries
            if not candidate_ids:
                pattern = f"{self.PREFIXES['memory']}*"
                keys = await self.redis.keys(pattern)
                candidate_ids = {key.replace(self.PREFIXES['memory'], '') for key in keys}
            
            # Fetch memory entries
            memories = []
            for entry_id in candidate_ids:
                memory_data = await self.get_memory(entry_id)
                if memory_data:
                    memories.append(memory_data)
            
            # Apply additional filters (text search, date range, etc.)
            memories = self._apply_memory_filters(memories, filters)
            
            # Sort and paginate
            memories = self._sort_and_paginate_memories(memories, filters)
            
            return memories
            
        except Exception as e:
            self.logger.error("Failed to query memory", error=e)
            return []
    
    # Mission Management
    async def store_mission(self, mission_data: Dict[str, Any]) -> str:
        """Store mission in Redis."""
        try:
            mission_id = mission_data.get("mission_id") or self._generate_mission_id()
            mission_key = f"{self.PREFIXES['mission']}{mission_id}"
            
            mission_data["mission_id"] = mission_id
            mission_data["created_at"] = datetime.utcnow().isoformat()
            
            await self.redis.hset(mission_key, mapping=self._serialize_dict(mission_data))
            
            # Add to active missions set
            await self.redis.sadd("nis:active_missions", mission_id)
            
            # Add to domain index
            domain = mission_data.get("domain", "unknown")
            await self.redis.sadd(f"nis:missions:domain:{domain}", mission_id)
            
            self.logger.info("Mission stored", mission_id=mission_id, domain=domain)
            
            return mission_id
            
        except Exception as e:
            self.logger.error("Failed to store mission", error=e)
            raise
    
    async def get_mission(self, mission_id: str) -> Optional[Dict[str, Any]]:
        """Get mission by ID."""
        try:
            mission_key = f"{self.PREFIXES['mission']}{mission_id}"
            mission_data = await self.redis.hgetall(mission_key)
            
            if mission_data:
                return self._deserialize_dict(mission_data)
            return None
            
        except Exception as e:
            self.logger.error("Failed to get mission", mission_id=mission_id, error=e)
            return None
    
    # Pub/Sub for real-time communication
    async def publish_message(self, channel: str, message: Dict[str, Any]) -> bool:
        """Publish message to Redis channel."""
        try:
            message_str = json.dumps(message, default=str)
            await self.redis.publish(channel, message_str)
            
            self.logger.debug("Message published", channel=channel)
            return True
            
        except Exception as e:
            self.logger.error("Failed to publish message", channel=channel, error=e)
            return False
    
    async def subscribe_to_channel(self, channel: str):
        """Subscribe to Redis channel."""
        try:
            await self.pubsub.subscribe(channel)
            self.logger.info("Subscribed to channel", channel=channel)
            
        except Exception as e:
            self.logger.error("Failed to subscribe to channel", channel=channel, error=e)
    
    # Statistics and monitoring
    async def get_node_count(self) -> int:
        """Get number of registered nodes."""
        try:
            return await self.redis.scard("nis:active_nodes")
        except Exception:
            return 0
    
    async def get_mission_count(self) -> int:
        """Get number of active missions."""
        try:
            return await self.redis.scard("nis:active_missions")
        except Exception:
            return 0
    
    async def get_memory_size(self) -> int:
        """Get approximate memory usage."""
        try:
            info = await self.redis.info("memory")
            return info.get("used_memory", 0)
        except Exception:
            return 0
    
    # Utility methods
    def _generate_node_id(self, name: str) -> str:
        """Generate unique node ID."""
        timestamp = datetime.utcnow().isoformat()
        hash_input = f"{name}:{timestamp}"
        return f"node_{hashlib.md5(hash_input.encode()).hexdigest()[:8]}"
    
    def _generate_memory_id(self) -> str:
        """Generate unique memory entry ID."""
        timestamp = datetime.utcnow().isoformat()
        return f"mem_{hashlib.md5(timestamp.encode()).hexdigest()[:12]}"
    
    def _generate_mission_id(self) -> str:
        """Generate unique mission ID."""
        timestamp = datetime.utcnow().isoformat()
        return f"mission_{hashlib.md5(timestamp.encode()).hexdigest()[:10]}"
    
    def _serialize_dict(self, data: Dict[str, Any]) -> Dict[str, str]:
        """Serialize dictionary values for Redis storage."""
        serialized = {}
        for key, value in data.items():
            if isinstance(value, (dict, list)):
                serialized[key] = json.dumps(value, default=str)
            else:
                serialized[key] = str(value)
        return serialized
    
    def _deserialize_dict(self, data: Dict[str, str]) -> Dict[str, Any]:
        """Deserialize dictionary values from Redis."""
        deserialized = {}
        for key, value in data.items():
            try:
                # Try to parse as JSON first
                deserialized[key] = json.loads(value)
            except (json.JSONDecodeError, TypeError):
                # If not JSON, keep as string
                deserialized[key] = value
        return deserialized
    
    def _apply_memory_filters(self, memories: List[Dict[str, Any]], filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Apply additional filters to memory entries."""
        # TODO: Implement text search, date range, and other filters
        return memories
    
    def _sort_and_paginate_memories(self, memories: List[Dict[str, Any]], filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Sort and paginate memory entries."""
        # TODO: Implement sorting and pagination
        return memories 