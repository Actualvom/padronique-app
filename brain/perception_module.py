#!/usr/bin/env python3
# brain/perception_module.py - Perception module for the AI Companion System

import logging
import time
import base64
from typing import Dict, List, Any, Optional

from brain.module_base import BrainModule
from memory.memory_manager import MemoryManager

logger = logging.getLogger(__name__)

class PerceptionModule(BrainModule):
    """
    Perception module for the AI Companion System.
    
    Responsible for:
    1. Processing different input types (text, image, etc.)
    2. Feature extraction from inputs
    3. Initial input normalization and preparation
    4. Input classification
    """
    
    def __init__(self, config: Dict[str, Any], memory_manager: MemoryManager):
        """
        Initialize the PerceptionModule.
        
        Args:
            config: Module-specific configuration
            memory_manager: Memory manager instance
        """
        super().__init__(config, memory_manager)
        
        self.input_channels = config.get('input_channels', ['text'])
        self.feature_extraction = config.get('feature_extraction', 'basic')
        
        # Input processing stats
        self.input_counts = {channel: 0 for channel in self.input_channels}
        
        logger.info(f"Perception module initialized with channels={self.input_channels}")
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process input data through appropriate perception channel.
        
        Args:
            input_data: Input data with type and content
            
        Returns:
            Processed perception data
        """
        start_time = time.time()
        
        try:
            input_type = input_data.get('type', 'text')
            content = input_data.get('content', '')
            
            if not content:
                self._record_processing_metrics(start_time, False)
                return {'error': 'No content provided'}
            
            # Check if we support this input type
            if input_type not in self.input_channels:
                logger.warning(f"Unsupported input type: {input_type}")
                self._record_processing_metrics(start_time, False)
                return {'error': f"Unsupported input type: {input_type}"}
            
            # Process based on type
            if input_type == 'text':
                result = self._process_text(content)
            elif input_type == 'image':
                result = self._process_image(content)
            else:
                # This shouldn't happen due to the check above, but just in case
                self._record_processing_metrics(start_time, False)
                return {'error': f"Input type {input_type} not implemented"}
            
            # Update stats
            self.input_counts[input_type] += 1
            
            # Add metadata
            result['input_type'] = input_type
            result['processed_at'] = time.time()
            
            # Store in memory if significant
            if self._is_significant_input(result):
                memory_id = self.memory_manager.store_memory({
                    'type': 'perception',
                    'input_type': input_type,
                    'features': result.get('features', {}),
                    'metadata': result.get('metadata', {})
                }, tags=['perception', input_type])
                
                result['memory_id'] = memory_id
            
            self._record_processing_metrics(start_time)
            return result
            
        except Exception as e:
            logger.error(f"Error in perception processing: {e}")
            self._record_processing_metrics(start_time, False)
            return {'error': f"Perception processing failed: {str(e)}"}
    
    def _process_text(self, text: str) -> Dict[str, Any]:
        """
        Process text input.
        
        Args:
            text: Text content to process
            
        Returns:
            Processed text features
        """
        # Initial text processing
        
        # Basic text statistics
        word_count = len(text.split())
        char_count = len(text)
        
        # Simple sentiment indicators (very basic)
        positive_words = ['good', 'great', 'excellent', 'happy', 'love', 'like']
        negative_words = ['bad', 'terrible', 'awful', 'sad', 'hate', 'dislike']
        
        words = text.lower().split()
        positive_count = sum(1 for word in words if word in positive_words)
        negative_count = sum(1 for word in words if word in negative_words)
        
        # Extract potential topics (very basic)
        potential_topics = [word for word in words if len(word) > 5]
        
        # Create features dictionary
        features = {
            'word_count': word_count,
            'char_count': char_count,
            'avg_word_length': char_count / max(word_count, 1),
            'sentiment_indicators': {
                'positive_words': positive_count,
                'negative_words': negative_count,
                'net_sentiment': positive_count - negative_count
            }
        }
        
        # Additional processing if using advanced feature extraction
        if self.feature_extraction == 'advanced':
            # This would use more sophisticated NLP techniques
            # For now, just add basic n-grams
            bigrams = []
            for i in range(len(words) - 1):
                bigrams.append(f"{words[i]} {words[i+1]}")
            
            features['bigrams'] = bigrams[:10]  # Top 10 bigrams
        
        return {
            'content': text,
            'features': features,
            'metadata': {
                'length': len(text),
                'potential_topics': potential_topics[:5]  # Top 5 potential topics
            }
        }
    
    def _process_image(self, image_data: str) -> Dict[str, Any]:
        """
        Process image input.
        
        Args:
            image_data: Image content (base64 encoded)
            
        Returns:
            Processed image features
        """
        # This is a placeholder implementation
        # A real system would perform image analysis
        
        try:
            # Check if it's a base64 string
            if not image_data.startswith(('data:image', 'http', '/')):
                try:
                    # Try to decode to check if it's valid base64
                    base64.b64decode(image_data)
                    image_type = "base64"
                except Exception:
                    image_type = "unknown"
            elif image_data.startswith('data:image'):
                image_type = "data_uri"
            elif image_data.startswith(('http://', 'https://')):
                image_type = "url"
            elif image_data.startswith('/'):
                image_type = "path"
            else:
                image_type = "unknown"
            
            # Placeholder for image features
            features = {
                'image_type': image_type,
                'analyzed': False,
                'placeholder': True
            }
            
            return {
                'content': image_type,  # Don't include full image data in result
                'features': features,
                'metadata': {
                    'source_type': image_type
                }
            }
            
        except Exception as e:
            logger.error(f"Error processing image: {e}")
            return {
                'error': f"Image processing failed: {str(e)}",
                'features': {},
                'metadata': {}
            }
    
    def _is_significant_input(self, result: Dict[str, Any]) -> bool:
        """
        Determine if input is significant enough to store in memory.
        
        Args:
            result: Processed input result
            
        Returns:
            True if input is significant, False otherwise
        """
        # This is a simplified implementation
        # A real system would have more sophisticated criteria
        
        # Check for errors
        if 'error' in result:
            return False
        
        input_type = result.get('input_type')
        
        if input_type == 'text':
            # Text is significant if it's not too short and has features
            content = result.get('content', '')
            word_count = len(content.split())
            
            has_features = 'features' in result and result['features']
            
            return word_count >= 3 and has_features
        
        elif input_type == 'image':
            # Images are always considered significant for now
            return True
        
        return False
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get module statistics.
        
        Returns:
            Dictionary with module statistics
        """
        stats = super().get_stats()
        
        # Add perception-specific stats
        stats['input_counts'] = self.input_counts
        stats['enabled_channels'] = self.input_channels
        
        return stats
