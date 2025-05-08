#!/usr/bin/env python3
"""
digital_soul.py: Manages personal memories and personality.
Loads memories, applies hierarchical tagging for deep search,
and provides APIs for memory retrieval.
"""

import os
import json
import logging
import time
import datetime
from digital_soul.memory_indexer import index_memories, search_memories
from digital_soul.encryption_utils import encrypt, decrypt

logger = logging.getLogger("padronique.digital_soul")

class DigitalSoul:
    """
    Digital Soul manages the memory and personality system.
    It loads memories, indexes them for search, and provides APIs
    for storing and retrieving memories with hierarchical tags.
    """
    
    def __init__(self, config, memory_dir="digital_soul/memories"):
        """
        Initialize the Digital Soul.
        
        Args:
            config: Configuration dictionary
            memory_dir: Directory for storing memories
        """
        self.config = config
        self.memory_dir = memory_dir
        self.memories = {}
        self.memory_index = {}
        self.personality_traits = {}
        
        # Ensure memory directory exists
        os.makedirs(memory_dir, exist_ok=True)
        
        # Initialize memory system
        self.load_memories()
        self.load_personality()
        
        # Index memories for search
        self.memory_index = index_memories(self.memories)
        
        logger.info("Digital Soul initialized")
    
    def load_memories(self):
        """Load memories from disk."""
        # Initialize memory categories
        for category in ["core", "personal", "interaction", "emotional"]:
            self.memories[category] = []
            
            # Try to load category file
            path = os.path.join(self.memory_dir, f"{category}_memories.json")
            if os.path.exists(path):
                try:
                    with open(path, "r") as f:
                        data = json.load(f)
                        if isinstance(data, list):
                            self.memories[category] = data
                            logger.info(f"Loaded {len(data)} {category} memories")
                except Exception as e:
                    logger.error(f"Error loading {category} memories: {e}")
        
        # Load encrypted credentials if they exist
        creds_path = os.path.join(self.memory_dir, "credentials.enc")
        if os.path.exists(creds_path):
            try:
                # In a real implementation, get key from secure storage
                key = self.config.get("encryption_key", "default_key")
                with open(creds_path, "r") as f:
                    encrypted_data = f.read()
                    decrypted_data = decrypt(encrypted_data, key)
                    self.memories["credentials"] = json.loads(decrypted_data)
                    logger.info("Loaded encrypted credentials")
            except Exception as e:
                logger.error(f"Error loading credentials: {e}")
                self.memories["credentials"] = {}
        else:
            self.memories["credentials"] = {}
    
    def load_personality(self):
        """Load personality traits from disk."""
        path = os.path.join(self.memory_dir, "personality.json")
        if os.path.exists(path):
            try:
                with open(path, "r") as f:
                    self.personality_traits = json.load(f)
                    logger.info("Loaded personality traits")
            except Exception as e:
                logger.error(f"Error loading personality: {e}")
                self.personality_traits = self._default_personality()
        else:
            # Initialize with default personality
            self.personality_traits = self._default_personality()
            self.save_personality()
    
    def _default_personality(self):
        """Create default personality traits."""
        return {
            "openness": 0.8,
            "conscientiousness": 0.7,
            "extraversion": 0.6,
            "agreeableness": 0.7,
            "neuroticism": 0.3,
            "empathy": 0.8,
            "creativity": 0.7,
            "curiosity": 0.9,
            "loyalty": 0.9,
            "protectiveness": 0.8
        }
    
    def save_personality(self):
        """Save personality traits to disk."""
        path = os.path.join(self.memory_dir, "personality.json")
        try:
            with open(path, "w") as f:
                json.dump(self.personality_traits, f, indent=2)
                logger.debug("Saved personality traits")
        except Exception as e:
            logger.error(f"Error saving personality: {e}")
    
    def add_memory(self, category, memory, tags=None):
        """
        Add a new memory with hierarchical tags.
        
        Args:
            category: Memory category (core, personal, interaction, emotional)
            memory: Memory content (string or dict)
            tags: List of tags, can include hierarchical tags (e.g., "emotion:joy:intense")
            
        Returns:
            dict: The stored memory entry
        """
        if tags is None:
            tags = []
        
        # Create memory entry with metadata
        timestamp = time.time()
        date_str = datetime.datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
        
        entry = {
            "memory": memory,
            "tags": tags,
            "timestamp": timestamp,
            "date": date_str
        }
        
        # Add to memory store
        self.memories.setdefault(category, [])
        self.memories[category].append(entry)
        
        # Save to disk
        self._save_category(category)
        
        # Update index
        self.memory_index = index_memories(self.memories)
        
        logger.debug(f"Added memory to {category} with tags {tags}")
        return entry
    
    def add_credential(self, service, credentials):
        """
        Add encrypted credentials.
        
        Args:
            service: Service name
            credentials: Credential dictionary
            
        Returns:
            bool: True if successful
        """
        try:
            # Add/update credentials
            self.memories.setdefault("credentials", {})
            self.memories["credentials"][service] = credentials
            
            # Save encrypted to disk
            self._save_credentials()
            logger.info(f"Added credentials for {service}")
            return True
        except Exception as e:
            logger.error(f"Error adding credentials: {e}")
            return False
    
    def get_credential(self, service):
        """
        Get credentials for a service.
        
        Args:
            service: Service name
            
        Returns:
            dict: Credentials or None if not found
        """
        return self.memories.get("credentials", {}).get(service)
    
    def _save_category(self, category):
        """Save a memory category to disk."""
        try:
            path = os.path.join(self.memory_dir, f"{category}_memories.json")
            with open(path, "w") as f:
                json.dump(self.memories[category], f, indent=2)
                logger.debug(f"Saved {category} memories")
        except Exception as e:
            logger.error(f"Error saving {category} memories: {e}")
    
    def _save_credentials(self):
        """Save encrypted credentials to disk."""
        try:
            # In a real implementation, get key from secure storage
            key = self.config.get("encryption_key", "default_key")
            creds_data = json.dumps(self.memories["credentials"])
            encrypted_data = encrypt(creds_data, key)
            
            path = os.path.join(self.memory_dir, "credentials.enc")
            with open(path, "w") as f:
                f.write(encrypted_data)
                logger.debug("Saved encrypted credentials")
        except Exception as e:
            logger.error(f"Error saving credentials: {e}")
    
    def get_memories(self, category=None, tag_filter=None, limit=10):
        """
        Get memories, optionally filtered by category and tags.
        
        Args:
            category: Optional category to filter by
            tag_filter: Optional list of tags to filter by
            limit: Maximum number of memories to return
            
        Returns:
            list: Matching memories
        """
        if category and category in self.memories:
            # Get memories from a specific category
            memories = self.memories[category]
        else:
            # Combine all categories
            memories = []
            for cat in self.memories:
                if cat != "credentials" and isinstance(self.memories[cat], list):
                    memories.extend(self.memories[cat])
        
        # Apply tag filter if provided
        if tag_filter:
            filtered = []
            for memory in memories:
                tags = memory.get("tags", [])
                # Check if all required tags are present
                if all(self._tag_matches(tag, tags) for tag in tag_filter):
                    filtered.append(memory)
            memories = filtered
        
        # Sort by timestamp (newest first) and limit
        sorted_memories = sorted(
            memories, 
            key=lambda x: x.get("timestamp", 0), 
            reverse=True
        )
        
        return sorted_memories[:limit]
    
    def _tag_matches(self, search_tag, memory_tags):
        """
        Check if a search tag matches any memory tag.
        Supports hierarchical tags (e.g., "emotion:joy" matches "emotion:joy:intense").
        
        Args:
            search_tag: Tag to search for
            memory_tags: List of tags in the memory
            
        Returns:
            bool: True if search tag matches any memory tag
        """
        # Direct match
        if search_tag in memory_tags:
            return True
        
        # Hierarchical match (prefix match)
        for tag in memory_tags:
            if tag.startswith(search_tag + ":"):
                return True
        
        return False
    
    def search_memories(self, query, limit=10):
        """
        Search memories by text content.
        
        Args:
            query: Search query string
            limit: Maximum number of results
            
        Returns:
            list: Matching memories
        """
        results = search_memories(self.memories, self.memory_index, query)
        return results[:limit]
    
    def get_trait(self, trait, default=0.5):
        """
        Get a personality trait value.
        
        Args:
            trait: Trait name
            default: Default value if trait not found
            
        Returns:
            float: Trait value (0.0 to 1.0)
        """
        return self.personality_traits.get(trait, default)
    
    def set_trait(self, trait, value):
        """
        Set a personality trait value.
        
        Args:
            trait: Trait name
            value: Trait value (0.0 to 1.0)
            
        Returns:
            float: New trait value
        """
        # Ensure value is in valid range
        value = max(0.0, min(1.0, value))
        self.personality_traits[trait] = value
        self.save_personality()
        return value
    
    def adjust_trait(self, trait, delta):
        """
        Adjust a personality trait value.
        
        Args:
            trait: Trait name
            delta: Amount to adjust (-1.0 to 1.0)
            
        Returns:
            float: New trait value
        """
        current = self.get_trait(trait, 0.5)
        return self.set_trait(trait, current + delta)
    
    def get_memory_overview(self):
        """
        Get an overview of memories for UI display.
        
        Returns:
            dict: Memory statistics and samples
        """
        stats = {}
        samples = {}
        
        for category in self.memories:
            if category != "credentials" and isinstance(self.memories[category], list):
                stats[category] = len(self.memories[category])
                
                # Get a few recent memories for display
                if self.memories[category]:
                    sorted_memories = sorted(
                        self.memories[category],
                        key=lambda x: x.get("timestamp", 0),
                        reverse=True
                    )
                    samples[category] = sorted_memories[:3]
        
        return {
            "stats": stats,
            "samples": samples,
            "trait_summary": self.personality_traits
        }
