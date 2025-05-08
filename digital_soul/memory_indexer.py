#!/usr/bin/env python3
"""
memory_indexer.py: Indexes memories for efficient retrieval and searching.
"""

import logging
import re
from collections import defaultdict

logger = logging.getLogger("padronique.memory_indexer")

def index_memories(memories):
    """
    Create a searchable index of memories.
    
    Args:
        memories: Dictionary of memory categories with lists of memory entries
        
    Returns:
        dict: Memory index for efficient searching
    """
    index = {
        "tag_index": defaultdict(list),  # Maps tags to memory entries
        "word_index": defaultdict(list),  # Maps words to memory entries
        "hierarchy_index": defaultdict(list),  # Maps hierarchical tag segments to memory entries
    }
    
    logger.info("Indexing memories...")
    
    # Process each memory category
    memory_count = 0
    for category, memory_list in memories.items():
        # Skip non-list items (like credentials dictionary)
        if not isinstance(memory_list, list):
            continue
            
        for memory_entry in memory_list:
            memory_count += 1
            
            # Extract memory content
            memory_content = memory_entry.get("memory", "")
            # Handle both string and dictionary memory formats
            if isinstance(memory_content, dict) and "content" in memory_content:
                content_text = memory_content["content"]
            elif isinstance(memory_content, str):
                content_text = memory_content
            else:
                content_text = str(memory_content)
            
            # Index by words
            words = tokenize_text(content_text)
            for word in words:
                if len(word) > 2:  # Skip very short words
                    index["word_index"][word].append((category, memory_entry))
            
            # Index by tags
            for tag in memory_entry.get("tags", []):
                index["tag_index"][tag].append((category, memory_entry))
                
                # Handle hierarchical tags (e.g., "emotion:joy:intense")
                if ":" in tag:
                    parts = tag.split(":")
                    # Index each level of the hierarchy
                    for i in range(1, len(parts)):
                        partial_tag = ":".join(parts[:i])
                        index["hierarchy_index"][partial_tag].append((category, memory_entry))
    
    logger.info(f"Indexed {memory_count} memories with {len(index['word_index'])} unique words and {len(index['tag_index'])} unique tags")
    return index

def tokenize_text(text):
    """
    Split text into searchable tokens.
    
    Args:
        text: Text to tokenize
        
    Returns:
        set: Unique tokens
    """
    if not text:
        return set()
        
    # Convert to lowercase and split on word boundaries
    text = text.lower()
    # Remove punctuation and split into words
    words = re.findall(r'\b\w+\b', text)
    return set(words)

def search_memories(memories, index, query, tag_filter=None):
    """
    Search memories using the index.
    
    Args:
        memories: Dictionary of memory categories
        index: Memory index
        query: Search query string
        tag_filter: Optional list of tags to filter by
        
    Returns:
        list: Matching memory entries
    """
    if not query:
        return []
    
    query = query.lower()
    words = tokenize_text(query)
    results = []
    seen = set()  # Track seen memories to avoid duplicates
    
    # Search for exact matches in words
    for word in words:
        if len(word) < 3:  # Skip very short words
            continue
            
        for category, memory in index["word_index"].get(word, []):
            # Create a unique identifier for this memory
            memory_id = (category, memory.get("timestamp", 0))
            if memory_id not in seen:
                seen.add(memory_id)
                
                # Check tag filter if provided
                if tag_filter:
                    memory_tags = memory.get("tags", [])
                    if not all(tag in memory_tags for tag in tag_filter):
                        continue
                
                # Calculate relevance score (simple count of matching words)
                score = sum(1 for w in words if w in tokenize_text(str(memory.get("memory", ""))))
                
                results.append({
                    "category": category,
                    "memory": memory,
                    "score": score
                })
    
    # Sort by relevance score (highest first)
    results.sort(key=lambda x: x["score"], reverse=True)
    return results

def get_related_memories(memories, index, tags, limit=5):
    """
    Get memories related to specific tags.
    
    Args:
        memories: Dictionary of memory categories
        index: Memory index
        tags: List of tags to find related memories
        limit: Maximum number of results
        
    Returns:
        list: Related memory entries
    """
    results = []
    seen = set()
    
    for tag in tags:
        # Check exact tag matches
        for category, memory in index["tag_index"].get(tag, []):
            memory_id = (category, memory.get("timestamp", 0))
            if memory_id not in seen:
                seen.add(memory_id)
                results.append({
                    "category": category,
                    "memory": memory,
                    "match_type": "exact_tag"
                })
        
        # Check hierarchical tag matches
        if ":" in tag:
            base_tag = tag.split(":")[0]
            for category, memory in index["hierarchy_index"].get(base_tag, []):
                memory_id = (category, memory.get("timestamp", 0))
                if memory_id not in seen:
                    seen.add(memory_id)
                    results.append({
                        "category": category,
                        "memory": memory,
                        "match_type": "related_tag"
                    })
    
    # Sort by recency (newest first)
    results.sort(key=lambda x: x["memory"].get("timestamp", 0), reverse=True)
    return results[:limit]
