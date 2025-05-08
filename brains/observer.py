#!/usr/bin/env python3
"""
observer.py: Analyzes input for patterns, sentiment, and intent.
"""

import re
from brains.base_brain import BaseBrain

class Observer(BaseBrain):
    """
    Observer brain responsible for analyzing input data.
    Identifies patterns, sentiment, and user intent from interactions.
    """
    
    def __init__(self):
        """Initialize the Observer brain."""
        super().__init__("Observer")
        self.digital_soul = None  # Will be set by orchestrator
        self.sentiment_words = {
            "positive": [
                "good", "great", "excellent", "awesome", "amazing", "love", "happy",
                "joy", "wonderful", "fantastic", "pleased", "delighted", "thank"
            ],
            "negative": [
                "bad", "terrible", "awful", "horrible", "hate", "sad", "angry",
                "upset", "disappointed", "frustrating", "annoyed", "sorry"
            ]
        }
    
    def process_input(self, input_data):
        """
        Process input data by analyzing patterns and sentiment.
        
        Args:
            input_data: Input data to process
            
        Returns:
            dict: Analysis results or None
        """
        super().process_input(input_data)
        
        # Skip cycle updates
        if input_data == "Cycle update":
            return None
        
        try:
            # Analyze the input
            analysis = {
                "intent": self._identify_intent(input_data),
                "sentiment": self._analyze_sentiment(input_data),
                "patterns": self._identify_patterns(input_data),
                "entities": self._extract_entities(input_data)
            }
            
            # Store analysis in memory if digital soul is available
            if hasattr(self, 'digital_soul') and self.digital_soul:
                self.digital_soul.add_memory(
                    "interaction", 
                    {
                        "input": input_data,
                        "analysis": analysis
                    },
                    tags=["analysis", f"intent:{analysis['intent']}", f"sentiment:{analysis['sentiment']}"]
                )
            
            self.stats["success_count"] += 1
            
            # Observer doesn't directly respond to user, it just analyzes
            return None
            
        except Exception as e:
            self.logger.error(f"Error in Observer analysis: {e}")
            self.stats["error_count"] += 1
            return None
    
    def _identify_intent(self, text):
        """
        Identify the likely intent of the user input.
        
        Args:
            text: Input text
            
        Returns:
            str: Identified intent
        """
        text_lower = text.lower()
        
        # Check for questions
        if "?" in text or text_lower.startswith(("what", "when", "where", "who", "why", "how", "is", "are", "can", "could", "would")):
            return "question"
        
        # Check for commands/requests
        if text_lower.startswith(("please", "can you", "could you", "would you", "i want you to", "i need you to")):
            return "request"
        
        # Check for greetings
        if any(word in text_lower for word in ["hello", "hi", "hey", "greetings", "good morning", "good afternoon", "good evening"]):
            return "greeting"
        
        # Check for farewells
        if any(word in text_lower for word in ["goodbye", "bye", "farewell", "see you", "talk to you later"]):
            return "farewell"
        
        # Check for gratitude
        if "thank" in text_lower:
            return "gratitude"
        
        # Check for apologies
        if any(word in text_lower for word in ["sorry", "apologize", "apology"]):
            return "apology"
        
        # Check for information sharing
        if text_lower.startswith(("i am", "i'm", "i feel", "i think", "i believe", "i want", "i need")):
            return "sharing"
        
        # Default to statement
        return "statement"
    
    def _analyze_sentiment(self, text):
        """
        Analyze the sentiment of the input text.
        
        Args:
            text: Input text
            
        Returns:
            str: Sentiment category (positive, negative, neutral)
        """
        text_lower = text.lower()
        
        # Count positive and negative words
        positive_count = sum(1 for word in self.sentiment_words["positive"] if word in text_lower)
        negative_count = sum(1 for word in self.sentiment_words["negative"] if word in text_lower)
        
        # Determine sentiment based on counts
        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        else:
            return "neutral"
    
    def _identify_patterns(self, text):
        """
        Identify recurring patterns in the input.
        
        Args:
            text: Input text
            
        Returns:
            list: Identified patterns
        """
        patterns = []
        text_lower = text.lower()
        
        # Check for personal preferences
        preference_match = re.search(r"i (like|love|prefer|enjoy|hate|dislike) (.*)", text_lower)
        if preference_match:
            patterns.append(f"preference:{preference_match.group(1)}:{preference_match.group(2).strip()}")
        
        # Check for time references
        if any(word in text_lower for word in ["yesterday", "today", "tomorrow", "last week", "next week", "morning", "afternoon", "evening", "night"]):
            patterns.append("time_reference")
        
        # Check for location references
        if any(word in text_lower for word in ["here", "there", "home", "work", "school", "office"]):
            patterns.append("location_reference")
        
        # Check for conditional statements
        if "if" in text_lower and any(word in text_lower for word in ["then", "would", "could", "might", "will"]):
            patterns.append("conditional")
        
        return patterns
    
    def _extract_entities(self, text):
        """
        Extract named entities from the input.
        This is a simple placeholder implementation.
        In a real system, this would use NER from an NLP library.
        
        Args:
            text: Input text
            
        Returns:
            dict: Extracted entities by type
        """
        entities = {
            "person": [],
            "location": [],
            "datetime": [],
            "organization": []
        }
        
        # Simple regex patterns for dates
        date_patterns = [
            r"\d{1,2}/\d{1,2}/\d{2,4}",  # MM/DD/YYYY
            r"\d{1,2}-\d{1,2}-\d{2,4}",  # MM-DD-YYYY
            r"(January|February|March|April|May|June|July|August|September|October|November|December) \d{1,2}(st|nd|rd|th)?, \d{4}"  # Month Day, Year
        ]
        
        for pattern in date_patterns:
            matches = re.findall(pattern, text)
            if matches:
                entities["datetime"].extend(matches)
        
        return entities
