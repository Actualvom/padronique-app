#!/usr/bin/env python3
"""
hunter.py: Searches for and retrieves relevant information.
"""

import re
from brains.base_brain import BaseBrain

class Hunter(BaseBrain):
    """
    Hunter brain responsible for searching and retrieving information.
    Acts as an information retrieval system for the Padronique system.
    """
    
    def __init__(self):
        """Initialize the Hunter brain."""
        super().__init__("Hunter")
        self.digital_soul = None  # Will be set by orchestrator
        self.search_patterns = [
            r"(?:find|search for|look for|hunt for|get) (.*)",
            r"(?:what|where|when|who|how) (?:is|are|was|were) (.*)",
            r"(?:tell me about) (.*)",
            r"(?:information on|info on|data about) (.*)",
            r"(?:do you know|can you tell me) (.*)"
        ]
    
    def process_input(self, input_data):
        """
        Process input data by searching for relevant information.
        
        Args:
            input_data: Input data to process
            
        Returns:
            str: Retrieved information or None
        """
        super().process_input(input_data)
        
        # Skip cycle updates
        if input_data == "Cycle update":
            return None
        
        # Check if this is a search or information retrieval request
        query = self._extract_search_query(input_data)
        if not query:
            return None
        
        try:
            # Search for information in memory first
            if hasattr(self, 'digital_soul') and self.digital_soul:
                memory_results = self.digital_soul.search_memories(query)
                
                if memory_results:
                    # Format memory results
                    response = self._format_memory_results(query, memory_results)
                    self.stats["success_count"] += 1
                    return response
            
            # If no memories found, check for information we might know
            # This would integrate with an LLM or knowledge database in a real implementation
            known_info = self._check_known_information(query)
            if known_info:
                self.stats["success_count"] += 1
                return known_info
            
            # If still no results, return a "no information" response
            self.stats["success_count"] += 1
            return f"I don't have specific information about {query}. Would you like me to remember this as an area of interest for you?"
            
        except Exception as e:
            self.logger.error(f"Error in Hunter search: {e}")
            self.stats["error_count"] += 1
            return None
    
    def _extract_search_query(self, text):
        """
        Extract a search query from the input text.
        
        Args:
            text: Input text
            
        Returns:
            str: Extracted query or None
        """
        text_lower = text.lower()
        
        # Check if this is a search request
        for pattern in self.search_patterns:
            match = re.search(pattern, text_lower)
            if match:
                query = match.group(1).strip()
                # Clean up query
                query = re.sub(r"^(about|on|regarding) ", "", query)
                query = query.strip("?,.!")
                return query
        
        return None
    
    def _format_memory_results(self, query, results):
        """
        Format memory search results into a response.
        
        Args:
            query: Search query
            results: Memory search results
            
        Returns:
            str: Formatted response
        """
        if not results:
            return f"I don't have any memories related to {query}."
        
        # Limit to top 3 results
        top_results = results[:3]
        
        response = f"Here's what I remember about {query}:\n\n"
        
        for idx, result in enumerate(top_results):
            memory = result["memory"]
            category = result["category"]
            
            # Format memory content based on type
            if isinstance(memory, dict) and "content" in memory:
                content = memory["content"]
            elif isinstance(memory, str):
                content = memory
            else:
                content = str(memory)
            
            # Truncate long memories
            if len(content) > 100:
                content = content[:97] + "..."
            
            response += f"{idx+1}. {content} [{category}]\n"
        
        return response
    
    def _check_known_information(self, query):
        """
        Check for information we might know about the query.
        This is a placeholder for integration with an LLM or knowledge database.
        
        Args:
            query: Search query
            
        Returns:
            str: Known information or None
        """
        # This would integrate with an LLM or knowledge database in a real implementation
        # For now, return None to indicate no information found
        return None
