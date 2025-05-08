#!/usr/bin/env python3
# main.py - Entry point for Modular AI Companion System

import logging
import os
from app import app
from core.orchestrator import Orchestrator
from core.config_manager import ConfigManager
from utils.logger import setup_logging
from utils.ai import get_llm_service

# Initialize logging
setup_logging()
logger = logging.getLogger(__name__)

def initialize_system():
    """Initialize the AI Companion System."""
    # Start the automatic backup manager
    from memory.backup_manager import get_backup_manager
    backup_manager = get_backup_manager()
    backup_manager.start_scheduled_backups()
    
    # Initialize modules
    logger.info("Initializing AI Companion System...")
    
    # Import core components
    from core.orchestrator import Orchestrator
    from digital_soul.core import get_soul
    
    # Initialize the orchestrator
    orchestrator = Orchestrator()
    orchestrator.initialize_system()
    
    # Log system components
    logger.info("System components initialized:")
    logger.info(f"- Digital Soul: {get_soul().soul_id}")
    
    return orchestrator
    logger.info("Initializing AI Companion System...")
    
    # Load configuration
    config_path = os.path.join(os.path.dirname(__file__), 'config.yaml')
    config_manager = ConfigManager(config_path)
    config = config_manager.load_config()
    
    # Initialize the LLM service based on configuration
    ai_provider = config.get('ai', {}).get('provider', 'openai')
    try:
        llm_service = get_llm_service(ai_provider)
        logger.info(f"Successfully initialized {ai_provider} LLM service")
    except Exception as e:
        logger.error(f"Failed to initialize {ai_provider} LLM service: {e}")
        logger.warning("The system will continue without LLM capabilities")
        llm_service = None
    
    # Initialize the orchestrator (core of the system)
    orchestrator = Orchestrator(config)
    
    # Add the LLM service to the orchestrator
    if llm_service:
        orchestrator.llm_service = llm_service
    
    # Initialize and register all modules
    orchestrator.initialize_modules()
    
    # If we have an external_comm module and LLM service, connect them
    external_comm = orchestrator.get_module('external_comm')
    if external_comm and llm_service:
        external_comm.llm_service = llm_service
        logger.info("Connected LLM service to External Communication module")
    
    logger.info("AI Companion System initialized successfully")
    return orchestrator

if __name__ == '__main__':
    # Initialize the AI system
    orchestrator = initialize_system()
    
    # Register the orchestrator with the Flask app
    app.config['ORCHESTRATOR'] = orchestrator
    
    # Run the Flask app
    app.run(host='0.0.0.0', port=5000, debug=True)
