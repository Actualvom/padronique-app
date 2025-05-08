#!/usr/bin/env python3
"""
knowledge_brain.py: Manages knowledge retrieval and information processing.
"""

import time
import re
import os
import json
import logging
import random
from brains.base_brain import BaseBrain

class KnowledgeBrain(BaseBrain):
    """
    Knowledge Brain responsible for information retrieval and knowledge management.
    Acts as the system's knowledge base and learning center.
    """
    
    def __init__(self):
        """Initialize the Knowledge Brain."""
        super().__init__("Knowledge")
        self.digital_soul = None  # Will be set by orchestrator
        self.llm_service = None   # Will be set by orchestrator
        self.knowledge_base = {}
        self.knowledge_categories = [
            "general", "science", "technology", "history", 
            "art", "language", "philosophy", "personal"
        ]
        self.last_update = 0
        self.knowledge_path = "digital_soul/memories/knowledge_base.json"
        self._load_knowledge_base()
    
    def _load_knowledge_base(self):
        """Load the knowledge base from disk."""
        try:
            if os.path.exists(self.knowledge_path):
                with open(self.knowledge_path, 'r') as f:
                    self.knowledge_base = json.load(f)
                    self.logger.info(f"Loaded knowledge base with {len(self.knowledge_base)} entries")
            else:
                # Initialize empty knowledge base
                self.knowledge_base = {category: {} for category in self.knowledge_categories}
                self.logger.info("Initialized empty knowledge base")
                self._save_knowledge_base()
        except Exception as e:
            self.logger.error(f"Error loading knowledge base: {e}")
            self.knowledge_base = {category: {} for category in self.knowledge_categories}
    
    def _save_knowledge_base(self):
        """Save the knowledge base to disk."""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.knowledge_path), exist_ok=True)
            
            with open(self.knowledge_path, 'w') as f:
                json.dump(self.knowledge_base, f, indent=2)
                
            self.logger.debug("Saved knowledge base to disk")
        except Exception as e:
            self.logger.error(f"Error saving knowledge base: {e}")
    
    def process_input(self, input_data):
        """
        Process input data for knowledge-related queries.
        
        Args:
            input_data: Input data to process
            
        Returns:
            str: Response with relevant knowledge or None
        """
        super().process_input(input_data)
        
        # Skip cycle updates
        if input_data == "Cycle update":
            return None
        
        # Skip if not knowledge-related
        if not self._is_knowledge_related(input_data):
            return None
        
        try:
            input_lower = input_data.lower()
            
            # Handle knowledge storage requests
            if any(phrase in input_lower for phrase in ["remember that", "store this", "save this"]):
                return self._handle_knowledge_storage(input_data)
            
            # Handle knowledge retrieval requests
            elif any(phrase in input_lower for phrase in ["what is", "who is", "when is", "where is", "why is", "how does"]):
                return self._handle_knowledge_retrieval(input_data)
            
            # Handle knowledge update requests
            elif any(phrase in input_lower for phrase in ["update", "correct", "revise"]):
                return self._handle_knowledge_update(input_data)
            
            # Handle forgetting requests
            elif any(phrase in input_lower for phrase in ["forget", "remove", "delete"]):
                return self._handle_forget_request(input_data)
            
            # Default response for knowledge-related inputs
            else:
                return self._general_knowledge_response(input_data)
                
        except Exception as e:
            self.logger.error(f"Error processing knowledge input: {e}")
            self.stats["error_count"] += 1
            return None
    
    def _is_knowledge_related(self, text):
        """
        Determine if input is related to knowledge or information.
        
        Args:
            text: Input text
            
        Returns:
            bool: True if knowledge-related
        """
        text_lower = text.lower()
        
        # Knowledge-related keywords
        knowledge_keywords = [
            "know", "learn", "understand", "remember", "forget", "fact",
            "information", "data", "knowledge", "explain", "definition",
            "meaning", "concept", "idea", "theory", "history", "science",
            "technology", "what is", "who is", "when is", "where is",
            "why is", "how does"
        ]
        
        return any(keyword in text_lower for keyword in knowledge_keywords)
    
    def _handle_knowledge_storage(self, text):
        """
        Handle requests to store new knowledge.
        
        Args:
            text: Request text
            
        Returns:
            str: Response
        """
        # Detect the fact/knowledge being stored
        knowledge_match = None
        
        # Try different patterns to extract knowledge
        patterns = [
            r"remember that (.*)",
            r"store this(?:fact|knowledge|information)?: (.*)",
            r"save this(?:fact|knowledge|information)?: (.*)",
            r"remember this: (.*)"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                knowledge_match = match.group(1).strip()
                break
        
        if not knowledge_match:
            return "I'm not sure what knowledge you want me to store. Please try again with a clear statement like 'Remember that X is Y'."
        
        # Determine the category
        category = self._categorize_knowledge(knowledge_match)
        
        # Generate a key for the knowledge
        key = self._generate_knowledge_key(knowledge_match)
        
        # Store the knowledge
        self.knowledge_base[category][key] = {
            "content": knowledge_match,
            "source": "user_input",
            "timestamp": time.time(),
            "confidence": 0.9  # High confidence for user-provided information
        }
        
        # Save the updated knowledge base
        self._save_knowledge_base()
        
        # Add to digital soul memories as well if available
        if hasattr(self, 'digital_soul') and self.digital_soul:
            self.digital_soul.add_memory(
                "core", 
                {"fact": knowledge_match},
                tags=["knowledge", f"category:{category}"]
            )
        
        return f"I've stored this knowledge: '{knowledge_match}' in the {category} category."
    
    def _handle_knowledge_retrieval(self, text):
        """
        Handle requests to retrieve knowledge.
        
        Args:
            text: Request text
            
        Returns:
            str: Response with relevant knowledge
        """
        query = self._extract_query(text)
        
        if not query:
            return "I'm not sure what knowledge you're asking for. Please try asking a more specific question."
        
        # Search in knowledge base first
        kb_results = self._search_knowledge_base(query)
        
        if kb_results:
            return kb_results
        
        # Search in digital soul memories
        if hasattr(self, 'digital_soul') and self.digital_soul:
            memory_results = self.digital_soul.search_memories(query)
            
            if memory_results:
                # Format the first relevant memory
                memory = memory_results[0]["memory"]
                category = memory_results[0]["category"]
                
                # Extract content based on memory format
                if isinstance(memory, dict) and "fact" in memory:
                    return memory["fact"]
                elif isinstance(memory, dict) and "content" in memory:
                    return memory["content"]
                elif isinstance(memory, str):
                    return memory
                else:
                    return f"I found related information in my {category} memories, but I can't formulate a clear answer."
        
        # If we have an LLM service, try to use it for general knowledge
        if hasattr(self, 'llm_service') and self.llm_service:
            try:
                llm_response = self.llm_service.query(
                    f"Provide a concise, factual answer to: {query}",
                    max_tokens=150
                )
                
                if llm_response:
                    # Store this knowledge for future use
                    category = self._categorize_knowledge(query)
                    key = self._generate_knowledge_key(query)
                    
                    self.knowledge_base[category][key] = {
                        "content": llm_response,
                        "query": query,
                        "source": "llm",
                        "timestamp": time.time(),
                        "confidence": 0.7  # Medium confidence for LLM-generated information
                    }
                    
                    self._save_knowledge_base()
                    
                    return llm_response
            except Exception as e:
                self.logger.error(f"Error querying LLM for knowledge: {e}")
        
        return f"I don't have specific knowledge about '{query}'. If you have information about this, you can tell me to remember it."
    
    def _handle_knowledge_update(self, text):
        """
        Handle requests to update existing knowledge.
        
        Args:
            text: Request text
            
        Returns:
            str: Response
        """
        # Try to extract the update pattern
        update_match = re.search(r"update .+? (to|that) (.+)", text, re.IGNORECASE)
        
        if not update_match:
            return "I'm not sure what knowledge you want me to update. Please use a format like 'Update X to Y' or 'Correct X to Y'."
        
        # Extract the new information
        new_info = update_match.group(2).strip()
        
        # Extract what needs to be updated (approximate)
        update_subject = text.lower().split("update")[1].split("to")[0].strip()
        if "that" in update_subject:
            update_subject = update_subject.split("that")[0].strip()
        
        # Search for matching knowledge
        matches = []
        
        for category, entries in self.knowledge_base.items():
            for key, entry in entries.items():
                content = entry["content"].lower()
                if update_subject in content or content in update_subject:
                    matches.append((category, key, entry))
        
        if not matches:
            return f"I couldn't find any existing knowledge about '{update_subject}' to update."
        
        # Update the first matching entry
        category, key, entry = matches[0]
        old_content = entry["content"]
        
        # Update the entry
        self.knowledge_base[category][key]["content"] = new_info
        self.knowledge_base[category][key]["timestamp"] = time.time()
        self.knowledge_base[category][key]["previous_content"] = old_content
        
        # Save the updated knowledge base
        self._save_knowledge_base()
        
        return f"I've updated my knowledge from '{old_content}' to '{new_info}'."
    
    def _handle_forget_request(self, text):
        """
        Handle requests to forget/remove knowledge.
        
        Args:
            text: Request text
            
        Returns:
            str: Response
        """
        # Extract what to forget
        forget_match = re.search(r"forget (?:about |that )?(.*)", text, re.IGNORECASE)
        
        if not forget_match:
            return "I'm not sure what knowledge you want me to forget. Please be more specific."
        
        forget_subject = forget_match.group(1).strip()
        
        # Search for matching knowledge
        matches = []
        
        for category, entries in self.knowledge_base.items():
            keys_to_remove = []
            
            for key, entry in entries.items():
                content = entry["content"].lower()
                if forget_subject.lower() in content:
                    matches.append((category, key, entry["content"]))
                    keys_to_remove.append(key)
            
            # Remove matched entries
            for key in keys_to_remove:
                del self.knowledge_base[category][key]
        
        if not matches:
            return f"I couldn't find any knowledge about '{forget_subject}' to forget."
        
        # Save the updated knowledge base
        self._save_knowledge_base()
        
        if len(matches) == 1:
            category, _, content = matches[0]
            return f"I've forgotten the {category} knowledge: '{content}'."
        else:
            return f"I've forgotten {len(matches)} pieces of knowledge related to '{forget_subject}'."
    
    def _extract_query(self, text):
        """
        Extract a knowledge query from text.
        
        Args:
            text: Input text
            
        Returns:
            str: Extracted query or None
        """
        # Common question patterns
        patterns = [
            r"what is (.*?)(?:\?|$)",
            r"who is (.*?)(?:\?|$)",
            r"when is (.*?)(?:\?|$)",
            r"where is (.*?)(?:\?|$)",
            r"why is (.*?)(?:\?|$)",
            r"how does (.*?)(?:\?|$)",
            r"tell me about (.*?)(?:\?|$)",
            r"explain (.*?)(?:\?|$)"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        # If no pattern matches, use the full text as the query
        if "?" in text:
            return text.strip()
        
        return None
    
    def _search_knowledge_base(self, query):
        """
        Search the knowledge base for information.
        
        Args:
            query: Search query
            
        Returns:
            str: Knowledge response or None if not found
        """
        query_words = set(query.lower().split())
        best_match = None
        best_score = 0
        
        for category, entries in self.knowledge_base.items():
            for key, entry in entries.items():
                content = entry["content"]
                content_words = set(content.lower().split())
                
                # Calculate word overlap score
                common_words = query_words.intersection(content_words)
                if not common_words:
                    continue
                
                # Calculate match score based on word overlap and entry confidence
                confidence = entry.get("confidence", 0.5)
                score = (len(common_words) / max(len(query_words), 1)) * confidence
                
                # If this is a direct query match, boost the score
                if "query" in entry and query.lower() in entry["query"].lower():
                    score += 0.3
                
                if score > best_score:
                    best_score = score
                    best_match = entry
        
        # Return the best match if it's good enough
        if best_score > 0.3 and best_match:
            return best_match["content"]
        
        return None
    
    def _categorize_knowledge(self, text):
        """
        Categorize a piece of knowledge.
        
        Args:
            text: Knowledge text
            
        Returns:
            str: Category name
        """
        text_lower = text.lower()
        
        # Simple keyword-based categorization
        category_keywords = {
            "science": ["science", "biology", "chemistry", "physics", "experiment", "scientific"],
            "technology": ["technology", "computer", "software", "hardware", "internet", "digital", "app", "code"],
            "history": ["history", "historical", "ancient", "past", "century", "year", "period", "era"],
            "art": ["art", "music", "painting", "sculpture", "artist", "creative", "design"],
            "language": ["language", "word", "grammar", "syntax", "speak", "speech", "communicate"],
            "philosophy": ["philosophy", "meaning", "ethics", "moral", "virtue", "belief", "concept"],
            "personal": ["i am", "my", "mine", "myself", "your", "you are", "personality"]
        }
        
        for category, keywords in category_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                return category
        
        # Default to general category
        return "general"
    
    def _generate_knowledge_key(self, text):
        """
        Generate a unique key for a knowledge entry.
        
        Args:
            text: Knowledge text
            
        Returns:
            str: Unique key
        """
        # Use first few words as key basis
        words = text.split()[:5]
        key_base = "_".join(words).lower()
        
        # Remove special characters
        key_base = re.sub(r'[^\w]', '', key_base)
        
        # Add timestamp to ensure uniqueness
        timestamp = int(time.time())
        
        return f"{key_base}_{timestamp}"
    
    def _general_knowledge_response(self, text):
        """
        Generate a general response for knowledge-related inputs.
        
        Args:
            text: Input text
            
        Returns:
            str: Response
        """
        general_responses = [
            "I can help you with knowledge and information. You can ask me questions or tell me to remember facts for future reference.",
            "I'm designed to learn and retain knowledge. What would you like to know or what should I remember for you?",
            "Knowledge is an important part of my functionality. I can answer questions or store information you want me to remember.",
            "I can serve as your external memory. Ask me questions or tell me to remember important information for you.",
            "I'm here to help with information and knowledge. What would you like to know about?"
        ]
        
        return random.choice(general_responses)
    
    def add_knowledge(self, content, category=None, source="system", confidence=0.8):
        """
        Add a new knowledge entry.
        Interface for other brain modules to use.
        
        Args:
            content: Knowledge content
            category: Knowledge category or None for auto-categorization
            source: Knowledge source
            confidence: Confidence level (0-1)
            
        Returns:
            bool: True if successful
        """
        if not category:
            category = self._categorize_knowledge(content)
        
        key = self._generate_knowledge_key(content)
        
        self.knowledge_base[category][key] = {
            "content": content,
            "source": source,
            "timestamp": time.time(),
            "confidence": confidence
        }
        
        self._save_knowledge_base()
        return True
    
    def get_knowledge(self, query):
        """
        Get knowledge based on a query.
        Interface for other brain modules to use.
        
        Args:
            query: Search query
            
        Returns:
            dict: Knowledge entry or None if not found
        """
        query_words = set(query.lower().split())
        best_match = None
        best_score = 0
        
        for category, entries in self.knowledge_base.items():
            for key, entry in entries.items():
                content = entry["content"]
                content_words = set(content.lower().split())
                
                # Calculate word overlap score
                common_words = query_words.intersection(content_words)
                if not common_words:
                    continue
                
                # Calculate match score based on word overlap and entry confidence
                confidence = entry.get("confidence", 0.5)
                score = (len(common_words) / max(len(query_words), 1)) * confidence
                
                if score > best_score:
                    best_score = score
                    best_match = entry
        
        # Return the best match if it's good enough
        if best_score > 0.3 and best_match:
            return best_match
        
        return None
