#!/usr/bin/env python3
# utils/logger.py - Logging configuration for the AI Companion System

import os
import logging
import logging.handlers
import sys
from typing import Optional


def setup_logging(log_level: Optional[str] = None, log_file: Optional[str] = None) -> None:
    """
    Set up logging for the AI Companion System.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file
    """
    # Get log level from environment or config
    if not log_level:
        log_level = os.environ.get('LOG_LEVEL', 'INFO')
    
    # Convert string log level to logging constant
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Create logs directory if it doesn't exist
    if log_file:
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
    else:
        # Default log file
        log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, 'ignis.log')
    
    # Configure root logger
    logging.basicConfig(
        level=numeric_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.handlers.RotatingFileHandler(
                log_file, maxBytes=10485760, backupCount=5  # 10MB files, keep 5 backups
            )
        ]
    )
    
    # Set level for specific modules if needed
    logging.getLogger('werkzeug').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    
    # Set debug level for our modules
    app_logger = logging.getLogger('app')
    app_logger.setLevel(numeric_level)
    
    # Log initial setup
    logging.info(f"Logging initialized at level {log_level}")
    logging.info(f"Log file: {log_file}")


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger for a specific module.
    
    Args:
        name: Name of the module
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)


class LogCapture:
    """
    Context manager to capture logs for testing or analysis.
    
    Example:
        with LogCapture() as logs:
            # Do something that logs
            function_that_logs()
        
        # Now logs.records contains all logged records
        for record in logs.records:
            print(f"{record.levelname}: {record.message}")
    """
    
    def __init__(self, level: int = logging.DEBUG):
        """
        Initialize the LogCapture.
        
        Args:
            level: Minimum log level to capture
        """
        self.level = level
        self.handler = None
        self.records = []
    
    def __enter__(self):
        """Set up the log handler when entering context."""
        self.handler = logging.handlers.MemoryHandler(capacity=1024, flushLevel=logging.CRITICAL)
        self.handler.setLevel(self.level)
        
        # Add a formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.handler.setFormatter(formatter)
        
        # Add a target that stores records
        target = logging.Handler()
        target.handle = self.records.append
        self.handler.setTarget(target)
        
        # Add the handler to the root logger
        logging.getLogger().addHandler(self.handler)
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Clean up the log handler when exiting context."""
        self.handler.flush()
        logging.getLogger().removeHandler(self.handler)


def configure_module_logging(module_name: str, level: str = 'INFO') -> None:
    """
    Configure logging for a specific module.
    
    Args:
        module_name: Name of the module
        level: Logging level for the module
    """
    logger = logging.getLogger(module_name)
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    logger.setLevel(numeric_level)
    
    # Ensure we have a StreamHandler for console output
    has_stream_handler = False
    for handler in logger.handlers:
        if isinstance(handler, logging.StreamHandler):
            has_stream_handler = True
            break
    
    if not has_stream_handler:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    logger.info(f"Module {module_name} logging configured at level {level}")
