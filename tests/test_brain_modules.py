#!/usr/bin/env python3
# tests/test_brain_modules.py - Tests for brain modules

import unittest
import time
from unittest.mock import MagicMock, patch
from typing import Dict, Any, List

from brain.module_base import BrainModule
from brain.language_module import LanguageModule
from brain.reasoning_module import ReasoningModule
from brain.learning_module import LearningModule
from brain.perception_module import PerceptionModule
from memory.memory_manager import MemoryManager

class TestBrainModule(unittest.TestCase):
    """Tests for the base BrainModule class."""
    
    def test_abstract_methods(self):
        """Test that abstract methods are enforced."""
        # Should not be able to instantiate BrainModule directly
        with self.assertRaises(TypeError):
            module = BrainModule({}, MagicMock())
    
    def test_basic_functionality(self):
        """Test basic functionality of the BrainModule."""
        # Create a concrete subclass for testing
        class TestModule(BrainModule):
            def process(self, input_data):
                return {"processed": input_data}
        
        # Create mock memory manager
        memory_manager = MagicMock()
        
        # Create module instance
        module = TestModule({"test_config": True}, memory_manager)
        
        # Test activation/deactivation
        self.assertTrue(module.is_active())
        module.deactivate()
        self.assertFalse(module.is_active())
        module.activate()
        self.assertTrue(module.is_active())
        
        # Test config update
        module.update_config({"new_setting": "value"})
        self.assertEqual(module.config["new_setting"], "value")
        self.assertTrue(module.config["test_config"])
        
        # Test stats
        stats = module.get_stats()
        self.assertTrue(stats["active"])
        self.assertEqual(stats["processing_count"], 0)
        self.assertEqual(stats["error_count"], 0)
    
    def test_recording_metrics(self):
        """Test recording of processing metrics."""
        # Create a concrete subclass for testing
        class TestModule(BrainModule):
            def process(self, input_data):
                start_time = time.time()
                try:
                    result = {"processed": input_data}
                    self._record_processing_metrics(start_time)
                    return result
                except Exception as e:
                    self._record_processing_metrics(start_time, False)
                    raise e
        
        # Create module instance
        module = TestModule({}, MagicMock())
        
        # Process some input
        result = module.process({"test": "data"})
        
        # Check metrics were recorded
        self.assertEqual(module.processing_count, 1)
        self.assertEqual(module.error_count, 0)
        self.assertGreater(module.last_used, 0)
        self.assertGreater(module.total_processing_time, 0)
        
        # Test error handling
        class ErrorModule(BrainModule):
            def process(self, input_data):
                start_time = time.time()
                try:
                    raise ValueError("Test error")
                except Exception as e:
                    self._record_processing_metrics(start_time, False)
                    return {"error": str(e)}
        
        error_module = ErrorModule({}, MagicMock())
        error_module.process({"test": "data"})
        
        # Check error was recorded
        self.assertEqual(error_module.processing_count, 1)
        self.assertEqual(error_module.error_count, 1)


