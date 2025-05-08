#!/usr/bin/env python3
# main.py - Entry point for Modular AI Companion System

import logging
import os
from app import app
from core.orchestrator import Orchestrator
from core.config_manager import ConfigManager
from utils.logger import setup_logging

# Initialize logging
setup_logging()
logger = logging.getLogger(__name__)

def initialize_system():
    """Initialize the AI Companion System."""
    logger.info("Initializing AI Companion System...")
    
    # Load configuration
    config_path = os.path.join(os.path.dirname(__file__), 'config.yaml')
    config_manager = ConfigManager(config_path)
    config = config_manager.load_config()
    
    # Initialize the orchestrator (core of the system)
    orchestrator = Orchestrator(config)
    
    # Initialize and register all modules
    orchestrator.initialize_modules()
    
    logger.info("AI Companion System initialized successfully")
    return orchestrator

if __name__ == '__main__':
    # Initialize the AI system
    orchestrator = initialize_system()
    
    # Register the orchestrator with the Flask app
    app.config['ORCHESTRATOR'] = orchestrator
    
    # Run the Flask app
    app.run(host='0.0.0.0', port=5000, debug=True)
