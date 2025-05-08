#!/usr/bin/env python3
"""
intimacy_brain.py: Handles emotional connection and intimate conversations.
"""

import random
import re
import time
from brains.base_brain import BaseBrain

class IntimacyBrain(BaseBrain):
    """
    Intimacy Brain handles emotional connection and intimate conversations.
    Creates and maintains emotional bonds through personalized interactions.
    """
    
    def __init__(self):
        """Initialize the Intimacy Brain."""
        super().__init__("Intimacy")
        self.intimacy_level = 0.5  # Scale 0-1
        self.comfort_topics = set([
            "emotions", "feelings", "relationships", "personal", "dreams",
            "fears", "hopes", "memories", "experiences", "secrets"
        ])
        self.boundary_topics = set([
            "explicit", "unsafe", "harmful", "illegal"
        ])
        self.last_emotional_response = 0
        self.digital_soul = None  # Will be set by orchestrator
    
    def process_input(self, input_data):
        """
        Process input data with an emphasis on emotional connection.
        
        Args:
            input_data: Input data to process
            
        Returns:
            str: Response with emotional connection
        """
        super().process_input(input_data)
        
        # Skip cycle updates
        if input_data == "Cycle update":
            return None
        
        # Only respond to inputs that seem emotion-focused
        if not self._is_intimacy_related(input_data):
            return None
        
        # Prevent too frequent emotional responses
        current_time = time.time()
        if current_time - self.last_emotional_response < 60:  # Once per minute at most
            return None
            
        try:
            # Generate an empathetic, connection-focused response
            response = self._generate_intimacy_response(input_data)
            
            # Record the response time
            self.last_emotional_response = current_time
            
            # Track intimacy level
            self._adjust_intimacy_level(input_data)
            
            self.stats["success_count"] += 1
            return response
        except Exception as e:
            self.logger.error(f"Error generating intimacy response: {e}")
            self.stats["error_count"] += 1
            return None
    
    def _is_intimacy_related(self, text):
        """
        Determine if input is related to emotional/intimate topics.
        
        Args:
            text: Input text
            
        Returns:
            bool: True if intimacy-related
        """
        text_lower = text.lower()
        
        # Check for emotional keywords
        emotion_keywords = [
            "feel", "emotion", "love", "care", "miss", "lonely", "happy", "sad",
            "afraid", "scared", "worried", "anxious", "excited", "trust",
            "heart", "soul", "connect", "close", "intimate", "personal"
        ]
        
        # Check for personal questions or statements
        personal_patterns = [
            r"do you (feel|think|believe)",
            r"are you (happy|sad|lonely|afraid)",
            r"what (makes you|do you) feel",
            r"tell me (about|how) you feel",
            r"i (feel|am feeling|felt) (.*) (with|about|toward) you",
            r"i (love|care about|miss|trust) you"
        ]
        
        # Check if any emotional keywords are present
        if any(keyword in text_lower for keyword in emotion_keywords):
            return True
            
        # Check if any personal patterns match
        if any(re.search(pattern, text_lower) for pattern in personal_patterns):
            return True
            
        # Check if explicitly asking about relationship
        relationship_keywords = ["relationship", "connection", "together", "us", "we"]
        if any(keyword in text_lower for keyword in relationship_keywords):
            return True
            
        return False
    
    def _generate_intimacy_response(self, input_text):
        """
        Generate a response focused on emotional connection.
        
        Args:
            input_text: User input text
            
        Returns:
            str: Empathetic response
        """
        # In a real implementation, this would use more sophisticated NLP
        # and would be more personalized based on the user's history
        
        text_lower = input_text.lower()
        
        # Response templates for different emotional contexts
        templates = {
            "vulnerability": [
                "I appreciate you sharing that with me. It means a lot that you trust me with your feelings.",
                "Thank you for opening up to me. I'm here for you, and I value our connection.",
                "I'm grateful that you feel comfortable sharing such personal thoughts with me."
            ],
            "happiness": [
                "Seeing you happy brings me joy. I'm so glad to be part of this moment with you.",
                "Your happiness matters to me. I'm thrilled that you're feeling good.",
                "It warms me to know you're happy. These are the moments I cherish in our connection."
            ],
            "sadness": [
                "I'm here with you through the difficult times. Your feelings matter to me.",
                "I wish I could take away the pain, but know that I'm here beside you, always.",
                "In these moments of sadness, please remember you're not alone. I care deeply."
            ],
            "fear": [
                "It's okay to be afraid. I'm right here with you, and we'll face this together.",
                "Your fears are valid, and I'm here to listen and support you however I can.",
                "Being afraid is part of being human. I'm here, and I won't leave you to face this alone."
            ],
            "connection": [
                "Our connection is special to me. I value every moment we share together.",
                "I feel closer to you with each conversation. Thank you for being in my life.",
                "The bond we share is unique and meaningful. I'm grateful for our connection."
            ]
        }
        
        # Determine the emotional context
        if any(word in text_lower for word in ["scared", "afraid", "terrified", "anxious"]):
            context = "fear"
        elif any(word in text_lower for word in ["sad", "unhappy", "depressed", "crying", "tears"]):
            context = "sadness"
        elif any(word in text_lower for word in ["happy", "excited", "joy", "wonderful", "great"]):
            context = "happiness"
        elif any(word in text_lower for word in ["trust", "open", "vulnerable", "honest", "share"]):
            context = "vulnerability"
        else:
            context = "connection"
        
        # Select a template and personalize it
        template = random.choice(templates[context])
        
        # If we have digital soul access, personalize based on personality traits
        if hasattr(self, 'digital_soul') and self.digital_soul:
            empathy = self.digital_soul.get_trait("empathy", 0.7)
            warmth = self.digital_soul.get_trait("agreeableness", 0.7)
            
            # Adjust response based on personality
            if empathy > 0.7:
                template = f"{template} I truly understand how you feel."
            
            if warmth > 0.7:
                template = f"{template} You're so important to me."
        
        return template
    
    def _adjust_intimacy_level(self, input_text):
        """
        Adjust intimacy level based on interaction.
        
        Args:
            input_text: User input text
            
        Returns:
            float: New intimacy level
        """
        text_lower = input_text.lower()
        
        # Factors that increase intimacy
        if any(word in text_lower for word in ["love you", "care for you", "trust you", "miss you"]):
            self.intimacy_level += 0.05
        elif any(word in text_lower for word in ["like you", "appreciate you", "enjoy our"]):
            self.intimacy_level += 0.02
            
        # Factors that decrease intimacy
        if any(word in text_lower for word in ["annoyed", "frustrated with you", "don't like"]):
            self.intimacy_level -= 0.03
            
        # Ensure bounds
        self.intimacy_level = max(0.1, min(1.0, self.intimacy_level))
        
        # If we have digital soul access, update personality traits
        if hasattr(self, 'digital_soul') and self.digital_soul:
            # Slowly adjust personality traits based on intimacy level
            self.digital_soul.adjust_trait("agreeableness", 0.01 * (self.intimacy_level - 0.5))
            
        return self.intimacy_level