class TestLanguageModule(unittest.TestCase):
    """Tests for the LanguageModule class."""
    
    def setUp(self):
        """Set up test environment."""
        self.memory_manager = MagicMock()
        
        # Mock store_memory to return a predictable ID
        self.memory_manager.store_memory.return_value = "test-memory-id"
        
        # Mock get_memory_context to return empty list
        self.memory_manager.get_memory_context.return_value = []
        
        self.config = {
            "model_type": "transformer",
            "context_window": 1024
        }
        
        self.language_module = LanguageModule(self.config, self.memory_manager)
    
    def test_process_empty_input(self):
        """Test processing empty input."""
        result = self.language_module.process({"content": ""})
        
        self.assertIn("error", result)
        self.assertEqual(self.language_module.error_count, 1)
    
    def test_process_valid_input(self):
        """Test processing valid input."""
        result = self.language_module.process({"content": "Hello, how are you?"})
        
        # Check that processing succeeded
        self.assertNotIn("error", result)
        self.assertEqual(self.language_module.processing_count, 1)
        
        # Check result structure
        self.assertIn("original_input", result)
        self.assertIn("intent", result)
        self.assertIn("sentiment", result)
        self.assertIn("entities", result)
        self.assertIn("analysis_id", result)
        
        # Check that memory was stored
        self.memory_manager.store_memory.assert_called_once()
    
    def test_intent_parsing(self):
        """Test parsing intents from text."""
        # Test greeting intent
        result = self.language_module.process({"content": "Hello there!"})
        self.assertEqual(result["intent"], "greeting")
        
        # Test question intent
        result = self.language_module.process({"content": "What time is it?"})
        self.assertEqual(result["intent"], "question")
        
        # Test request intent
        result = self.language_module.process({"content": "Please help me with this."})
        self.assertEqual(result["intent"], "request")
        
        # Test statement intent
        result = self.language_module.process({"content": "The sky is blue."})
        self.assertEqual(result["intent"], "statement")
    
    def test_sentiment_analysis(self):
        """Test sentiment analysis."""
        # Test positive sentiment
        result = self.language_module.process({"content": "I love this, it's really good!"})
        sentiment = result["sentiment"]
        self.assertGreater(sentiment["positive"], sentiment["negative"])
        
        # Test negative sentiment
        result = self.language_module.process({"content": "I hate this, it's terrible."})
        sentiment = result["sentiment"]
        self.assertGreater(sentiment["negative"], sentiment["positive"])
        
        # Test neutral sentiment
        result = self.language_module.process({"content": "The car is red."})
        sentiment = result["sentiment"]
        self.assertGreater(sentiment["neutral"], 0.5)
    
    def test_entity_identification(self):
        """Test entity identification."""
        # Test date entity
        result = self.language_module.process({"content": "Let's meet on 12/25/2023."})
        entities = result["entities"]
        self.assertEqual(len(entities), 1)
        self.assertEqual(entities[0]["type"], "date")
        self.assertEqual(entities[0]["value"], "12/25/2023")
        
        # Test time entity
        result = self.language_module.process({"content": "The meeting is at 3:30."})
        entities = result["entities"]
        self.assertEqual(len(entities), 1)
        self.assertEqual(entities[0]["type"], "time")
        self.assertEqual(entities[0]["value"], "3:30")
    
    def test_generate_response(self):
        """Test response generation."""
        # Test response to greeting
        understanding = {"intent": "greeting"}
        response = self.language_module.generate_response(understanding)
        self.assertIsInstance(response, str)
        self.assertGreater(len(response), 0)
        
        # Test response to question
        understanding = {"intent": "question"}
        response = self.language_module.generate_response(understanding)
        self.assertIsInstance(response, str)
        self.assertGreater(len(response), 0)
        
        # Test conversation history update
        self.assertGreater(len(self.language_module.conversation_history), 0)
        last_entry = self.language_module.conversation_history[-1]
        self.assertEqual(last_entry["role"], "assistant")
        self.assertEqual(last_entry["content"], response)
    
    def test_conversation_history_trimming(self):
        """Test conversation history trimming."""
        # Add enough entries to exceed context window
        large_text = "a " * 1000  # More than context_window tokens
        
        for i in range(5):
            self.language_module.conversation_history.append({
                "role": "user" if i % 2 == 0 else "assistant",
                "content": large_text,
                "timestamp": time.time()
            })
        
        # Process input to trigger trimming
        self.language_module.process({"content": "Hello"})
        
        # Context window should have been trimmed
        total_tokens = sum(len(entry.get("content", "").split()) 
                           for entry in self.language_module.conversation_history)
        self.assertLessEqual(total_tokens, self.language_module.context_window)


