#!/usr/bin/env python3
# brain/language_module.py - Language processing module for the AI Companion System

import logging
import time
from typing import Dict, List, Any, Optional

from brain.module_base import BrainModule
from memory.memory_manager import MemoryManager

logger = logging.getLogger(__name__)

class LanguageModule(BrainModule):
    """
    Language processing module for the AI Companion System.
    
    Responsible for:
    1. Natural language understanding
    2. Text generation
    3. Dialog management
    4. Linguistic pattern recognition
    """
    
    def __init__(self, config: Dict[str, Any], memory_manager: MemoryManager):
        """
        Initialize the LanguageModule.
        
        Args:
            config: Module-specific configuration
            memory_manager: Memory manager instance
        """
        super().__init__(config, memory_manager)
        
        self.model_type = config.get('model_type', 'transformer')
        self.context_window = config.get('context_window', 2048)
        
        # Language processing state
        self.conversation_history = []
        self.language_patterns = {}
        
        logger.info(f"Language module initialized with model_type={self.model_type}")
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process input data using language understanding.
        
        Args:
            input_data: Input data to process
            
        Returns:
            Processed language understanding
        """
        start_time = time.time()
        
        try:
            content = input_data.get('content', '')
            if not content:
                self._record_processing_metrics(start_time, False)
                return {'error': 'No content provided'}
            
            # Update conversation history
            self.conversation_history.append({
                'role': 'user',
                'content': content,
                'timestamp': time.time()
            })
            
            # Trim conversation history to fit context window
            self._trim_conversation_history()
            
            # Get relevant memories for context
            context_memories = self.memory_manager.get_memory_context(content, context_size=3)
            
            # Parse intent from input
            intent = self._parse_intent(content)
            
            # Analyze sentiment
            sentiment = self._analyze_sentiment(content)
            
            # Identify entities
            entities = self._identify_entities(content)
            
            # Store the language analysis
            analysis_id = self.memory_manager.store_memory({
                'type': 'language_analysis',
                'content': content,
                'intent': intent,
                'sentiment': sentiment,
                'entities': entities
            }, tags=['language', 'analysis'])
            
            # Create understanding result
            understanding = {
                'original_input': content,
                'intent': intent,
                'sentiment': sentiment,
                'entities': entities,
                'context_memories': [mem.get('id') for mem in context_memories],
                'analysis_id': analysis_id
            }
            
            self._record_processing_metrics(start_time)
            return understanding
            
        except Exception as e:
            logger.error(f"Error in language processing: {e}")
            self._record_processing_metrics(start_time, False)
            return {'error': f"Language processing failed: {str(e)}"}
    
    def generate_response(self, understanding: Dict[str, Any], tone: str = 'neutral') -> str:
        """
        Generate a natural language response based on understanding.
        
        Args:
            understanding: Language understanding to respond to
            tone: Tone of the response (neutral, formal, friendly, etc.)
            
        Returns:
            Generated response text
        """
        # This is a simplified implementation
        # A real system would use a language model
        
        intent = understanding.get('intent', 'unknown')
        
        # Simple response templates
        responses = {
            'greeting': [
                "Hello! How can I help you today?",
                "Hi there! What can I do for you?",
                "Greetings! How may I assist you?"
            ],
            'question': [
                "I'll do my best to answer that.",
                "Let me think about that question.",
                "That's an interesting question."
            ],
            'request': [
                "I'll help you with that request.",
                "Let me see what I can do about that.",
                "I'll take care of that for you."
            ],
            'statement': [
                "I understand.",
                "Thanks for letting me know.",
                "I've noted that information."
            ],
            'unknown': [
                "I'm not sure I understand. Could you rephrase that?",
                "I'm still learning. Could you clarify what you mean?",
                "I didn't quite catch that. Can you explain differently?"
            ]
        }
        
        # Get response options for the intent
        options = responses.get(intent, responses['unknown'])
        
        # Simple selection based on the current time (just for variety)
        selection = int(time.time()) % len(options)
        response = options[selection]
        
        # Add to conversation history
        self.conversation_history.append({
            'role': 'assistant',
            'content': response,
            'timestamp': time.time()
        })
        
        return response
    
    def _parse_intent(self, text: str) -> str:
        """
        Parse the intent from text.
        
        Args:
            text: Text to parse
            
        Returns:
            Identified intent
        """
        # This is a simplified implementation
        # A real system would use NLU models
        
        text_lower = text.lower()
        
        # Simple rule-based intent detection
        if text_lower.startswith(('hi', 'hello', 'hey', 'greetings')):
            return 'greeting'
        elif '?' in text:
            return 'question'
        elif text_lower.startswith(('can you', 'could you', 'please', 'would you')):
            return 'request'
        else:
            return 'statement'
    
    def _analyze_sentiment(self, text: str) -> Dict[str, float]:
        """
        Analyze sentiment in text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Sentiment analysis results
        """
        # This is a simplified implementation
        # A real system would use sentiment analysis models
        
        text_lower = text.lower()
        
        # Simple keyword-based sentiment
        positive_words = ['good', 'great', 'excellent', 'amazing', 'happy', 'love', 'like']
        negative_words = ['bad', 'terrible', 'awful', 'hate', 'dislike', 'sad', 'angry']
        
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        total_words = len(text_lower.split())
        
        positive_score = positive_count / max(total_words, 1)
        negative_score = negative_count / max(total_words, 1)
        neutral_score = 1.0 - (positive_score + negative_score)
        
        return {
            'positive': positive_score,
            'negative': negative_score,
            'neutral': neutral_score
        }
    
    def _identify_entities(self, text: str) -> List[Dict[str, Any]]:
        """
        Identify entities in text.
        
        Args:
            text: Text to analyze
            
        Returns:
            List of identified entities
        """
        # This is a simplified implementation
        # A real system would use NER models
        
        entities = []
        
        # Simple pattern matching for dates
        import re
        date_pattern = r'\d{1,2}/\d{1,2}/\d{2,4}'
        dates = re.findall(date_pattern, text)
        for date in dates:
            entities.append({
                'type': 'date',
                'value': date,
                'confidence': 0.9
            })
        
        # Simple pattern matching for times
        time_pattern = r'\d{1,2}:\d{2}'
        times = re.findall(time_pattern, text)
        for time_val in times:
            entities.append({
                'type': 'time',
                'value': time_val,
                'confidence': 0.9
            })
        
        return entities
    
    def _trim_conversation_history(self) -> None:
        """
        Trim conversation history to fit within context window.
        """
        # Calculate current token count (very rough approximation)
        total_tokens = sum(len(entry.get('content', '').split()) for entry in self.conversation_history)
        
        # If we're over the limit, remove oldest entries
        while total_tokens > self.context_window and len(self.conversation_history) > 1:
            removed = self.conversation_history.pop(0)
            # Approximate token count
            total_tokens -= len(removed.get('content', '').split())
