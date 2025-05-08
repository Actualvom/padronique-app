#!/usr/bin/env python3
# memory/memory_manager.py - Memory management for the AI Companion System

import logging
import time
from typing import Dict, List, Any, Optional
from memory.memory_store import MemoryStore
from memory.tagging import TagManager

logger = logging.getLogger(__name__)

class MemoryManager:
    """
    Memory manager for the AI Companion System.
    
    Responsible for:
    1. Storing and retrieving memories
    2. Managing memory organization with tagging
    3. Handling memory expiration and priority
    4. Providing context for queries
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the MemoryManager.
        
        Args:
            config: Memory configuration from config.yaml
        """
        self.config = config
        self.storage_path = config.get('storage_path', './data/memory')
        self.encryption_enabled = config.get('encryption_enabled', True)
        self.max_memories = config.get('max_memories', 10000)
        self.default_expiry_days = config.get('default_expiry_days', 365)
        
        # Initialize memory store
        self.memory_store = MemoryStore(self.storage_path, self.encryption_enabled)
        
        # Initialize tag manager
        self.tag_manager = TagManager()
        
        # Load existing memories
        self.memory_store.load()
        
        logger.info("Memory manager initialized")
    
    def store_memory(self, memory_data: Dict[str, Any], tags: List[str] = None) -> str:
        """
        Store a memory with optional tags.
        
        Args:
            memory_data: The memory data to store
            tags: List of tags to associate with the memory
            
        Returns:
            ID of the stored memory
        """
        # Add metadata
        memory_data['created'] = time.time()
        memory_data['accessed'] = time.time()
        memory_data['access_count'] = 0
        
        # Set expiry if not provided
        if 'expiry' not in memory_data:
            # Calculate expiry time (current time + default expiry in seconds)
            memory_data['expiry'] = time.time() + (self.default_expiry_days * 24 * 3600)
        
        # Store memory and get its ID
        memory_id = self.memory_store.add(memory_data)
        
        # Add tags
        if tags:
            self.tag_manager.tag_memory(memory_id, tags)
        
        logger.debug(f"Stored memory with ID {memory_id} and tags {tags}")
        
        # Check if we need to prune memories
        if self.memory_store.count() > self.max_memories:
            self._prune_old_memories()
        
        return memory_id
    
    def retrieve_memory(self, memory_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a specific memory by ID.
        
        Args:
            memory_id: ID of the memory to retrieve
            
        Returns:
            Memory data if found, None otherwise
        """
        memory = self.memory_store.get(memory_id)
        
        if memory:
            # Update access metadata
            memory['accessed'] = time.time()
            memory['access_count'] = memory.get('access_count', 0) + 1
            self.memory_store.update(memory_id, memory)
            logger.debug(f"Retrieved memory with ID {memory_id}")
            return memory
        
        logger.debug(f"Memory with ID {memory_id} not found")
        return None
    
    def search_memories(self, query: str, tags: List[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search memories by query text and optional tags.
        
        Args:
            query: Text query to search for
            tags: Optional list of tags to filter by
            limit: Maximum number of results to return
            
        Returns:
            List of matching memory data dictionaries
        """
        # Get IDs of memories with the requested tags
        if tags:
            memory_ids = self.tag_manager.get_memories_by_tags(tags)
            if not memory_ids:
                return []
        else:
            memory_ids = self.memory_store.get_all_ids()
        
        # Filter memories by query text and expiry
        current_time = time.time()
        matching_memories = []
        
        for memory_id in memory_ids:
            memory = self.memory_store.get(memory_id)
            
            # Skip expired memories
            if memory.get('expiry', float('inf')) < current_time:
                continue
            
            # Very basic text search (in a real system, you'd use a proper search engine)
            if query.lower() in str(memory).lower():
                matching_memories.append(memory)
                
                # Update access metadata
                memory['accessed'] = current_time
                memory['access_count'] = memory.get('access_count', 0) + 1
                self.memory_store.update(memory_id, memory)
            
            if len(matching_memories) >= limit:
                break
        
        logger.debug(f"Found {len(matching_memories)} memories matching query '{query}' and tags {tags}")
        return matching_memories
    
    def get_memories_by_tags(self, tags: List[str], limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get memories that have all the specified tags.
        
        Args:
            tags: List of tags to filter by
            limit: Maximum number of results to return
            
        Returns:
            List of matching memory data dictionaries
        """
        memory_ids = self.tag_manager.get_memories_by_tags(tags)
        
        current_time = time.time()
        result = []
        
        for memory_id in memory_ids[:limit]:
            memory = self.memory_store.get(memory_id)
            
            # Skip expired memories
            if memory.get('expiry', float('inf')) < current_time:
                continue
                
            # Update access metadata
            memory['accessed'] = current_time
            memory['access_count'] = memory.get('access_count', 0) + 1
            self.memory_store.update(memory_id, memory)
            
            result.append(memory)
        
        logger.debug(f"Found {len(result)} memories with tags {tags}")
        return result
    
    def delete_memory(self, memory_id: str) -> bool:
        """
        Delete a memory by ID.
        
        Args:
            memory_id: ID of the memory to delete
            
        Returns:
            True if successful, False otherwise
        """
        # Remove from tag manager
        self.tag_manager.untag_memory(memory_id)
        
        # Remove from memory store
        result = self.memory_store.delete(memory_id)
        
        if result:
            logger.debug(f"Deleted memory with ID {memory_id}")
        else:
            logger.debug(f"Failed to delete memory with ID {memory_id}")
        
        return result
    
    def add_tags_to_memory(self, memory_id: str, tags: List[str]) -> bool:
        """
        Add tags to an existing memory.
        
        Args:
            memory_id: ID of the memory
            tags: List of tags to add
            
        Returns:
            True if successful, False otherwise
        """
        if not self.memory_store.exists(memory_id):
            logger.warning(f"Cannot add tags: Memory with ID {memory_id} not found")
            return False
        
        self.tag_manager.tag_memory(memory_id, tags)
        logger.debug(f"Added tags {tags} to memory {memory_id}")
        return True
    
    def remove_tags_from_memory(self, memory_id: str, tags: List[str]) -> bool:
        """
        Remove tags from an existing memory.
        
        Args:
            memory_id: ID of the memory
            tags: List of tags to remove
            
        Returns:
            True if successful, False otherwise
        """
        if not self.memory_store.exists(memory_id):
            logger.warning(f"Cannot remove tags: Memory with ID {memory_id} not found")
            return False
        
        self.tag_manager.untag_memory(memory_id, tags)
        logger.debug(f"Removed tags {tags} from memory {memory_id}")
        return True
    
    def get_memory_context(self, query: str, context_size: int = 5) -> List[Dict[str, Any]]:
        """
        Get relevant memory context for a query.
        
        Args:
            query: Query to get context for
            context_size: Number of memories to include in context
            
        Returns:
            List of relevant memories as context
        """
        # This is a simple implementation
        # A more advanced system would use semantic search or embeddings
        
        # First, try to find memories by exact query
        memories = self.search_memories(query, limit=context_size)
        
        # If we don't have enough, get some recent ones
        if len(memories) < context_size:
            recent_memories = self.get_recent_memories(context_size - len(memories))
            # Add only memories not already in the results
            existing_ids = {mem.get('id') for mem in memories}
            for mem in recent_memories:
                if mem.get('id') not in existing_ids:
                    memories.append(mem)
        
        logger.debug(f"Generated context with {len(memories)} memories for query '{query}'")
        return memories
    
    def get_recent_memories(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get the most recently created memories.
        
        Args:
            limit: Maximum number of memories to return
            
        Returns:
            List of recent memories
        """
        all_memories = [self.memory_store.get(memory_id) for memory_id in self.memory_store.get_all_ids()]
        
        # Filter out expired memories
        current_time = time.time()
        valid_memories = [mem for mem in all_memories if mem.get('expiry', float('inf')) > current_time]
        
        # Sort by creation time (newest first)
        sorted_memories = sorted(valid_memories, key=lambda m: m.get('created', 0), reverse=True)
        
        return sorted_memories[:limit]
    
    def _prune_old_memories(self) -> int:
        """
        Prune old or less important memories to maintain size limits.
        
        Returns:
            Number of memories pruned
        """
        logger.info("Pruning old memories")
        
        # First, remove all expired memories
        current_time = time.time()
        expired_count = 0
        
        for memory_id in self.memory_store.get_all_ids():
            memory = self.memory_store.get(memory_id)
            if memory.get('expiry', float('inf')) < current_time:
                self.delete_memory(memory_id)
                expired_count += 1
        
        # If still over the limit, remove old, less accessed memories
        if self.memory_store.count() > self.max_memories:
            # Get all memories
            all_memories = [(memory_id, self.memory_store.get(memory_id)) 
                           for memory_id in self.memory_store.get_all_ids()]
            
            # Sort by importance (a function of access count and recency)
            def importance(memory_tuple):
                memory_id, memory = memory_tuple
                access_count = memory.get('access_count', 0)
                last_accessed = memory.get('accessed', memory.get('created', 0))
                age = current_time - last_accessed
                
                # Simple importance formula
                return (access_count * 10) - (age / (24 * 3600))  # access count * 10 - days old
            
            sorted_memories = sorted(all_memories, key=importance)
            
            # Delete the least important memories until we're under the limit
            pruned_count = 0
            while len(sorted_memories) > 0 and self.memory_store.count() > self.max_memories:
                memory_id, _ = sorted_memories.pop(0)  # Get least important
                self.delete_memory(memory_id)
                pruned_count += 1
            
            logger.info(f"Pruned {pruned_count} low-importance memories")
            return expired_count + pruned_count
        
        logger.info(f"Pruned {expired_count} expired memories")
        return expired_count
    
    def save_state(self) -> bool:
        """
        Save the current memory state.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self.memory_store.save()
            logger.info("Memory state saved successfully")
            return True
        except Exception as e:
            logger.error(f"Error saving memory state: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get memory statistics.
        
        Returns:
            Dictionary with memory statistics
        """
        total_memories = self.memory_store.count()
        
        # Count memories by type
        memory_types = {}
        current_time = time.time()
        expired_count = 0
        
        for memory_id in self.memory_store.get_all_ids():
            memory = self.memory_store.get(memory_id)
            
            # Check if expired
            if memory.get('expiry', float('inf')) < current_time:
                expired_count += 1
                continue
            
            # Count by type
            memory_type = memory.get('type', 'unknown')
            memory_types[memory_type] = memory_types.get(memory_type, 0) + 1
        
        # Get tag statistics
        tag_stats = self.tag_manager.get_stats()
        
        return {
            'total_memories': total_memories,
            'active_memories': total_memories - expired_count,
            'expired_memories': expired_count,
            'memory_types': memory_types,
            'tags': tag_stats
        }