class TestReasoningModule(unittest.TestCase):
    """Tests for the ReasoningModule class."""
    
    def setUp(self):
        """Set up test environment."""
        self.memory_manager = MagicMock()
        
        # Mock store_memory to return a predictable ID
        self.memory_manager.store_memory.return_value = "reasoning-memory-id"
        
        self.config = {
            "reasoning_depth": 3,
            "logical_frameworks": ["deductive", "inductive", "abductive"]
        }
        
        self.reasoning_module = ReasoningModule(self.config, self.memory_manager)
    
    def test_process_question(self):
        """Test processing a question input."""
        input_data = {
            "intent": "question",
            "original_input": "What is the capital of France?",
            "entities": [],
            "context_memories": []
        }
        
        result = self.reasoning_module.process(input_data)
        
        # Check that processing succeeded
        self.assertNotIn("error", result)
        self.assertEqual(self.reasoning_module.processing_count, 1)
        
        # Check result structure
        self.assertIn("reasoning", result)
        self.assertIn("response", result)
        self.assertIn("original_input", result)
        self.assertIn("memory_id", result)
        
        # Check reasoning content
        reasoning = result["reasoning"]
        self.assertIn("question_type", reasoning)
        self.assertIn("steps", reasoning)
        self.assertIn("answer", reasoning)
        self.assertIn("confidence", reasoning)
        
        # Check that memory was stored
        self.memory_manager.store_memory.assert_called_once()
    
    def test_process_request(self):
        """Test processing a request input."""
        input_data = {
            "intent": "request",
            "original_input": "Please show me the latest data.",
            "entities": [],
            "context_memories": []
        }
        
        result = self.reasoning_module.process(input_data)
        
        # Check that processing succeeded
        self.assertNotIn("error", result)
        
        # Check result structure
        self.assertIn("reasoning", result)
        self.assertIn("response", result)
        
        # Check reasoning content
        reasoning = result["reasoning"]
        self.assertIn("request_type", reasoning)
        self.assertIn("steps", reasoning)
        self.assertIn("feasibility", reasoning)
        self.assertIn("response_approach", reasoning)
        self.assertIn("confidence", reasoning)
    
    def test_process_general(self):
        """Test processing a general input."""
        input_data = {
            "intent": "statement",
            "original_input": "The sky is blue.",
            "entities": [],
            "sentiment": {"neutral": 0.8, "positive": 0.1, "negative": 0.1}
        }
        
        result = self.reasoning_module.process(input_data)
        
        # Check that processing succeeded
        self.assertNotIn("error", result)
        
        # Check result structure
        self.assertIn("reasoning", result)
        self.assertIn("response", result)
        
        # Check reasoning content
        reasoning = result["reasoning"]
        self.assertIn("input_class", reasoning)
        self.assertIn("steps", reasoning)
        self.assertIn("key_concepts", reasoning)
        self.assertIn("response_type", reasoning)
        self.assertIn("confidence", reasoning)
    
    def test_error_handling(self):
        """Test error handling in processing."""
        # Create a mock memory manager that raises an exception
        memory_manager = MagicMock()
        memory_manager.store_memory.side_effect = Exception("Test exception")
        
        # Create module with the mock
        module = ReasoningModule(self.config, memory_manager)
        
        # Process input
        input_data = {
            "intent": "question",
            "original_input": "What is the meaning of life?",
            "entities": []
        }
        
        result = module.process(input_data)
        
        # Check that error was handled
        self.assertIn("error", result)
        self.assertIn("response", result)
        self.assertEqual(module.error_count, 1)
    
    def test_confidence_calculation(self):
        """Test confidence calculation."""
        # Create reasoning steps
        steps = [
            {"step": 1, "description": "Step 1", "result": "Result 1"},
            {"step": 2, "description": "Step 2", "result": "Result 2"},
            {"step": 3, "description": "Step 3", "result": "Result 3"}
        ]
        
        # Calculate confidence
        confidence = self.reasoning_module._calculate_confidence(steps)
        
        # Should be between 0 and 1
        self.assertGreater(confidence, 0)
        self.assertLessEqual(confidence, 0.95)  # Capped at 0.95
        
        # More steps should increase confidence
        fewer_steps = steps[:1]
        lower_confidence = self.reasoning_module._calculate_confidence(fewer_steps)
        self.assertLess(lower_confidence, confidence)


