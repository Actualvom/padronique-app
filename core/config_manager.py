#!/usr/bin/env python3
"""
config_manager.py: Loads YAML configuration files.
"""

import os
import yaml
import logging

logger = logging.getLogger("padronique.config_manager")

def load_config(path):
    """
    Load a YAML configuration file.
    
    Args:
        path: Path to the YAML file
        
    Returns:
        Dict containing configuration values or empty dict if file not found
    """
    try:
        if not os.path.exists(path):
            logger.warning(f"Config file not found: {path}")
            return {}
            
        with open(path, 'r') as f:
            config = yaml.safe_load(f)
            logger.info(f"Loaded configuration from {path}")
            return config or {}
    except Exception as e:
        logger.error(f"Error loading config from {path}: {e}")
        return {}

def save_config(config, path):
    """
    Save configuration to a YAML file.
    
    Args:
        config: Dict containing configuration values
        path: Path to save the YAML file
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        directory = os.path.dirname(path)
        if not os.path.exists(directory):
            os.makedirs(directory)
            
        with open(path, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
            logger.info(f"Saved configuration to {path}")
            return True
    except Exception as e:
        logger.error(f"Error saving config to {path}: {e}")
        return False
