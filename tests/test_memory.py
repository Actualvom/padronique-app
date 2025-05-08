#!/usr/bin/env python3
# tests/test_memory.py - Tests for memory system components

import os
import unittest
import tempfile
import shutil
import json
import time
from typing import Dict, Any, List

from memory.memory_manager import MemoryManager
from memory.memory_store import MemoryStore
from memory.tagging import TagManager

class TestTagManager(unittest.TestCase):
    """Tests for the TagManager class."""
    
    def setUp(self):
        """Set up test environment."""
        self.tag_manager = TagManager()
    
    def test_tag_memory(self):
        """Test tagging a memory."""
        memory_id = "test-memory-id"
        tags = ["test", "important", "reminder"]
        
        self.tag_manager.tag_memory(memory_id, tags)
        
        # Check that the memory has the tags
        memory_tags = self.tag_manager.get_tags_for_memory(memory_id)
        self.assertEqual(set(memory_tags), set(tags))
        
        # Check that the tags have the memory
        for tag in tags:
            memories = self.tag_manager.get_memories_by_tag(tag)
            self.assertIn(memory_id, memories)
    
    def test_untag_memory(self):
        """Test removing tags from a memory."""
        memory_id = "test-memory-id"
        tags = ["test", "important", "reminder"]
        
        # Add tags
        self.tag_manager.tag_memory(memory_id, tags)
        
        # Remove one tag
        self.tag_manager.untag_memory(memory_id, ["important"])
        
        # Check remaining tags
        memory_tags = self.tag_manager.get_tags_for_memory(memory_id)
        self.assertEqual(set(memory_tags), {"test", "reminder"})
        
        # Check that the removed tag no longer has the memory
        important_memories = self.tag_manager.get_memories_by_tag("important")
        self.assertNotIn(memory_id, important_memories)
        
        # Remove all tags
        self.tag_manager.untag_memory(memory_id)
        
        # Check that no tags remain
        memory_tags = self.tag_manager.get_tags_for_memory(memory_id)
        self.assertEqual(memory_tags, [])
    
    def test_get_memories_by_tags(self):
        """Test retrieving memories with multiple tags."""
        # Add memories with various tags
        self.tag_manager.tag_memory("memory1", ["tag1", "tag2", "tag3"])
        self.tag_manager.tag_memory("memory2", ["tag1", "tag2"])
        self.tag_manager.tag_memory("memory3", ["tag1"])
        self.tag_manager.tag_memory("memory4", ["tag4"])
        
        # Test requiring all tags (intersection)
        memories = self.tag_manager.get_memories_by_tags(["tag1", "tag2"], require_all=True)
        self.assertEqual(set(memories), {"memory1", "memory2"})
        
        # Test requiring any tag (union)
        memories = self.tag_manager.get_memories_by_tags(["tag1", "tag4"], require_all=False)
        self.assertEqual(set(memories), {"memory1", "memory2", "memory3", "memory4"})
        
        # Test with tags that have no memories
        memories = self.tag_manager.get_memories_by_tags(["nonexistent"], require_all=True)
        self.assertEqual(memories, [])
    
    def test_get_all_tags(self):
        """Test retrieving all tags."""
        # Add memories with various tags
        self.tag_manager.tag_memory("memory1", ["tag1", "tag2", "tag3"])
        self.tag_manager.tag_memory("memory2", ["tag4", "tag5"])
        
        # Get all tags
        all_tags = self.tag_manager.get_all_tags()
        self.assertEqual(set(all_tags), {"tag1", "tag2", "tag3", "tag4", "tag5"})
    
    def test_get_similar_tags(self):
        """Test finding similar tags."""
        # Add memories with various tags
        self.tag_manager.tag_memory("memory1", ["test", "testing", "tester"])
        self.tag_manager.tag_memory("memory2", ["important", "priority"])
        
        # Find similar tags
        similar = self.tag_manager.get_similar_tags("test")
        self.assertTrue(all(tag in similar for tag in ["test", "testing", "tester"]))
        
        # Find similar with no match
        similar = self.tag_manager.get_similar_tags("nonexistent")
        self.assertEqual(similar, [])
    
    def test_get_stats(self):
        """Test getting tag statistics."""
        # Add memories with various tags
        self.tag_manager.tag_memory("memory1", ["tag1", "tag2"])
        self.tag_manager.tag_memory("memory2", ["tag1", "tag3"])
        self.tag_manager.tag_memory("memory3", ["tag1"])
        
        # Get statistics
        stats = self.tag_manager.get_stats()
        
        # Check counts
        self.assertEqual(stats["total_tags"], 3)
        self.assertEqual(stats["tagged_memories"], 3)
        
        # Check popular tags
        popular_tags = stats["popular_tags"]
        self.assertEqual(len(popular_tags), 3)
        
        # tag1 should be the most popular
        self.assertEqual(popular_tags[0][0], "tag1")
        self.assertEqual(popular_tags[0][1], 3)