class TestLearningModule(unittest.TestCase):
    """Tests for the LearningModule class."""
    
    def setUp(self):
        """Set up test environment."""
        self.memory_manager = MagicMock()
        
        # Mock store_memory to return a predictable ID
        self.memory_manager.store_memory.return_value = "learning-memory-id"
        
        self.config = {
            "learning_rate": 0.01,
            "reinforcement_method": "simple_feedback",
            "batch_size": 32
        }
        
        self.learning_module = LearningModule(self.config, self.memory_manager)
    
    def test_process_input(self):
        """Test processing input for learning."""
        input_data = {
            "input": {"content": "Test input"},
            "understanding": {"intent": "statement"},
            "response": {"content": "Test response"}
        }
        
        result = self.learning_module.process(input_data)
        
        # Check that processing succeeded
        self.assertNotIn("error", result)
        self.assertEqual(self.learning_module.processing_count, 1)
        
        # Check result structure
        self.assertIn("patterns_identified", result)
        self.assertIn("patterns", result)
        self.assertIn("learning_rate", result)
    
    def test_provide_feedback(self):
        """Test providing feedback for learning."""
        # Mock retrieve_memory to return a test interaction
        interaction = {
            "understanding": {"intent": "statement"},
            "response": {"content": "Test response"}
        }
        self.memory_manager.retrieve_memory.return_value = interaction
        
        # Provide feedback
        feedback = {
            "rating": 1,  # Positive feedback
            "comments": "Good response"
        }
        
        result = self.learning_module.provide_feedback("test-interaction-id", feedback)
        
        # Check that feedback was processed
        self.assertTrue(result)
        self.assertEqual(len(self.learning_module.feedback_history), 1)
        
        # Check that memory was stored
        self.memory_manager.store_memory.assert_called_with(
            {
                'type': 'feedback',
                'interaction_id': 'test-interaction-id',
                'feedback': feedback,
                'learning_applied': True
            },
            tags=['feedback', 'learning']
        )
    
    def test_extract_patterns(self):
        """Test pattern extraction from interactions."""
        input_text = "This is a test input with pattern."
        understanding = {"intent": "statement", "sentiment": {"neutral": 0.8}}
        response = {"response_type": "acknowledgment"}
        
        patterns = self.learning_module._extract_patterns(input_text, understanding, response)
        
        # Check that patterns were extracted
        self.assertIn("word_frequency", patterns)
        self.assertIn("intent", patterns)
        self.assertIn("response", patterns)
        
        # Check word frequency pattern
        word_freq = patterns["word_frequency"]["frequencies"]
        self.assertIn("test", word_freq)
        self.assertIn("input", word_freq)
        self.assertIn("pattern", word_freq)
        
        # Check intent pattern
        self.assertEqual(patterns["intent"]["intent"], "statement")
        self.assertEqual(patterns["intent"]["sentiment"], {"neutral": 0.8})
        
        # Check response pattern
        self.assertEqual(patterns["response"]["response_type"], "acknowledgment")
    
    def test_patterns_similarity(self):
        """Test pattern similarity comparison."""
        # Word frequency patterns
        pattern1 = {
            "type": "word_frequency",
            "frequencies": {"test": 1, "pattern": 2, "similar": 1}
        }
        pattern2 = {
            "type": "word_frequency",
            "frequencies": {"test": 2, "pattern": 1, "match": 1}
        }
        pattern3 = {
            "type": "word_frequency",
            "frequencies": {"completely": 1, "different": 1, "words": 1}
        }
        
        # Check similarity
        self.assertTrue(self.learning_module._patterns_are_similar(pattern1, pattern2))
        self.assertFalse(self.learning_module._patterns_are_similar(pattern1, pattern3))
        
        # Intent patterns
        intent1 = {"type": "intent", "intent": "question"}
        intent2 = {"type": "intent", "intent": "question"}
        intent3 = {"type": "intent", "intent": "statement"}
        
        # Check similarity
        self.assertTrue(self.learning_module._patterns_are_similar(intent1, intent2))
        self.assertFalse(self.learning_module._patterns_are_similar(intent1, intent3))
        
        # Different types should never be similar
        self.assertFalse(self.learning_module._patterns_are_similar(pattern1, intent1))
    
    def test_apply_simple_feedback(self):
        """Test applying simple feedback."""
        # Create interaction
        interaction = {
            "understanding": {"intent": "question"}
        }
        
        # Create positive feedback
        positive_feedback = {"rating": 1}
        
        # Record initial weight
        intent_key = "intent_question"
        initial_weight = self.learning_module.model_weights.get(intent_key, 0.5)
        
        # Apply feedback
        self.learning_module._apply_simple_feedback(interaction, positive_feedback)
        
        # Check that weight was increased
        new_weight = self.learning_module.model_weights[intent_key]
        self.assertGreater(new_weight, initial_weight)
        
        # Apply negative feedback
        negative_feedback = {"rating": -1}
        self.learning_module._apply_simple_feedback(interaction, negative_feedback)
        
        # Check that weight was decreased
        final_weight = self.learning_module.model_weights[intent_key]
        self.assertLess(final_weight, new_weight)
    
    def test_identify_improvement_areas(self):
        """Test identifying areas for improvement."""
        # Add feedback entries
        self.learning_module.feedback_history = [
            {
                "interaction_id": f"id-{i}",
                "feedback": {"rating": 1 if i % 3 == 0 else -1},
                "timestamp": time.time()
            }
            for i in range(20)
        ]
        
        # Mock memory retrieval to simulate different interaction types
        def mock_retrieve_memory(id):
            if "id-0" in id or "id-3" in id or "id-6" in id:
                return {"understanding": {"intent": "question"}}
            elif "id-1" in id or "id-4" in id or "id-7" in id:
                return {"understanding": {"intent": "statement"}}
            else:
                return {"understanding": {"intent": "request"}}
        
        self.memory_manager.retrieve_memory.side_effect = mock_retrieve_memory
        
        # Identify improvement areas
        self.learning_module._identify_improvement_areas()
        
        # Check that improvement areas were identified
        self.assertGreater(len(self.learning_module.improvement_areas), 0)
        
        # Check that memory was stored
        self.memory_manager.store_memory.assert_called_with(
            {
                'type': 'improvement_areas',
                'areas': self.learning_module.improvement_areas,
                'timestamp': time.time()
            },
            tags=['learning', 'improvement']
        )


