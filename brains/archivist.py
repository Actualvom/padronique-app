#!/usr/bin/env python3
"""
archivist.py: Records and categorizes conversations and events.
"""

import time
import json
import logging
from brains.base_brain import BaseBrain

class Archivist(BaseBrain):
    """
    Archivist brain responsible for recording and categorizing memories.
    Acts as the system's historian, ensuring experiences are properly stored.
    """
    
    def __init__(self):
        """Initialize the Archivist brain."""
        super().__init__("Archivist")
        self.conversation_buffer = []
        self.digital_soul = None  # Will be set by orchestrator
    
    def process_input(self, input_data):
        """
        Process input data by analyzing and archiving it.
        
        Args:
            input_data: Input data to process
            
        Returns:
            str: Status message
        """
        super().process_input(input_data)
        
        # Skip archiving for system cycle updates
        if input_data == "Cycle update":
            return None
        
        try:
            # Add to conversation buffer
            self.conversation_buffer.append({
                "role": "user",
                "content": input_data,
                "timestamp": time.time()
            })
            
            # Limit buffer size
            if len(self.conversation_buffer) > 20:
                self.conversation_buffer = self.conversation_buffer[-20:]
            
            # Analyze input for important concepts
            tags = self._analyze_for_tags(input_data)
            
            # If we have access to digital soul, store the memory
            if hasattr(self, 'digital_soul') and self.digital_soul:
                self.digital_soul.add_memory(
                    "interaction", 
                    {"role": "user", "content": input_data},
                    tags=tags
                )
                
                self.logger.info(f"Archived user input with tags: {tags}")
                return f"Input archived with tags: {', '.join(tags)}"
            else:
                self.logger.warning("Digital Soul not available for archiving")
                return "Input received but not archived"
                
        except Exception as e:
            self.logger.error(f"Error in Archivist: {e}")
            self.stats["error_count"] += 1
            return "Failed to archive input"
    
    def record_response(self, response, additional_tags=None):
        """
        Record a system response.
        
        Args:
            response: Response to record
            additional_tags: Optional additional tags
            
        Returns:
            bool: True if successful
        """
        if not response:
            return False
            
        tags = ["system_response"]
        if additional_tags:
            tags.extend(additional_tags)
        
        # Add to conversation buffer
        self.conversation_buffer.append({
            "role": "assistant",
            "content": response,
            "timestamp": time.time()
        })
        
        # If we have access to digital soul, store the memory
        if hasattr(self, 'digital_soul') and self.digital_soul:
            self.digital_soul.add_memory(
                "interaction", 
                {"role": "assistant", "content": response},
                tags=tags
            )
            return True
        else:
            self.logger.warning("Digital Soul not available for recording response")
            return False
    
    def _analyze_for_tags(self, text):
        """
        Analyze text to extract relevant tags.
        
        Args:
            text: Text to analyze
            
        Returns:
            list: Extracted tags
        """
        tags = ["interaction"]
        
        # Simple keyword-based tagging
        # In a real implementation, use NLP for better tagging
        text_lower = text.lower()
        
        # Emotion detection
        emotions = {
            "joy": ["happy", "joy", "excited", "glad", "delighted"],
            "sadness": ["sad", "unhappy", "upset", "depressed", "sorrow"],
            "anger": ["angry", "mad", "furious", "annoyed", "irritated"],
            "fear": ["afraid", "scared", "fearful", "terrified", "anxious"],
            "surprise": ["surprised", "shocked", "amazed", "astonished"],
            "trust": ["trust", "believe", "reliable", "faithful", "confidence"],
            "disgust": ["disgust", "revolting", "gross", "repulsive"],
            "anticipation": ["expect", "anticipate", "look forward"]
        }
        
        for emotion, keywords in emotions.items():
            if any(keyword in text_lower for keyword in keywords):
                tags.append(f"emotion:{emotion}")
        
        # Topic detection
        topics = {
            "health": ["health", "doctor", "sick", "illness", "disease", "medicine"],
            "technology": ["tech", "computer", "software", "hardware", "program", "code"],
            "finance": ["money", "finance", "bank", "invest", "loan", "budget"],
            "relationship": ["love", "friend", "family", "relationship", "date"],
            "work": ["job", "work", "office", "boss", "career", "profession"],
            "education": ["learn", "study", "school", "college", "education", "teach"],
            "entertainment": ["movie", "music", "game", "play", "fun", "hobby"],
            "personal": ["I", "me", "my", "myself"]
        }
        
        for topic, keywords in topics.items():
            if any(keyword in text_lower for keyword in keywords):
                tags.append(f"topic:{topic}")
        
        # Question detection
        if "?" in text or any(q in text_lower for q in ["what", "how", "why", "when", "where", "who"]):
            tags.append("question")
        
        # Command detection
        command_starters = ["please", "could you", "can you", "would you", "tell me", "show me", "find", "search"]
        if any(text_lower.startswith(starter) for starter in command_starters):
            tags.append("command")
        
        return tags
    
    def extract_conversation_summary(self, limit=5):
        """
        Generate a summary of recent conversation.
        
        Args:
            limit: Maximum number of turns to include
            
        Returns:
            str: Conversation summary
        """
        if not self.conversation_buffer:
            return "No conversation recorded"
        
        # Get most recent turns
        recent = self.conversation_buffer[-limit*2:]  # Get pairs of turns
        
        summary = "Recent conversation:\n"
        for entry in recent:
            role = "User" if entry["role"] == "user" else "Padronique"
            summary += f"{role}: {entry['content']}\n"
        
        return summary