class TestMemoryStore(unittest.TestCase):
    """Tests for the MemoryStore class."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.store = MemoryStore(self.temp_dir, encryption_enabled=False)
    
    def tearDown(self):
        """Clean up after tests."""
        shutil.rmtree(self.temp_dir)
    
    def test_add_memory(self):
        """Test adding a memory to the store."""
        memory_data = {
            "type": "test",
            "content": "Test memory content"
        }
        
        memory_id = self.store.add(memory_data)
        
        # Check that the memory was added
        self.assertTrue(self.store.exists(memory_id))
        
        # Check that the memory data is correct
        retrieved = self.store.get(memory_id)
        self.assertEqual(retrieved["type"], memory_data["type"])
        self.assertEqual(retrieved["content"], memory_data["content"])
        self.assertEqual(retrieved["id"], memory_id)
    
    def test_update_memory(self):
        """Test updating a memory in the store."""
        # Add initial memory
        memory_data = {
            "type": "test",
            "content": "Original content"
        }
        memory_id = self.store.add(memory_data)
        
        # Update the memory
        updated_data = {
            "type": "test",
            "content": "Updated content"
        }
        result = self.store.update(memory_id, updated_data)
        
        # Check update was successful
        self.assertTrue(result)
        
        # Check that the memory data was updated
        retrieved = self.store.get(memory_id)
        self.assertEqual(retrieved["content"], "Updated content")
    
    def test_delete_memory(self):
        """Test deleting a memory from the store."""
        # Add memory
        memory_data = {"type": "test", "content": "Test content"}
        memory_id = self.store.add(memory_data)
        
        # Delete memory
        result = self.store.delete(memory_id)
        
        # Check deletion was successful
        self.assertTrue(result)
        
        # Check that the memory no longer exists
        self.assertFalse(self.store.exists(memory_id))
    
    def test_get_all_ids(self):
        """Test retrieving all memory IDs."""
        # Add memories
        id1 = self.store.add({"type": "test1"})
        id2 = self.store.add({"type": "test2"})
        id3 = self.store.add({"type": "test3"})
        
        # Get all IDs
        all_ids = self.store.get_all_ids()
        
        # Check that all IDs are in the result
        self.assertIn(id1, all_ids)
        self.assertIn(id2, all_ids)
        self.assertIn(id3, all_ids)
    
    def test_count(self):
        """Test counting memories in the store."""
        # Initially empty
        self.assertEqual(self.store.count(), 0)
        
        # Add memories
        self.store.add({"type": "test1"})
        self.store.add({"type": "test2"})
        
        # Check count
        self.assertEqual(self.store.count(), 2)
        
        # Add another memory
        self.store.add({"type": "test3"})
        
        # Check count again
        self.assertEqual(self.store.count(), 3)
    
    def test_save_and_load(self):
        """Test saving and loading memories."""
        # Add memories
        id1 = self.store.add({"type": "test1", "content": "Content 1"})
        id2 = self.store.add({"type": "test2", "content": "Content 2"})
        
        # Save to disk
        self.store.save()
        
        # Create a new store and load from disk
        new_store = MemoryStore(self.temp_dir, encryption_enabled=False)
        new_store.load()
        
        # Check that memories were loaded
        self.assertEqual(new_store.count(), 2)
        self.assertTrue(new_store.exists(id1))
        self.assertTrue(new_store.exists(id2))
        
        # Check content
        memory1 = new_store.get(id1)
        self.assertEqual(memory1["content"], "Content 1")


class TestMemoryManager(unittest.TestCase):
    """Tests for the MemoryManager class."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.config = {
            "storage_path": self.temp_dir,
            "encryption_enabled": False,
            "max_memories": 10,
            "default_expiry_days": 1
        }
        self.memory_manager = MemoryManager(self.config)
    
    def tearDown(self):
        """Clean up after tests."""
        shutil.rmtree(self.temp_dir)
    
    def test_store_and_retrieve_memory(self):
        """Test storing and retrieving a memory."""
        memory_data = {
            "type": "test",
            "content": "Test memory content"
        }
        
        # Store memory
        memory_id = self.memory_manager.store_memory(memory_data, tags=["test", "example"])
        
        # Retrieve memory
        retrieved = self.memory_manager.retrieve_memory(memory_id)
        
        # Check content
        self.assertEqual(retrieved["type"], memory_data["type"])
        self.assertEqual(retrieved["content"], memory_data["content"])
        
        # Check metadata
        self.assertIn("created", retrieved)
        self.assertIn("accessed", retrieved)
        self.assertIn("access_count", retrieved)
        self.assertIn("expiry", retrieved)
        self.assertEqual(retrieved["access_count"], 1)  # First access from retrieve
        
        # Check tags
        tags = self.memory_manager.tag_manager.get_tags_for_memory(memory_id)
        self.assertEqual(set(tags), {"test", "example"})
    
    def test_search_memories(self):
        """Test searching for memories."""
        # Add test memories
        self.memory_manager.store_memory(
            {"type": "note", "content": "Remember to buy milk"}, 
            tags=["reminder", "shopping"]
        )
        self.memory_manager.store_memory(
            {"type": "note", "content": "Call mom tomorrow"}, 
            tags=["reminder", "family"]
        )
        self.memory_manager.store_memory(
            {"type": "fact", "content": "Paris is the capital of France"}, 
            tags=["geography", "knowledge"]
        )
        
        # Search by text
        results = self.memory_manager.search_memories("milk")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["content"], "Remember to buy milk")
        
        # Search by tags
        results = self.memory_manager.search_memories("", tags=["reminder"])
        self.assertEqual(len(results), 2)
        
        # Search by text and tags
        results = self.memory_manager.search_memories("call", tags=["family"])
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["content"], "Call mom tomorrow")
    
    def test_get_memories_by_tags(self):
        """Test retrieving memories by tags."""
        # Add test memories
        self.memory_manager.store_memory(
            {"type": "note", "content": "Memory 1"}, 
            tags=["tag1", "tag2"]
        )
        self.memory_manager.store_memory(
            {"type": "note", "content": "Memory 2"}, 
            tags=["tag1", "tag3"]
        )
        self.memory_manager.store_memory(
            {"type": "note", "content": "Memory 3"}, 
            tags=["tag3", "tag4"]
        )
        
        # Get memories with tag1
        results = self.memory_manager.get_memories_by_tags(["tag1"])
        self.assertEqual(len(results), 2)
        
        # Get memories with tag3
        results = self.memory_manager.get_memories_by_tags(["tag3"])
        self.assertEqual(len(results), 2)
        
        # Get memories with both tag1 and tag3
        results = self.memory_manager.get_memories_by_tags(["tag1", "tag3"])
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["content"], "Memory 2")
    
    def test_delete_memory(self):
        """Test deleting a memory."""
        # Add memory
        memory_id = self.memory_manager.store_memory(
            {"type": "note", "content": "Temporary note"}, 
            tags=["temporary"]
        )
        
        # Confirm it exists
        self.assertIsNotNone(self.memory_manager.retrieve_memory(memory_id))
        
        # Delete memory
        result = self.memory_manager.delete_memory(memory_id)
        
        # Check deletion was successful
        self.assertTrue(result)
        
        # Confirm it's gone
        self.assertIsNone(self.memory_manager.retrieve_memory(memory_id))
        
        # Check that tags were removed
        tags = self.memory_manager.tag_manager.get_tags_for_memory(memory_id)
        self.assertEqual(tags, [])
    
    def test_add_and_remove_tags(self):
        """Test adding and removing tags from a memory."""
        # Add memory with initial tags
        memory_id = self.memory_manager.store_memory(
            {"type": "note", "content": "Tagged note"}, 
            tags=["initial"]
        )
        
        # Add more tags
        result = self.memory_manager.add_tags_to_memory(memory_id, ["additional", "tags"])
        self.assertTrue(result)
        
        # Check tags were added
        tags = self.memory_manager.tag_manager.get_tags_for_memory(memory_id)
        self.assertEqual(set(tags), {"initial", "additional", "tags"})
        
        # Remove a tag
        result = self.memory_manager.remove_tags_from_memory(memory_id, ["additional"])
        self.assertTrue(result)
        
        # Check tag was removed
        tags = self.memory_manager.tag_manager.get_tags_for_memory(memory_id)
        self.assertEqual(set(tags), {"initial", "tags"})
    
    def test_memory_expiry(self):
        """Test memory expiration."""
        # Add memory with short expiry (1 second)
        memory_data = {
            "type": "temp",
            "content": "This will expire soon",
            "expiry": time.time() + 1  # 1 second from now
        }
        memory_id = self.memory_manager.store_memory(memory_data)
        
        # Verify it exists initially
        memory = self.memory_manager.retrieve_memory(memory_id)
        self.assertIsNotNone(memory)
        
        # Wait for expiry
        time.sleep(1.5)
        
        # Search should not return expired memory
        results = self.memory_manager.search_memories("expire")
        self.assertEqual(len(results), 0)
        
        # Direct retrieval should still work
        memory = self.memory_manager.retrieve_memory(memory_id)
        self.assertIsNotNone(memory)
    
    def test_memory_context(self):
        """Test getting memory context for a query."""
        # Add several memories
        self.memory_manager.store_memory(
            {"type": "fact", "content": "Context test memory one"},
            tags=["context", "test"]
        )
        self.memory_manager.store_memory(
            {"type": "fact", "content": "Context test memory two"},
            tags=["context", "test"]
        )
        self.memory_manager.store_memory(
            {"type": "fact", "content": "Unrelated memory"},
            tags=["unrelated"]
        )
        
        # Get context for query
        context = self.memory_manager.get_memory_context("context test")
        
        # Check context
        self.assertGreaterEqual(len(context), 2)
        
        # Check that it contains relevant memories
        contents = [mem["content"] for mem in context]
        self.assertTrue(any("Context test memory" in content for content in contents))
    
    def test_get_recent_memories(self):
        """Test retrieving recent memories."""
        # Add memories with different creation times
        memory_data1 = {"type": "note", "content": "Oldest memory"}
        memory_data1["created"] = time.time() - 3600  # 1 hour ago
        self.memory_manager.memory_store.add(memory_data1)
        
        memory_data2 = {"type": "note", "content": "Newer memory"}
        memory_data2["created"] = time.time() - 1800  # 30 minutes ago
        self.memory_manager.memory_store.add(memory_data2)
        
        memory_data3 = {"type": "note", "content": "Newest memory"}
        memory_data3["created"] = time.time()  # Now
        self.memory_manager.memory_store.add(memory_data3)
        
        # Get recent memories
        recent = self.memory_manager.get_recent_memories(2)
        
        # Check order (newest first)
        self.assertEqual(len(recent), 2)
        self.assertEqual(recent[0]["content"], "Newest memory")
        self.assertEqual(recent[1]["content"], "Newer memory")
    
    def test_prune_old_memories(self):
        """Test pruning old memories when exceeding the limit."""
        # Configure a memory manager with a small limit
        config = {
            "storage_path": self.temp_dir,
            "encryption_enabled": False,
            "max_memories": 2,  # Only allow 2 memories
            "default_expiry_days": 1
        }
        manager = MemoryManager(config)
        
        # Add more memories than the limit
        id1 = manager.store_memory({"type": "note", "content": "Memory 1"})
        id2 = manager.store_memory({"type": "note", "content": "Memory 2"})
        id3 = manager.store_memory({"type": "note", "content": "Memory 3"})
        
        # Check that we don't exceed the limit
        self.assertLessEqual(manager.memory_store.count(), 2)
        
        # Check which memories survived (should be the newer ones)
        self.assertIsNone(manager.retrieve_memory(id1))  # Should be pruned
        self.assertIsNotNone(manager.retrieve_memory(id2))
        self.assertIsNotNone(manager.retrieve_memory(id3))
    
    def test_get_stats(self):
        """Test getting memory statistics."""
        # Add various types of memories
        self.memory_manager.store_memory(
            {"type": "note", "content": "Note 1"}, 
            tags=["note"]
        )
        self.memory_manager.store_memory(
            {"type": "note", "content": "Note 2"}, 
            tags=["note"]
        )
        self.memory_manager.store_memory(
            {"type": "fact", "content": "Fact 1"}, 
            tags=["fact"]
        )
        
        # Get statistics
        stats = self.memory_manager.get_stats()
        
        # Check counts
        self.assertEqual(stats["total_memories"], 3)
        self.assertEqual(stats["active_memories"], 3)
        self.assertEqual(stats["expired_memories"], 0)
        
        # Check memory types
        self.assertEqual(stats["memory_types"]["note"], 2)
        self.assertEqual(stats["memory_types"]["fact"], 1)


if __name__ == "__main__":
    unittest.main()
