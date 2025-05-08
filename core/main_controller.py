#!/usr/bin/env python3
"""
main_controller.py: The entry point for Padronique.
Loads configurations, initializes Digital Soul, and launches the Orchestrator.
"""

import os
import logging
import threading
import time
from core.config_manager import load_config
from digital_soul.digital_soul import DigitalSoul
from core.orchestrator import Orchestrator

logger = logging.getLogger(__name__)

class PadroniqueSystem:
    """Main controller class for the Padronique system."""
    
    def __init__(self, config):
        self.config = config
        self.soul = DigitalSoul(config, memory_dir="digital_soul/memories")
        self.orchestrator = Orchestrator(self.soul, config)
        self._running = False
        self._thread = None
    
    def start(self):
        """Start the Padronique orchestrator in a separate thread."""
        if self._running:
            logger.warning("Padronique is already running")
            return
        
        self._running = True
        self._thread = threading.Thread(target=self._run_loop)
        self._thread.daemon = True
        self._thread.start()
        logger.info("Padronique system started")
    
    def _run_loop(self):
        """Run the main orchestrator loop."""
        try:
            self.orchestrator.start_loop()
        except Exception as e:
            logger.error(f"Error in Padronique main loop: {e}")
            self._running = False
    
    def stop(self):
        """Stop the Padronique system."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=5.0)
        logger.info("Padronique system stopped")

# Global instance for easy access
_padronique_instance = None

def initialize_padronique():
    """Initialize and return the Padronique system."""
    global _padronique_instance
    
    if _padronique_instance is None:
        # Ensure directories exist
        os.makedirs("digital_soul/memories", exist_ok=True)
        os.makedirs("logs", exist_ok=True)
        
        # Load configuration
        config = load_config("config/settings.yaml")
        
        # Create and start Padronique
        _padronique_instance = PadroniqueSystem(config)
        _padronique_instance.start()
        
        # Allow time for initialization
        time.sleep(1)
    
    return _padronique_instance

def main():
    """Main function to run Padronique as a standalone application."""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler("logs/padronique.log")
        ]
    )
    
    # Initialize Padronique
    padronique = initialize_padronique()
    
    try:
        # Keep main thread alive while Padronique runs in background
        while padronique._running:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received, shutting down...")
        padronique.stop()

if __name__ == '__main__':
    main()
