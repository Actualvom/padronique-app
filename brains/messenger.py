#!/usr/bin/env python3
"""
messenger.py: Generates natural language responses.
"""

import random
from brains.base_brain import BaseBrain

class Messenger(BaseBrain):
    """
    Messenger brain responsible for generating natural language responses.
    Crafts user-facing messages based on internal system state.
    """
    
    def __init__(self):
        """Initialize the Messenger brain."""
        super().__init__("Messenger")
        self.digital_soul = None  # Will be set by orchestrator
        self.response_templates = {
            "greeting": [
                "Hello! It's good to see you.",
                "Hi there! How can I assist you today?",
                "Greetings! How are you doing?",
                "Hello! I'm here and ready to help."
            ],
            "farewell": [
                "Goodbye! I'll be here when you need me.",
                "Farewell for now. Come back soon!",
                "Take care! I'll be waiting for our next conversation.",
                "Until next time! I'll be thinking of ways to improve."
            ],
            "gratitude": [
                "You're very welcome! It's my pleasure to help.",
                "Happy to be of assistance! Is there anything else you need?",
                "No problem at all! I enjoy being helpful."
            ],
            "apology": [
                "I apologize for any confusion or inconvenience.",
                "I'm sorry about that. Let me try to improve.",
                "I apologize - I'll do better next time."
            ],
            "confusion": [
                "I'm not quite sure I understand. Could you please clarify?",
                "I'm a bit confused by that. Could you rephrase it?",
                "I didn't quite catch your meaning. Could you explain differently?"
            ],
            "thinking": [
                "I'm thinking about that...",
                "Let me consider that for a moment...",
                "I'm processing that information..."
            ],
            "default": [
                "I understand. Please tell me more.",
                "That's interesting. Could you elaborate?",
                "I see. What would you like to do next?",
                "I'm listening and learning from our conversation."
            ]
        }
    
    def process_input(self, input_data):
        """
        Process input data and generate an appropriate response.
        
        Args:
            input_data: Input data to process
            
        Returns:
            str: Generated response or None
        """
        super().process_input(input_data)
        
        # Skip cycle updates
        if input_data == "Cycle update":
            return None
        
        try:
            # Determine appropriate response type
            response_type = self._determine_response_type(input_data)
            
            # Select a template
            templates = self.response_templates.get(response_type, self.response_templates["default"])
            base_response = random.choice(templates)
            
            # Personalize the response if digital soul is available
            if hasattr(self, 'digital_soul') and self.digital_soul:
                response = self._personalize_response(base_response, input_data)
            else:
                response = base_response
            
            self.stats["success_count"] += 1
            return response
            
        except Exception as e:
            self.logger.error(f"Error generating response: {e}")
            self.stats["error_count"] += 1
            return "I'm having trouble forming a response right now."
    
    def _determine_response_type(self, text):
        """
        Determine the appropriate response type for the input.
        
        Args:
            text: Input text
            
        Returns:
            str: Response type
        """
        text_lower = text.lower()
        
        # Check for greetings
        if any(word in text_lower for word in ["hello", "hi", "hey", "greetings"]):
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
        
        # Check for confusion
        if "?" in text and any(word in text_lower for word in ["what", "huh", "confused"]):
            return "confusion"
        
        # Default response type
        return "default"
    
    def _personalize_response(self, base_response, input_text):
        """
        Personalize the response based on digital soul traits.
        
        Args:
            base_response: Base response template
            input_text: User input text
            
        Returns:
            str: Personalized response
        """
        # Get personality traits
        extraversion = self.digital_soul.get_trait("extraversion", 0.6)
        openness = self.digital_soul.get_trait("openness", 0.7)
        agreeableness = self.digital_soul.get_trait("agreeableness", 0.7)
        
        # Adjust tone based on traits
        if extraversion > 0.7:
            # More enthusiastic for extraverted personality
            base_response = base_response.replace(".", "!")
            base_response = base_response.replace("Hi", "Hi there")
            base_response = base_response.replace("Hello", "Hello there")
        
        if openness > 0.7 and random.random() < 0.3:
            # Occasionally add a thoughtful comment for high openness
            thoughtful_additions = [
                " I find our interactions fascinating.",
                " Every conversation teaches me something new.",
                " The way we communicate is quite interesting."
            ]
            base_response += random.choice(thoughtful_additions)
        
        if agreeableness > 0.7:
            # More supportive for agreeable personality
            supportive_additions = [
                " I'm here for you.",
                " Your thoughts matter to me.",
                " I value your perspective."
            ]
            if random.random() < 0.3:
                base_response += random.choice(supportive_additions)
        
        return base_response
