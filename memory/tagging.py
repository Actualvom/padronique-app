#!/usr/bin/env python3
# memory/tagging.py - Memory tagging for the AI Companion System

import logging
from typing import Dict, List, Set, Any

logger = logging.getLogger(__name__)

class TagManager:
    """
    Tag manager for the AI Companion System.
    
    Responsible for:
    1. Managing tags for memories
    2. Finding memories by tags
    3. Generating tag statistics
    """
    
    def __init__(self):
        """Initialize the TagManager."""
        # Maps tag -> set of memory IDs
        self.tag_to_memories: Dict[str, Set[str]] = {}
        
        # Maps memory ID -> set of tags
        self.memory_to_tags: Dict[str, Set[str]] = {}
        
        logger.info("Tag manager initialized")
    
    def tag_memory(self, memory_id: str, tags: List[str]) -> None:
        """
        Tag a memory with one or more tags.
        
        Args:
            memory_id: ID of the memory to tag
            tags: List of tags to apply
        """
        # Create sets if they don't exist
        if memory_id not in self.memory_to_tags:
            self.memory_to_tags[memory_id] = set()
        
        # Add each tag
        for tag in tags:
            # Normalize tag
            tag = tag.strip().lower()
            
            # Skip empty tags
            if not tag:
                continue
            
            # Create tag set if it doesn't exist
            if tag not in self.tag_to_memories:
                self.tag_to_memories[tag] = set()
            
            # Add memory to tag set
            self.tag_to_memories[tag].add(memory_id)
            
            # Add tag to memory set
            self.memory_to_tags[memory_id].add(tag)
    
    def untag_memory(self, memory_id: str, tags: List[str] = None) -> None:
        """
        Remove tags from a memory.
        
        Args:
            memory_id: ID of the memory to untag
            tags: List of tags to remove, or all tags if None
        """
        # Skip if memory has no tags
        if memory_id not in self.memory_to_tags:
            return
        
        # If no tags specified, remove all tags
        if tags is None:
            all_tags = list(self.memory_to_tags[memory_id])
            for tag in all_tags:
                # Remove memory from tag set
                if tag in self.tag_to_memories:
                    self.tag_to_memories[tag].discard(memory_id)
                    
                    # Remove empty tag sets
                    if not self.tag_to_memories[tag]:
                        del self.tag_to_memories[tag]
            
            # Remove memory from tracking
            del self.memory_to_tags[memory_id]
        else:
            # Remove specific tags
            for tag in tags:
                # Normalize tag
                tag = tag.strip().lower()
                
                # Remove memory from tag set
                if tag in self.tag_to_memories:
                    self.tag_to_memories[tag].discard(memory_id)
                    
                    # Remove empty tag sets
                    if not self.tag_to_memories[tag]:
                        del self.tag_to_memories[tag]
                
                # Remove tag from memory set
                if memory_id in self.memory_to_tags:
                    self.memory_to_tags[memory_id].discard(tag)
                    
                    # Remove empty memory sets
                    if not self.memory_to_tags[memory_id]:
                        del self.memory_to_tags[memory_id]
    
    def get_memories_by_tag(self, tag: str) -> List[str]:
        """
        Get memory IDs that have a specific tag.
        
        Args:
            tag: Tag to search for
            
        Returns:
            List of memory IDs with the tag
        """
        # Normalize tag
        tag = tag.strip().lower()
        
        if tag in self.tag_to_memories:
            return list(self.tag_to_memories[tag])
        return []
    
    def get_memories_by_tags(self, tags: List[str], require_all: bool = True) -> List[str]:
        """
        Get memory IDs that have specific tags.
        
        Args:
            tags: List of tags to search for
            require_all: If True, memories must have all tags; if False, any tag
            
        Returns:
            List of memory IDs with the specified tags
        """
        if not tags:
            return []
        
        # Normalize tags
        normalized_tags = [tag.strip().lower() for tag in tags if tag.strip()]
        
        if not normalized_tags:
            return []
        
        # Get memory sets for each tag
        memory_sets = []
        for tag in normalized_tags:
            if tag in self.tag_to_memories:
                memory_sets.append(self.tag_to_memories[tag])
        
        if not memory_sets:
            return []
        
        if require_all:
            # Intersection: memories that have ALL the tags
            result = set.intersection(*memory_sets)
        else:
            # Union: memories that have ANY of the tags
            result = set.union(*memory_sets)
        
        return list(result)
    
    def get_tags_for_memory(self, memory_id: str) -> List[str]:
        """
        Get all tags for a specific memory.
        
        Args:
            memory_id: ID of the memory
            
        Returns:
            List of tags for the memory
        """
        if memory_id in self.memory_to_tags:
            return list(self.memory_to_tags[memory_id])
        return []
    
    def get_all_tags(self) -> List[str]:
        """
        Get a list of all tags.
        
        Returns:
            List of all tags
        """
        return list(self.tag_to_memories.keys())
    
    def get_similar_tags(self, tag: str, max_results: int = 5) -> List[str]:
        """
        Get tags similar to the given tag.
        
        Args:
            tag: Tag to find similar tags for
            max_results: Maximum number of results
            
        Returns:
            List of similar tags
        """
        # Normalize tag
        tag = tag.strip().lower()
        
        if not tag:
            return []
        
        # Simple substring matching (could be improved with fuzzy matching)
        similar_tags = []
        for existing_tag in self.tag_to_memories.keys():
            if tag in existing_tag or existing_tag in tag:
                similar_tags.append(existing_tag)
                
            if len(similar_tags) >= max_results:
                break
        
        return similar_tags
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get tag statistics.
        
        Returns:
            Dictionary with tag statistics
        """
        total_tags = len(self.tag_to_memories)
        
        # Get counts of memories per tag
        tag_counts = {}
        for tag, memory_set in self.tag_to_memories.items():
            tag_counts[tag] = len(memory_set)
        
        # Sort tags by popularity
        popular_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)
        
        return {
            'total_tags': total_tags,
            'tagged_memories': len(self.memory_to_tags),
            'popular_tags': popular_tags[:10]  # Top 10 tags
        }
