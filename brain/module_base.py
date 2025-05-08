#!/usr/bin/env python3
# brain/module_base.py - Base brain module for the AI Companion System

import logging
import time
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod

from memory.memory_manager import MemoryManager

logger = logging.getLogger(__name__)

class BrainModule(ABC):
    """
    Abstract base class for all brain modules.
    
    Defines the interface that all brain modules must implement.
    """
    
    def __init__(self, config: Dict[str, Any], memory_manager: MemoryManager):
        """
        Initialize the brain module.
        
        Args:
            config: Module-specific configuration
            memory_manager: Memory manager instance for storing/retrieving memories
        """
        self.config = config
        self.memory_manager = memory_manager
        self.active = True
        self.last_used = 0
        self.processing_count = 0
        self.error_count = 0
        self.total_processing_time = 0
        
        logger.info(f"{self.__class__.__name__} initialized with config: {config}")
    
    @abstractmethod
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process input data and return a result.
        
        Args:
            input_data: Input data to process
            
        Returns:
            Processed output data
        """
        pass
    
    def is_active(self) -> bool:
        """
        Check if the module is active.
        
        Returns:
            True if active, False otherwise
        """
        return self.active
    
    def activate(self) -> None:
        """Activate the module."""
        self.active = True
        logger.info(f"{self.__class__.__name__} activated")
    
    def deactivate(self) -> None:
        """Deactivate the module."""
        self.active = False
        logger.info(f"{self.__class__.__name__} deactivated")
    
    def update_config(self, new_config: Dict[str, Any]) -> None:
        """
        Update the module's configuration.
        
        Args:
            new_config: New configuration to apply
        """
        self.config.update(new_config)
        logger.info(f"{self.__class__.__name__} config updated: {new_config}")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get module statistics.
        
        Returns:
            Dictionary with module statistics
        """
        avg_processing_time = 0
        if self.processing_count > 0:
            avg_processing_time = self.total_processing_time / self.processing_count
        
        return {
            'active': self.active,
            'last_used': self.last_used,
            'processing_count': self.processing_count,
            'error_count': self.error_count,
            'avg_processing_time': avg_processing_time
        }
    
    def shutdown(self) -> None:
        """Perform any necessary cleanup before shutdown."""
        logger.info(f"{self.__class__.__name__} shutting down")
    
    def _record_processing_metrics(self, start_time: float, success: bool = True) -> None:
        """
        Record processing metrics.
        
        Args:
            start_time: Start time of processing
            success: Whether processing was successful
        """
        self.last_used = time.time()
        processing_time = self.last_used - start_time
        self.total_processing_time += processing_time
        self.processing_count += 1
        
        if not success:
            self.error_count += 1