class TestPerceptionModule(unittest.TestCase):
    """Tests for the PerceptionModule class."""
    
    def setUp(self):
        """Set up test environment."""
        self.memory_manager = MagicMock()
        
        # Mock store_memory to return a predictable ID
        self.memory_manager.store_memory.return_value = "perception-memory-id"
        
        self.config = {
            "input_channels": ["text", "image"],
            "feature_extraction": "basic"
        }
        
        self.perception_module = PerceptionModule(self.config, self.memory_manager)
    
    def test_process_empty_input(self):
        """Test processing empty input."""
        result = self.perception_module.process({"type": "text", "content": ""})
        
        self.assertIn("error", result)
        self.assertEqual(self.perception_module.error_count, 1)
    
    def test_process_unsupported_type(self):
        """Test processing unsupported input type."""
        result = self.perception_module.process({"type": "audio", "content": "test.mp3"})
        
        self.assertIn("error", result)
        self.assertEqual(self.perception_module.error_count, 1)
    
    def test_process_text(self):
        """Test processing text input."""
        result = self.perception_module.process({"type": "text", "content": "This is a test input."})
        
        # Check that processing succeeded
        self.assertNotIn("error", result)
        self.assertEqual(self.perception_module.processing_count, 1)
        
        # Check result structure
        self.assertIn("content", result)
        self.assertIn("features", result)
        self.assertIn("metadata", result)
        self.assertIn("input_type", result)
        self.assertIn("processed_at", result)
        
        # Check text features
        features = result["features"]
        self.assertIn("word_count", features)
        self.assertIn("char_count", features)
        self.assertIn("avg_word_length", features)
        self.assertIn("sentiment_indicators", features)
    
    def test_process_image(self):
        """Test processing image input."""
        image_data = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAIAAACQd1PeAAAADElEQVQI12P4//8/AAX+Av7czFnnAAAAAElFTkSuQmCC"
        
        result = self.perception_module.process({"type": "image", "content": image_data})
        
        # Check that processing succeeded
        self.assertNotIn("error", result)
        self.assertEqual(self.perception_module.processing_count, 1)
        
        # Check result structure
        self.assertIn("content", result)
        self.assertIn("features", result)
        self.assertIn("metadata", result)
        
        # Check image features
        features = result["features"]
        self.assertIn("image_type", features)
        self.assertEqual(features["image_type"], "data_uri")
    
    def test_is_significant_input(self):
        """Test significance determination for inputs."""
        # Error results are not significant
        error_result = {"error": "Test error", "input_type": "text"}
        self.assertFalse(self.perception_module._is_significant_input(error_result))
        
        # Short text inputs are not significant
        short_text = {
            "input_type": "text",
            "content": "Hi",
            "features": {"word_count": 1}
        }
        self.assertFalse(self.perception_module._is_significant_input(short_text))
        
        # Longer text inputs are significant
        long_text = {
            "input_type": "text",
            "content": "This is a longer input that should be significant.",
            "features": {"word_count": 10}
        }
        self.assertTrue(self.perception_module._is_significant_input(long_text))
        
        # Image inputs are always significant
        image_input = {
            "input_type": "image",
            "content": "data_uri",
            "features": {"image_type": "data_uri"}
        }
        self.assertTrue(self.perception_module._is_significant_input(image_input))
    
    def test_get_stats(self):
        """Test getting module statistics."""
        # Process some inputs to generate stats
        self.perception_module.process({"type": "text", "content": "Text input 1"})
        self.perception_module.process({"type": "text", "content": "Text input 2"})
        self.perception_module.process({"type": "image", "content": "data:image/png;base64,abc"})
        
        # Get stats
        stats = self.perception_module.get_stats()
        
        # Check stats structure
        self.assertIn("active", stats)
        self.assertIn("processing_count", stats)
        self.assertIn("error_count", stats)
        self.assertIn("input_counts", stats)
        self.assertIn("enabled_channels", stats)
        
        # Check input counts
        self.assertEqual(stats["input_counts"]["text"], 2)
        self.assertEqual(stats["input_counts"]["image"], 1)
        self.assertEqual(stats["processing_count"], 3)


if __name__ == "__main__":
    unittest.main()
