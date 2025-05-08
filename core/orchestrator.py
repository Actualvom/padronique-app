#!/usr/bin/env python3
# core/orchestrator.py - Core orchestrator for the AI Companion System

import logging
import importlib
import time
from typing import Dict, List, Any, Optional

from memory.memory_manager import MemoryManager
from core.security import SecurityManager
from brain.module_base import BrainModule

logger = logging.getLogger(__name__)

class Orchestrator:
    """
    Core orchestrator for the AI Companion System.
    
    The Orchestrator is responsible for:
    1. Initializing and managing all brain modules
    2. Coordinating communication between modules
    3. Managing the memory system
    4. Handling security and access control
    5. Coordinating self-improvement through the learning module
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the Orchestrator.
        
        Args:
            config: Configuration dictionary loaded from config.yaml
        """
        self.config = config
        self.system_name = config['system']['name']
        self.version = config['system']['version']
        
        # Initialize memory manager
        self.memory_manager = MemoryManager(config['memory'])
        
        # Initialize security manager
        self.security_manager = SecurityManager(config['security'])
        
        # Dictionary to store brain modules
        self.modules: Dict[str, BrainModule] = {}
        
        # Start time for uptime tracking
        self.start_time = time.time()
        
        logger.info(f"Orchestrator initialized for {self.system_name} v{self.version}")
    
    def initialize_modules(self) -> None:
        """Initialize all enabled brain modules from configuration."""
        logger.info("Initializing brain modules...")
        
        for module_config in self.config['brain']['modules']:
            name = module_config['name']
            if not module_config.get('enabled', True):
                logger.info(f"Module '{name}' is disabled, skipping")
                continue
            
            try:
                # Dynamically import the module class
                module_path = f"brain.{name}_module"
                class_name = f"{name.capitalize()}Module"
                
                module = importlib.import_module(module_path)
                module_class = getattr(module, class_name)
                
                # Instantiate the module
                instance = module_class(module_config.get('config', {}), self.memory_manager)
                self.register_module(name, instance)
                logger.info(f"Module '{name}' initialized successfully")
            except (ImportError, AttributeError) as e:
                logger.error(f"Failed to initialize module '{name}': {e}")
    
    def register_module(self, name: str, module: BrainModule) -> None:
        """
        Register a brain module with the orchestrator.
        
        Args:
            name: Name of the module
            module: Module instance
        """
        self.modules[name] = module
        logger.debug(f"Module '{name}' registered with orchestrator")
    
    def get_module(self, name: str) -> Optional[BrainModule]:
        """
        Get a brain module by name.
        
        Args:
            name: Name of the module
            
        Returns:
            The module instance if found, None otherwise
        """
        return self.modules.get(name)
    
    def process_input(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process input through the appropriate modules.
        
        Args:
            input_data: Input data with type and content
            
        Returns:
            Response from the system
        """
        logger.debug(f"Processing input: {input_data}")
        
        # Check security access
        if not self.security_manager.authorize_request(input_data):
            return {"error": "Unauthorized request"}
        
        input_type = input_data.get('type', 'text')
        content = input_data.get('content', '')
        
        # Start with perception module to process the input
        perception = self.get_module('perception')
        if not perception:
            return {"error": "Perception module not available"}
        
        # Process the input through perception
        perceived_data = perception.process({'type': input_type, 'content': content})
        
        # Use language module to understand the input
        language = self.get_module('language')
        if language:
            understanding = language.process(perceived_data)
        else:
            understanding = perceived_data
        
        # Use reasoning module to formulate a response
        reasoning = self.get_module('reasoning')
        if reasoning:
            response_data = reasoning.process(understanding)
        else:
            response_data = understanding
        
        # Record interaction in memory
        self.memory_manager.store_memory({
            'type': 'interaction',
            'input': input_data,
            'response': response_data,
            'timestamp': time.time()
        }, tags=['interaction', input_type])
        
        # Use learning module for self-improvement
        learning = self.get_module('learning')
        if learning:
            learning.process({
                'input': input_data,
                'understanding': understanding,
                'response': response_data
            })
        
        return response_data
    
    def get_system_status(self) -> Dict[str, Any]:
        """
        Get the current status of the system.
        
        Returns:
            Dictionary with system status information
        """
        uptime = time.time() - self.start_time
        
        module_status = {}
        for name, module in self.modules.items():
            module_status[name] = {
                'active': module.is_active(),
                'last_used': module.last_used,
                'stats': module.get_stats()
            }
        
        memory_stats = self.memory_manager.get_stats()
        
        return {
            'system_name': self.system_name,
            'version': self.version,
            'uptime': uptime,
            'modules': module_status,
            'memory': memory_stats
        }
    
    def shutdown(self) -> None:
        """Properly shut down the system, saving state if needed."""
        logger.info("Shutting down orchestrator...")
        
        # Shutdown all modules
        for name, module in self.modules.items():
            try:
                module.shutdown()
                logger.info(f"Module '{name}' shut down successfully")
            except Exception as e:
                logger.error(f"Error shutting down module '{name}': {e}")
        
        # Save memory state
        self.memory_manager.save_state()
        logger.info("Memory state saved")
        
        logger.info("Orchestrator shut down complete")
