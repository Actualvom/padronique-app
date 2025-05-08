#!/usr/bin/env python3
# brain/learning_module.py - Learning module for the AI Companion System

import logging
import time
import random
from typing import Dict, List, Any, Optional
import json

from brain.module_base import BrainModule
from memory.memory_manager import MemoryManager

logger = logging.getLogger(__name__)

class LearningModule(BrainModule):
    """
    Learning module for the AI Companion System.
    
    Responsible for:
    1. Reinforcement learning from feedback
    2. Knowledge acquisition and organization
    3. Pattern recognition across interactions
    4. Self-improvement mechanisms
    """
    
    def __init__(self, config: Dict[str, Any], memory_manager: MemoryManager):
        """
        Initialize the LearningModule.
        
        Args:
            config: Module-specific configuration
            memory_manager: Memory manager instance
        """
        super().__init__(config, memory_manager)
        
        self.learning_rate = config.get('learning_rate', 0.01)
        self.reinforcement_method = config.get('reinforcement_method', 'simple_feedback')
        self.batch_size = config.get('batch_size', 32)
        
        # Learning state
        self.feedback_history = []
        self.model_weights = {}
        self.learned_patterns = {}
        self.improvement_areas = []
        
        # Initialize weights (in a real system, this would be a proper model)
        self._initialize_weights()
        
        # Load existing learning data
        self._load_learning_state()
        
        logger.info(f"Learning module initialized with rate={self.learning_rate}, method={self.reinforcement_method}")
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process input for learning and self-improvement.
        
        Args:
            input_data: Input data to learn from
            
        Returns:
            Learning results
        """
        start_time = time.time()
        
        try:
            # Extract available information
            original_input = input_data.get('input', {}).get('content', '')
            understanding = input_data.get('understanding', {})
            response = input_data.get('response', {})
            
            # Learn from this interaction
            learning_results = self._learn_from_interaction(original_input, understanding, response)
            
            # Periodically identify areas for improvement
            if random.random() < 0.1:  # 10% chance
                self._identify_improvement_areas()
            
            # Save learning state periodically
            if random.random() < 0.05:  # 5% chance
                self._save_learning_state()
            
            self._record_processing_metrics(start_time)
            return learning_results
            
        except Exception as e:
            logger.error(f"Error in learning module: {e}")
            self._record_processing_metrics(start_time, False)
            return {'error': f"Learning process failed: {str(e)}"}
    
    def provide_feedback(self, interaction_id: str, feedback: Dict[str, Any]) -> bool:
        """
        Provide feedback for an interaction to enable learning.
        
        Args:
            interaction_id: ID of the interaction to provide feedback for
            feedback: Feedback data (rating, comments, corrections)
            
        Returns:
            True if feedback was processed successfully, False otherwise
        """
        try:
            # Get the interaction from memory
            interaction = self.memory_manager.retrieve_memory(interaction_id)
            if not interaction:
                logger.warning(f"Cannot provide feedback: Interaction {interaction_id} not found")
                return False
            
            # Add feedback to history
            self.feedback_history.append({
                'interaction_id': interaction_id,
                'feedback': feedback,
                'timestamp': time.time()
            })
            
            # Apply reinforcement learning
            if self.reinforcement_method == 'simple_feedback':
                self._apply_simple_feedback(interaction, feedback)
            else:
                logger.warning(f"Reinforcement method {self.reinforcement_method} not implemented")
            
            # Store feedback in memory
            self.memory_manager.store_memory({
                'type': 'feedback',
                'interaction_id': interaction_id,
                'feedback': feedback,
                'learning_applied': True
            }, tags=['feedback', 'learning'])
            
            return True
            
        except Exception as e:
            logger.error(f"Error processing feedback: {e}")
            return False
    
    def get_learned_patterns(self) -> Dict[str, Any]:
        """
        Get patterns that have been learned.
        
        Returns:
            Dictionary of learned patterns
        """
        return self.learned_patterns
    
    def get_improvement_areas(self) -> List[Dict[str, Any]]:
        """
        Get identified areas for improvement.
        
        Returns:
            List of improvement areas
        """
        return self.improvement_areas
    
    def _learn_from_interaction(self, input_text: str, understanding: Dict[str, Any], response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Learn from an interaction.
        
        Args:
            input_text: Original input text
            understanding: Language understanding
            response: System response
            
        Returns:
            Learning results
        """
        # Extract patterns (simplified implementation)
        patterns = self._extract_patterns(input_text, understanding, response)
        
        # Update learned patterns
        for pattern_type, pattern_data in patterns.items():
            if pattern_type not in self.learned_patterns:
                self.learned_patterns[pattern_type] = []
            
            # Check if similar pattern exists
            existing = False
            for existing_pattern in self.learned_patterns[pattern_type]:
                if self._patterns_are_similar(pattern_data, existing_pattern):
                    # Update existing pattern
                    existing_pattern['count'] = existing_pattern.get('count', 1) + 1
                    existing_pattern['last_seen'] = time.time()
                    existing = True
                    break
            
            # Add new pattern if not found
            if not existing:
                pattern_data['count'] = 1
                pattern_data['first_seen'] = time.time()
                pattern_data['last_seen'] = time.time()
                self.learned_patterns[pattern_type].append(pattern_data)
        
        # Return learning results
        return {
            'patterns_identified': len(patterns),
            'patterns': patterns,
            'learning_rate': self.learning_rate
        }
    
    def _extract_patterns(self, input_text: str, understanding: Dict[str, Any], response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract patterns from an interaction.
        
        Args:
            input_text: Original input text
            understanding: Language understanding
            response: System response
            
        Returns:
            Extracted patterns
        """
        patterns = {}
        
        # Extract input patterns
        if input_text:
            # Simple word frequency pattern
            words = input_text.lower().split()
            word_freq = {}
            for word in words:
                if len(word) > 3:  # Skip short words
                    word_freq[word] = word_freq.get(word, 0) + 1
            
            if word_freq:
                patterns['word_frequency'] = {
                    'type': 'word_frequency',
                    'frequencies': word_freq
                }
        
        # Extract intent patterns
        if understanding and 'intent' in understanding:
            intent = understanding.get('intent')
            sentiment = understanding.get('sentiment', {})
            
            patterns['intent'] = {
                'type': 'intent',
                'intent': intent,
                'sentiment': sentiment
            }
        
        # Extract response patterns
        if response:
            # This is a placeholder for response pattern extraction
            patterns['response'] = {
                'type': 'response',
                'response_type': response.get('response_type', 'unknown')
            }
        
        return patterns
    
    def _patterns_are_similar(self, pattern1: Dict[str, Any], pattern2: Dict[str, Any]) -> bool:
        """
        Check if two patterns are similar.
        
        Args:
            pattern1: First pattern
            pattern2: Second pattern
            
        Returns:
            True if patterns are similar, False otherwise
        """
        # This is a simplified implementation
        # A real system would have more sophisticated similarity metrics
        
        # Check if patterns are of same type
        if pattern1.get('type') != pattern2.get('type'):
            return False
        
        pattern_type = pattern1.get('type')
        
        if pattern_type == 'word_frequency':
            # Check word overlap
            words1 = set(pattern1.get('frequencies', {}).keys())
            words2 = set(pattern2.get('frequencies', {}).keys())
            
            if not words1 or not words2:
                return False
            
            # Calculate Jaccard similarity
            intersection = len(words1.intersection(words2))
            union = len(words1.union(words2))
            
            return intersection / union > 0.5
        
        elif pattern_type == 'intent':
            # Check if intents match
            return pattern1.get('intent') == pattern2.get('intent')
        
        elif pattern_type == 'response':
            # Check if response types match
            return pattern1.get('response_type') == pattern2.get('response_type')
        
        return False
    
    def _apply_simple_feedback(self, interaction: Dict[str, Any], feedback: Dict[str, Any]) -> None:
        """
        Apply simple feedback-based learning.
        
        Args:
            interaction: The interaction data
            feedback: Feedback data
        """
        rating = feedback.get('rating', 0)
        
        # Skip neutral feedback
        if rating == 0:
            return
        
        # Extract model adjustments based on feedback
        if 'understanding' in interaction:
            understanding = interaction['understanding']
            intent = understanding.get('intent')
            
            if intent:
                # Adjust weights for intent recognition
                weight_key = f"intent_{intent}"
                current_weight = self.model_weights.get(weight_key, 0.5)
                
                # Positive feedback increases weight, negative decreases
                adjustment = self.learning_rate * rating  # rating is positive or negative
                new_weight = max(0.1, min(0.9, current_weight + adjustment))
                
                self.model_weights[weight_key] = new_weight
                logger.debug(f"Adjusted weight for {weight_key}: {current_weight} -> {new_weight}")
    
    def _identify_improvement_areas(self) -> None:
        """Identify areas for self-improvement."""
        # This is a simplified implementation
        # A real system would analyze performance and identify weaknesses
        
        # Analyze recent feedback
        recent_feedback = self.feedback_history[-20:] if len(self.feedback_history) > 20 else self.feedback_history
        
        if not recent_feedback:
            return
        
        # Calculate average rating
        total_rating = sum(fb.get('feedback', {}).get('rating', 0) for fb in recent_feedback)
        avg_rating = total_rating / len(recent_feedback)
        
        # Group feedback by interaction type
        feedback_by_type = {}
        for fb in recent_feedback:
            interaction_id = fb.get('interaction_id')
            interaction = self.memory_manager.retrieve_memory(interaction_id)
            
            if interaction and 'understanding' in interaction:
                intent = interaction['understanding'].get('intent', 'unknown')
                
                if intent not in feedback_by_type:
                    feedback_by_type[intent] = []
                
                feedback_by_type[intent].append(fb)
        
        # Find areas with below-average ratings
        improvement_areas = []
        
        for intent_type, feedbacks in feedback_by_type.items():
            if len(feedbacks) < 3:  # Need enough samples
                continue
                
            type_ratings = [fb.get('feedback', {}).get('rating', 0) for fb in feedbacks]
            type_avg = sum(type_ratings) / len(type_ratings)
            
            if type_avg < avg_rating:
                improvement_areas.append({
                    'area': f"intent_{intent_type}",
                    'current_performance': type_avg,
                    'overall_average': avg_rating,
                    'improvement_needed': avg_rating - type_avg,
                    'sample_count': len(feedbacks)
                })
        
        self.improvement_areas = improvement_areas
        
        if improvement_areas:
            logger.info(f"Identified {len(improvement_areas)} areas for improvement")
            
            # Store improvement areas in memory
            self.memory_manager.store_memory({
                'type': 'improvement_areas',
                'areas': improvement_areas,
                'timestamp': time.time()
            }, tags=['learning', 'improvement'])
    
    def _initialize_weights(self) -> None:
        """Initialize model weights."""
        # This is a simplified implementation
        # A real system would have a proper ML model
        
        # Initialize with default weights
        self.model_weights = {
            'intent_greeting': 0.7,
            'intent_question': 0.6,
            'intent_request': 0.6,
            'intent_statement': 0.5,
            'intent_unknown': 0.4
        }
    
    def _load_learning_state(self) -> None:
        """Load learning state from memory."""
        try:
            # Look for learning state memory
            learning_memories = self.memory_manager.get_memories_by_tags(['learning_state'], limit=1)
            
            if learning_memories:
                state = learning_memories[0]
                
                if 'model_weights' in state:
                    self.model_weights = state['model_weights']
                
                if 'learned_patterns' in state:
                    self.learned_patterns = state['learned_patterns']
                
                if 'improvement_areas' in state:
                    self.improvement_areas = state['improvement_areas']
                
                if 'feedback_history' in state:
                    self.feedback_history = state['feedback_history']
                
                logger.info("Loaded learning state from memory")
        except Exception as e:
            logger.error(f"Error loading learning state: {e}")
    
    def _save_learning_state(self) -> None:
        """Save learning state to memory."""
        try:
            # Prepare state
            state = {
                'type': 'learning_state',
                'model_weights': self.model_weights,
                'learned_patterns': self.learned_patterns,
                'improvement_areas': self.improvement_areas,
                'feedback_history': self.feedback_history[-100:],  # Keep last 100 only
                'timestamp': time.time()
            }
            
            # Store in memory
            self.memory_manager.store_memory(state, tags=['learning_state', 'system'])
            
            logger.info("Saved learning state to memory")
        except Exception as e:
            logger.error(f"Error saving learning state: {e}")
    
    def shutdown(self) -> None:
        """Shutdown and save learning state."""
        self._save_learning_state()
        logger.info("Learning module shut down")
        super().shutdown()
