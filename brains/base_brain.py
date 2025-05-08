#!/usr/bin/env python3
"""
base_brain.py: Base class for all brain modules.
"""

import logging
import time

class BaseBrain:
    """
    Base class for all brain modules.
    Defines common functionality and interface for brain modules.
    """
    
    def __init__(self, name=None):
        """
        Initialize the brain module.
        
        Args:
            name: Optional brain name, defaults to class name
        """
        self.name = name or self.__class__.__name__
        self.logger = logging.getLogger(f"padronique.brains.{self.name.lower()}")
        self.last_active = 0
        self.stats = {
            "process_count": 0,
            "success_count": 0,
            "error_count": 0,
            "creation_time": time.time()
        }
        self.logger.info(f"{self.name} brain initialized")
    
    def process_input(self, input_data):
        """
        Process input data and produce a response.
        All brain modules must implement this method.
        
        Args:
            input_data: Input data to process (string or other type)
            
        Returns:
            Response data (string or other type)
        """
        self.last_active = time.time()
        self.stats["process_count"] += 1
        
        try:
            # Default implementation does nothing
            self.logger.warning("Default process_input called on BaseBrain - should be overridden")
            self.stats["success_count"] += 1
            return f"{self.name} processed: {input_data}"
        except Exception as e:
            self.logger.error(f"Error processing input: {e}")
            self.stats["error_count"] += 1
            return None
    
    def get_status(self):
        """
        Get brain status and statistics.
        
        Returns:
            dict: Brain status and statistics
        """
        uptime = time.time() - self.stats["creation_time"]
        active_ago = time.time() - self.last_active if self.last_active > 0 else -1
        
        return {
            "name": self.name,
            "uptime_seconds": uptime,
            "last_active_seconds_ago": active_ago,
            "process_count": self.stats["process_count"],
            "success_rate": self._calculate_success_rate(),
            "error_count": self.stats["error_count"]
        }
    
    def _calculate_success_rate(self):
        """Calculate the success rate of processing."""
        if self.stats["process_count"] == 0:
            return 0
        return self.stats["success_count"] / self.stats["process_count"]
    
    def reset_stats(self):
        """Reset brain statistics."""
        self.stats["process_count"] = 0
        self.stats["success_count"] = 0
        self.stats["error_count"] = 0
        return True
