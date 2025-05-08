#!/usr/bin/env python3
"""
weaver.py: Integrates and refines outputs from other brain modules.
"""

from brains.base_brain import BaseBrain

class Weaver(BaseBrain):
    """
    Weaver brain responsible for integrating and refining responses.
    Combines outputs from multiple brain modules into a coherent response.
    """
    
    def __init__(self):
        """Initialize the Weaver brain."""
        super().__init__("Weaver")
        self.digital_soul = None  # Will be set by orchestrator
    
    def process_input(self, input_data):
        """
        Process input data by analyzing general context.
        This is mainly used to determine which other brains should respond.
        
        Args:
            input_data: Input data to process
            
        Returns:
            str: Processing status
        """
        super().process_input(input_data)
        
        # Skip cycle updates
        if input_data == "Cycle update":
            return None
        
        # Weaver doesn't generate primary responses
        # It mainly combines responses from other brains
        return None
    
    def weave_responses(self, user_input, responses):
        """
        Combine and refine responses from multiple brain modules.
        
        Args:
            user_input: Original user input
            responses: List of responses from other brain modules
            
        Returns:
            str: Integrated response
        """
        if not responses:
            return "I'm processing that input."
        
        # If only one response, return it directly
        if len(responses) == 1:
            return responses[0]
        
        # Filter out None or empty responses
        valid_responses = [r for r in responses if r]
        if not valid_responses:
            return "I'm processing that input."
        
        # For simplicity in this implementation, we'll choose the best response
        # In a real implementation, this would use NLG to combine responses
        
        # Categorize responses
        emotional_responses = []
        informational_responses = []
        action_responses = []
        
        for response in valid_responses:
            # Classify responses (simple version)
            if any(word in response.lower() for word in ["feel", "emotion", "care", "love", "sorry", "happy", "sad"]):
                emotional_responses.append(response)
            elif any(word in response.lower() for word in ["i'll", "let me", "i can", "i will", "let's"]):
                action_responses.append(response)
            else:
                informational_responses.append(response)
        
        # Get personality bias if available
        emotional_bias = 0.5
        if hasattr(self, 'digital_soul') and self.digital_soul:
            emotional_bias = self.digital_soul.get_trait("empathy", 0.5)
        
        # Form response based on priorities and personality
        final_parts = []
        
        # Add emotional response if available and appropriate
        if emotional_responses and emotional_bias > 0.3:
            final_parts.append(emotional_responses[0])
        
        # Add main informational response if available
        if informational_responses:
            # Choose the longest informational response as it's likely more detailed
            main_info = max(informational_responses, key=len)
            if main_info not in final_parts:
                final_parts.append(main_info)
        
        # Add action response if available
        if action_responses and not any("i'll" in part.lower() for part in final_parts):
            final_parts.append(action_responses[0])
        
        # If we still have no parts, use the first valid response
        if not final_parts:
            final_parts.append(valid_responses[0])
        
        # Join parts with appropriate spacing
        # Make sure not to duplicate very similar responses
        unique_parts = []
        for part in final_parts:
            if not any(self._is_similar(part, existing) for existing in unique_parts):
                unique_parts.append(part)
        
        final_response = " ".join(unique_parts)
        
        self.stats["success_count"] += 1
        return final_response
    
    def _is_similar(self, response1, response2):
        """
        Check if two responses are very similar.
        
        Args:
            response1: First response
            response2: Second response
            
        Returns:
            bool: True if responses are similar
        """
        # Simple similarity check based on shared words
        words1 = set(response1.lower().split())
        words2 = set(response2.lower().split())
        
        # If more than 70% of words are shared, consider similar
        if not words1 or not words2:
            return False
            
        smaller_set = words1 if len(words1) < len(words2) else words2
        intersection = words1.intersection(words2)
        
        similarity = len(intersection) / len(smaller_set)
        return similarity > 0.7
