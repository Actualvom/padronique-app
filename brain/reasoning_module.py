#!/usr/bin/env python3
# brain/reasoning_module.py - Reasoning module for the AI Companion System

import logging
import time
from typing import Dict, List, Any, Optional

from brain.module_base import BrainModule
from memory.memory_manager import MemoryManager

logger = logging.getLogger(__name__)

class ReasoningModule(BrainModule):
    """
    Reasoning module for the AI Companion System.
    
    Responsible for:
    1. Logical reasoning
    2. Decision making
    3. Problem solving
    4. Inference generation
    """
    
    def __init__(self, config: Dict[str, Any], memory_manager: MemoryManager):
        """
        Initialize the ReasoningModule.
        
        Args:
            config: Module-specific configuration
            memory_manager: Memory manager instance
        """
        super().__init__(config, memory_manager)
        
        self.reasoning_depth = config.get('reasoning_depth', 3)
        self.logical_frameworks = config.get('logical_frameworks', ['deductive'])
        
        logger.info(f"Reasoning module initialized with depth={self.reasoning_depth}")
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process input data using reasoning capabilities.
        
        Args:
            input_data: Input data to process (typically from language module)
            
        Returns:
            Reasoning output with response
        """
        start_time = time.time()
        
        try:
            # Extract information from input
            intent = input_data.get('intent', 'unknown')
            original_input = input_data.get('original_input', '')
            
            # Apply reasoning based on intent
            reasoning_result = self._apply_reasoning(input_data)
            
            # Generate response based on reasoning
            response = self._generate_response(reasoning_result)
            
            # Create result
            result = {
                'reasoning': reasoning_result,
                'response': response,
                'original_input': original_input
            }
            
            # Save reasoning to memory
            memory_id = self.memory_manager.store_memory({
                'type': 'reasoning',
                'input': input_data,
                'reasoning': reasoning_result,
                'response': response
            }, tags=['reasoning', intent])
            
            result['memory_id'] = memory_id
            
            self._record_processing_metrics(start_time)
            return result
            
        except Exception as e:
            logger.error(f"Error in reasoning module: {e}")
            self._record_processing_metrics(start_time, False)
            return {
                'error': f"Reasoning failed: {str(e)}",
                'response': "I'm having difficulty processing that right now. Could you try again?"
            }
    
    def _apply_reasoning(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply reasoning to input data.
        
        Args:
            input_data: Input data to reason about
            
        Returns:
            Reasoning results
        """
        intent = input_data.get('intent', 'unknown')
        
        if intent == 'question':
            return self._answer_question(input_data)
        elif intent == 'request':
            return self._evaluate_request(input_data)
        else:
            return self._general_reasoning(input_data)
    
    def _answer_question(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply reasoning to answer a question.
        
        Args:
            input_data: Question input data
            
        Returns:
            Reasoning for the answer
        """
        question = input_data.get('original_input', '')
        entities = input_data.get('entities', [])
        
        # Extract context memories if available
        context_memory_ids = input_data.get('context_memories', [])
        context_memories = []
        
        for memory_id in context_memory_ids:
            memory = self.memory_manager.retrieve_memory(memory_id)
            if memory:
                context_memories.append(memory)
        
        # Apply multi-step reasoning
        reasoning_steps = []
        
        # Step 1: Identify question type
        question_type = self._identify_question_type(question)
        reasoning_steps.append({
            'step': 1,
            'description': 'Identify question type',
            'result': question_type
        })
        
        # Step 2: Search for relevant information
        relevant_info = self._extract_relevant_information(question, context_memories)
        reasoning_steps.append({
            'step': 2,
            'description': 'Search for relevant information',
            'result': relevant_info
        })
        
        # Step 3: Formulate answer
        answer = self._formulate_answer(question_type, relevant_info)
        reasoning_steps.append({
            'step': 3,
            'description': 'Formulate answer',
            'result': answer
        })
        
        return {
            'question_type': question_type,
            'steps': reasoning_steps,
            'answer': answer,
            'confidence': self._calculate_confidence(reasoning_steps)
        }
    
    def _evaluate_request(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate a request using reasoning.
        
        Args:
            input_data: Request input data
            
        Returns:
            Reasoning for the request evaluation
        """
        request = input_data.get('original_input', '')
        
        # Apply reasoning steps
        reasoning_steps = []
        
        # Step 1: Determine request type
        request_type = self._determine_request_type(request)
        reasoning_steps.append({
            'step': 1,
            'description': 'Determine request type',
            'result': request_type
        })
        
        # Step 2: Evaluate feasibility
        feasibility = self._evaluate_feasibility(request_type, request)
        reasoning_steps.append({
            'step': 2,
            'description': 'Evaluate feasibility',
            'result': feasibility
        })
        
        # Step 3: Determine response
        response_approach = self._determine_response_approach(request_type, feasibility)
        reasoning_steps.append({
            'step': 3,
            'description': 'Determine response approach',
            'result': response_approach
        })
        
        return {
            'request_type': request_type,
            'steps': reasoning_steps,
            'feasibility': feasibility,
            'response_approach': response_approach,
            'confidence': self._calculate_confidence(reasoning_steps)
        }
    
    def _general_reasoning(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply general reasoning to input.
        
        Args:
            input_data: Input data to reason about
            
        Returns:
            Reasoning results
        """
        # Apply simple reasoning
        reasoning_steps = []
        
        # Step 1: Classify input
        input_class = self._classify_input(input_data)
        reasoning_steps.append({
            'step': 1,
            'description': 'Classify input',
            'result': input_class
        })
        
        # Step 2: Identify key concepts
        key_concepts = self._identify_key_concepts(input_data)
        reasoning_steps.append({
            'step': 2,
            'description': 'Identify key concepts',
            'result': key_concepts
        })
        
        # Step 3: Determine appropriate response type
        response_type = self._determine_response_type(input_class, key_concepts)
        reasoning_steps.append({
            'step': 3,
            'description': 'Determine response type',
            'result': response_type
        })
        
        return {
            'input_class': input_class,
            'steps': reasoning_steps,
            'key_concepts': key_concepts,
            'response_type': response_type,
            'confidence': self._calculate_confidence(reasoning_steps)
        }
    
    def _generate_response(self, reasoning_result: Dict[str, Any]) -> str:
        """
        Generate a response based on reasoning results.
        
        Args:
            reasoning_result: Results from reasoning process
            
        Returns:
            Generated response
        """
        # This is a simplified implementation
        # In a real system, this would generate natural language responses
        # based on the reasoning results
        
        if 'answer' in reasoning_result:
            return reasoning_result['answer']
        
        if 'response_approach' in reasoning_result:
            approach = reasoning_result['response_approach']
            feasibility = reasoning_result.get('feasibility', {}).get('can_fulfill', False)
            
            if feasibility:
                return f"I can help with that. {approach}"
            else:
                return f"I'm not able to fulfill that request. {approach}"
        
        if 'response_type' in reasoning_result:
            response_type = reasoning_result['response_type']
            
            if response_type == 'acknowledgment':
                return "I understand. Thank you for sharing that information."
            elif response_type == 'clarification':
                return "I'm not sure I fully understand. Could you provide more details?"
            elif response_type == 'information':
                return "That's interesting information. Let me process that."
            else:
                return "I've processed your input and am ready to continue our conversation."
        
        # Fallback
        return "I've thought about that and have a response for you."
    
    # Helper methods for question answering
    
    def _identify_question_type(self, question: str) -> str:
        """Identify the type of question."""
        question_lower = question.lower()
        
        if question_lower.startswith(('what', 'which')):
            return 'factual'
        elif question_lower.startswith(('how')):
            return 'procedural'
        elif question_lower.startswith(('why')):
            return 'explanatory'
        elif question_lower.startswith(('when')):
            return 'temporal'
        elif question_lower.startswith(('where')):
            return 'spatial'
        elif question_lower.startswith(('who', 'whom')):
            return 'person'
        elif question_lower.startswith(('can', 'could', 'will', 'would', 'do', 'does', 'is', 'are')):
            return 'yes_no'
        else:
            return 'other'
    
    def _extract_relevant_information(self, question: str, context_memories: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract information relevant to the question."""
        # Simple keyword matching
        keywords = [word for word in question.lower().split() if len(word) > 3]
        
        relevant_memories = []
        for memory in context_memories:
            memory_content = str(memory.get('content', ''))
            if any(keyword in memory_content.lower() for keyword in keywords):
                relevant_memories.append(memory)
        
        return {
            'keywords': keywords,
            'relevant_memories': relevant_memories
        }
    
    def _formulate_answer(self, question_type: str, relevant_info: Dict[str, Any]) -> str:
        """Formulate an answer based on question type and relevant information."""
        memories = relevant_info.get('relevant_memories', [])
        
        if not memories:
            return self._get_default_answer(question_type)
        
        # Very simple answer formulation
        answer_parts = []
        for memory in memories:
            if isinstance(memory.get('content'), str):
                answer_parts.append(memory.get('content'))
        
        if answer_parts:
            return " ".join(answer_parts)
        
        return self._get_default_answer(question_type)
    
    def _get_default_answer(self, question_type: str) -> str:
        """Get a default answer for a question type when no information is available."""
        defaults = {
            'factual': "I don't have specific information about that.",
            'procedural': "I don't have the steps for that procedure.",
            'explanatory': "I can't provide an explanation for that right now.",
            'temporal': "I don't have timing information for that.",
            'spatial': "I don't know the location for that.",
            'person': "I don't have information about that person.",
            'yes_no': "I don't have enough information to answer yes or no.",
            'other': "I don't have a specific answer for that question."
        }
        
        return defaults.get(question_type, "I don't have an answer for that right now.")
    
    # Helper methods for request evaluation
    
    def _determine_request_type(self, request: str) -> str:
        """Determine the type of request."""
        request_lower = request.lower()
        
        if any(x in request_lower for x in ['show', 'display', 'view']):
            return 'information_display'
        elif any(x in request_lower for x in ['find', 'search', 'look for']):
            return 'information_retrieval'
        elif any(x in request_lower for x in ['create', 'make', 'generate']):
            return 'creation'
        elif any(x in request_lower for x in ['change', 'update', 'modify']):
            return 'modification'
        elif any(x in request_lower for x in ['delete', 'remove']):
            return 'deletion'
        elif any(x in request_lower for x in ['help', 'assist']):
            return 'assistance'
        else:
            return 'other'
    
    def _evaluate_feasibility(self, request_type: str, request: str) -> Dict[str, Any]:
        """Evaluate the feasibility of fulfilling a request."""
        # This is a simplified implementation
        # In a real system, this would evaluate capabilities, permissions, etc.
        
        # Simple capability check
        capabilities = {
            'information_display': True,
            'information_retrieval': True,
            'creation': False,
            'modification': False,
            'deletion': False,
            'assistance': True,
            'other': False
        }
        
        can_fulfill = capabilities.get(request_type, False)
        
        return {
            'can_fulfill': can_fulfill,
            'reasons': ["Capability not implemented"] if not can_fulfill else []
        }
    
    def _determine_response_approach(self, request_type: str, feasibility: Dict[str, Any]) -> str:
        """Determine how to respond to a request."""
        if feasibility.get('can_fulfill', False):
            approaches = {
                'information_display': "I'll show you the information you requested.",
                'information_retrieval': "I'll find that information for you.",
                'creation': "I'll create that for you.",
                'modification': "I'll make those changes for you.",
                'deletion': "I'll remove that for you.",
                'assistance': "I'm here to help you with that.",
                'other': "I'll process your request."
            }
            return approaches.get(request_type, "I'll process your request.")
        else:
            approaches = {
                'information_display': "I can't display that information right now.",
                'information_retrieval': "I'm unable to retrieve that information.",
                'creation': "I can't create that for you at the moment.",
                'modification': "I'm not able to make those changes.",
                'deletion': "I can't delete that for you right now.",
                'assistance': "I'm not able to assist with that specific request.",
                'other': "I'm unable to process your request."
            }
            return approaches.get(request_type, "I'm unable to process your request at this time.")
    
    # Helper methods for general reasoning
    
    def _classify_input(self, input_data: Dict[str, Any]) -> str:
        """Classify the input data."""
        intent = input_data.get('intent', 'unknown')
        sentiment = input_data.get('sentiment', {})
        
        if intent == 'statement':
            # Determine if informative or emotional
            neutral = sentiment.get('neutral', 1.0)
            if neutral > 0.7:
                return 'informative'
            else:
                return 'emotional'
        else:
            return intent
    
    def _identify_key_concepts(self, input_data: Dict[str, Any]) -> List[str]:
        """Identify key concepts in the input."""
        original_input = input_data.get('original_input', '')
        entities = input_data.get('entities', [])
        
        # Extract entity values
        entity_values = [entity.get('value') for entity in entities]
        
        # Add important words (very simplified)
        words = original_input.split()
        important_words = [word for word in words if len(word) > 5]
        
        # Combine unique concepts
        all_concepts = entity_values + important_words
        unique_concepts = list(set(all_concepts))
        
        return unique_concepts
    
    def _determine_response_type(self, input_class: str, key_concepts: List[str]) -> str:
        """Determine the appropriate response type."""
        if input_class == 'informative':
            return 'acknowledgment'
        elif input_class == 'emotional':
            return 'empathy'
        elif input_class == 'greeting':
            return 'greeting'
        elif input_class == 'question':
            return 'answer'
        elif input_class == 'request':
            return 'fulfillment'
        elif len(key_concepts) < 2:
            return 'clarification'
        else:
            return 'information'
    
    def _calculate_confidence(self, reasoning_steps: List[Dict[str, Any]]) -> float:
        """Calculate confidence in reasoning results."""
        # This is a simplified implementation
        # A real system would evaluate reasoning quality
        
        # Base confidence
        confidence = 0.7
        
        # Adjust based on number of steps (more steps = more thorough)
        steps_factor = min(len(reasoning_steps) / self.reasoning_depth, 1.0)
        confidence *= (0.5 + 0.5 * steps_factor)
        
        # Cap at 0.95 (never completely certain)
        return min(confidence, 0.95)
