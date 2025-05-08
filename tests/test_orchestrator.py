#!/usr/bin/env python3
# tests/test_orchestrator.py - Tests for the core orchestrator

import unittest
import time
import tempfile
import shutil
import os
from unittest.mock import MagicMock, patch
from typing import Dict, Any, List

from core.orchestrator import Orchestrator
from memory.memory_manager import MemoryManager
from core.security import SecurityManager
from brain.module_base import BrainModule

class MockBrainModule(BrainModule):
    """Mock brain module for testing."""
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process input data and return a result."""
        # Record metrics
        start_time = time.time()
        
        # Simple processing - just echo input with additional field
        result = input_data.copy()
        result["processed_by"] = self.__class__.__name__
        
        self._record_processing_metrics(start_time)
        return result

class MockPerceptionModule(MockBrainModule):
    """Mock perception module."""
    pass

class MockLanguageModule(MockBrainModule):
    """Mock language module."""
    pass

class MockReasoningModule(MockBrainModule):
    """Mock reasoning module."""
    pass

class MockLearningModule(MockBrainModule):
    """Mock learning module."""
    pass

class TestOrchestrator(unittest.TestCase):
    """Tests for the Orchestrator class."""
    
    def setUp(self):
        """Set up test environment."""
        # Create temporary directory for memory
        self.temp_dir = tempfile.mkdtemp()
        
        # Basic configuration
        self.config = {
            "system": {
                "name": "TestSystem",
                "version": "1.0.0"
            },
            "memory": {
                "storage_path": self.temp_dir,
                "encryption_enabled": False,
                "max_memories": 100,
                "default_expiry_days": 1
            },
            "security": {
                "encryption_key_rotation_days": 90,
                "require_authentication": False,
                "sensitive_data_tags": ["personal", "financial"]
            },
            "brain": {
                "modules": [
                    {
                        "name": "perception",
                        "enabled": True,
                        "config": {"test_config": True}
                    },
                    {
                        "name": "language",
                        "enabled": True,
                        "config": {"test_config": True}
                    },
                    {
                        "name": "reasoning",
                        "enabled": True,
                        "config": {"test_config": True}
                    },
                    {
                        "name": "learning",
                        "enabled": True,
                        "config": {"test_config": True}
                    },
                    {
                        "name": "disabled_module",
                        "enabled": False,
                        "config": {}
                    }
                ]
            }
        }
        
        # Create orchestrator
        self.orchestrator = Orchestrator(self.config)
    
    def tearDown(self):
        """Clean up after tests."""
        shutil.rmtree(self.temp_dir)
    
    def test_initialization(self):
        """Test basic initialization of the orchestrator."""
        # Check system info
        self.assertEqual(self.orchestrator.system_name, "TestSystem")
        self.assertEqual(self.orchestrator.version, "1.0.0")
        
        # Check memory manager initialization
        self.assertIsInstance(self.orchestrator.memory_manager, MemoryManager)
        
        # Check security manager initialization
        self.assertIsInstance(self.orchestrator.security_manager, SecurityManager)
        
        # Initially no modules should be registered
        self.assertEqual(len(self.orchestrator.modules), 0)
    
    @patch("importlib.import_module")
    def test_initialize_modules(self, mock_import_module):
        """Test module initialization."""
        # Set up mocks for the module classes
        mock_perception = MagicMock(return_value=MockPerceptionModule)
        mock_language = MagicMock(return_value=MockLanguageModule)
        mock_reasoning = MagicMock(return_value=MockReasoningModule)
        mock_learning = MagicMock(return_value=MockLearningModule)
        
        # Configure import_module mock to return our module mocks
        def side_effect(module_path):
            module_mock = MagicMock()
            if module_path == "brain.perception_module":
                module_mock.PerceptionModule = MockPerceptionModule
            elif module_path == "brain.language_module":
                module_mock.LanguageModule = MockLanguageModule
            elif module_path == "brain.reasoning_module":
                module_mock.ReasoningModule = MockReasoningModule
            elif module_path == "brain.learning_module":
                module_mock.LearningModule = MockLearningModule
            return module_mock
        
        mock_import_module.side_effect = side_effect
        
        # Initialize modules
        self.orchestrator.initialize_modules()
        
        # Check that enabled modules were initialized
        self.assertEqual(len(self.orchestrator.modules), 4)
        self.assertIn("perception", self.orchestrator.modules)
        self.assertIn("language", self.orchestrator.modules)
        self.assertIn("reasoning", self.orchestrator.modules)
        self.assertIn("learning", self.orchestrator.modules)
        
        # Check that disabled modules were not initialized
        self.assertNotIn("disabled_module", self.orchestrator.modules)
        
        # Check module types
        self.assertIsInstance(self.orchestrator.modules["perception"], MockPerceptionModule)
        self.assertIsInstance(self.orchestrator.modules["language"], MockLanguageModule)
        self.assertIsInstance(self.orchestrator.modules["reasoning"], MockReasoningModule)
        self.assertIsInstance(self.orchestrator.modules["learning"], MockLearningModule)
    
    def test_register_and_get_module(self):
        """Test registering and retrieving modules."""
        # Create a mock module
        mock_module = MockBrainModule({}, self.orchestrator.memory_manager)
        
        # Register the module
        self.orchestrator.register_module("test_module", mock_module)
        
        # Check it was registered
        self.assertIn("test_module", self.orchestrator.modules)
        
        # Retrieve the module
        retrieved = self.orchestrator.get_module("test_module")
        self.assertEqual(retrieved, mock_module)
        
        # Try retrieving a non-existent module
        self.assertIsNone(self.orchestrator.get_module("nonexistent"))
    
    def test_process_input(self):
        """Test processing input through the orchestrator."""
        # Register mock modules
        self.orchestrator.register_module("perception", MockPerceptionModule({}, self.orchestrator.memory_manager))
        self.orchestrator.register_module("language", MockLanguageModule({}, self.orchestrator.memory_manager))
        self.orchestrator.register_module("reasoning", MockReasoningModule({}, self.orchestrator.memory_manager))
        self.orchestrator.register_module("learning", MockLearningModule({}, self.orchestrator.memory_manager))
        
        # Create test input
        input_data = {
            "type": "text",
            "content": "Hello, this is a test."
        }
        
        # Process input
        result = self.orchestrator.process_input(input_data)
        
        # Check that all modules processed the input
        self.assertIn("processed_by", result)
        self.assertEqual(result["processed_by"], "MockReasoningModule")
        
        # Check that memory was stored
        # We can't easily check this directly, but we can check memory stats
        memory_stats = self.orchestrator.memory_manager.get_stats()
        self.assertGreaterEqual(memory_stats["total_memories"], 1)
    
    def test_error_handling_missing_module(self):
        """Test handling of missing modules."""
        # Register some modules but not perception
        self.orchestrator.register_module("language", MockLanguageModule({}, self.orchestrator.memory_manager))
        self.orchestrator.register_module("reasoning", MockReasoningModule({}, self.orchestrator.memory_manager))
        
        # Create test input
        input_data = {
            "type": "text",
            "content": "Hello, this is a test."
        }
        
        # Process input
        result = self.orchestrator.process_input(input_data)
        
        # Check that error was reported
        self.assertIn("error", result)
        self.assertEqual(result["error"], "Perception module not available")
    
    def test_unauthorized_request(self):
        """Test handling of unauthorized requests."""
        # Configure security to require auth
        self.orchestrator.security_manager.require_auth = True
        
        # Create test input without auth token
        input_data = {
            "type": "text",
            "content": "Hello, this is a test."
        }
        
        # Process input
        result = self.orchestrator.process_input(input_data)
        
        # Check that unauthorized error was reported
        self.assertIn("error", result)
        self.assertEqual(result["error"], "Unauthorized request")
        
        # Reset security config
        self.orchestrator.security_manager.require_auth = False
    
    def test_get_system_status(self):
        """Test getting system status."""
        # Register mock modules
        self.orchestrator.register_module("perception", MockPerceptionModule({}, self.orchestrator.memory_manager))
        self.orchestrator.register_module("language", MockLanguageModule({}, self.orchestrator.memory_manager))
        
        # Get status
        status = self.orchestrator.get_system_status()
        
        # Check status information
        self.assertEqual(status["system_name"], "TestSystem")
        self.assertEqual(status["version"], "1.0.0")
        self.assertIn("uptime", status)
        self.assertIn("modules", status)
        self.assertIn("memory", status)
        
        # Check module status
        self.assertIn("perception", status["modules"])
        self.assertIn("language", status["modules"])
        
        # Check memory status
        self.assertIn("total_memories", status["memory"])
    
    def test_shutdown(self):
        """Test system shutdown."""
        # Register mock modules
        perception = MockPerceptionModule({}, self.orchestrator.memory_manager)
        language = MockLanguageModule({}, self.orchestrator.memory_manager)
        
        # Add spies to shutdown methods
        perception.shutdown = MagicMock()
        language.shutdown = MagicMock()
        
        self.orchestrator.register_module("perception", perception)
        self.orchestrator.register_module("language", language)
        
        # Shutdown
        self.orchestrator.shutdown()
        
        # Check that module shutdown methods were called
        perception.shutdown.assert_called_once()
        language.shutdown.assert_called_once()
    
    def test_error_handling_in_module(self):
        """Test handling of errors in modules."""
        # Create a module that raises an exception during processing
        class ErrorModule(BrainModule):
            def process(self, input_data):
                raise ValueError("Test error")
        
        # Register modules
        self.orchestrator.register_module("perception", ErrorModule({}, self.orchestrator.memory_manager))
        self.orchestrator.register_module("language", MockLanguageModule({}, self.orchestrator.memory_manager))
        
        # Create test input
        input_data = {
            "type": "text",
            "content": "Hello, this is a test."
        }
        
        # This should raise an exception in the perception module
        # The orchestrator should catch and handle it
        with self.assertRaises(Exception):
            self.orchestrator.process_input(input_data)


if __name__ == "__main__":
    unittest.main()
