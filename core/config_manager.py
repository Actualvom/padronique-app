#!/usr/bin/env python3
# core/config_manager.py - Configuration management for the AI Companion System

import os
import logging
import yaml
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class ConfigManager:
    """
    Configuration manager for the AI Companion System.
    
    Responsible for:
    1. Loading configuration from YAML files
    2. Validating configuration
    3. Providing access to configuration values
    4. Saving configuration changes
    """
    
    def __init__(self, config_path: str):
        """
        Initialize the ConfigManager.
        
        Args:
            config_path: Path to the configuration YAML file
        """
        self.config_path = config_path
        self.config = {}
        logger.info(f"Config manager initialized with path: {config_path}")
    
    def load_config(self) -> Dict[str, Any]:
        """
        Load configuration from the YAML file.
        
        Returns:
            Loaded configuration as a dictionary
        """
        try:
            with open(self.config_path, 'r') as file:
                self.config = yaml.safe_load(file)
            logger.info("Configuration loaded successfully")
            self._validate_config()
            return self.config
        except FileNotFoundError:
            logger.error(f"Configuration file not found: {self.config_path}")
            # Create default config
            self.config = self._create_default_config()
            self.save_config()
            return self.config
        except yaml.YAMLError as e:
            logger.error(f"Error parsing YAML configuration: {e}")
            raise
    
    def _validate_config(self) -> None:
        """Validate the loaded configuration."""
        required_sections = ['system', 'memory', 'brain', 'api', 'security']
        
        for section in required_sections:
            if section not in self.config:
                logger.warning(f"Missing required configuration section: {section}")
                self.config[section] = {}
        
        # Validate system section
        system = self.config['system']
        if 'name' not in system:
            system['name'] = "Ignis"
            logger.warning("System name not found in config, using default: Ignis")
        
        if 'version' not in system:
            system['version'] = "0.1.0"
            logger.warning("System version not found in config, using default: 0.1.0")
        
        # Add other validations as needed
    
    def _create_default_config(self) -> Dict[str, Any]:
        """
        Create a default configuration.
        
        Returns:
            Default configuration dictionary
        """
        logger.info("Creating default configuration")
        return {
            'system': {
                'name': 'Ignis',
                'version': '0.1.0',
                'log_level': 'INFO'
            },
            'memory': {
                'storage_path': './data/memory',
                'encryption_enabled': True,
                'max_memories': 10000,
                'default_expiry_days': 365
            },
            'brain': {
                'modules': [
                    {
                        'name': 'language',
                        'enabled': True,
                        'config': {
                            'model_type': 'transformer',
                            'context_window': 2048
                        }
                    },
                    {
                        'name': 'reasoning',
                        'enabled': True,
                        'config': {
                            'reasoning_depth': 3,
                            'logical_frameworks': ['deductive', 'inductive', 'abductive']
                        }
                    },
                    {
                        'name': 'learning',
                        'enabled': True,
                        'config': {
                            'learning_rate': 0.01,
                            'reinforcement_method': 'simple_feedback',
                            'batch_size': 32
                        }
                    },
                    {
                        'name': 'perception',
                        'enabled': True,
                        'config': {
                            'input_channels': ['text', 'image'],
                            'feature_extraction': 'basic'
                        }
                    }
                ]
            },
            'api': {
                'rate_limit': 100,
                'timeout_seconds': 30,
                'swift_bridge_enabled': True
            },
            'security': {
                'encryption_key_rotation_days': 90,
                'require_authentication': True,
                'sensitive_data_tags': ['personal', 'financial', 'health', 'credentials']
            },
            'sandbox': {
                'enabled': True,
                'isolation_level': 'process',
                'timeout_seconds': 10,
                'max_memory_mb': 500
            }
        }
    
    def get_value(self, path: str, default: Any = None) -> Any:
        """
        Get a configuration value by path.
        
        Args:
            path: Dot-separated path to the configuration value
            default: Default value if the path doesn't exist
            
        Returns:
            Configuration value or default
        """
        parts = path.split('.')
        current = self.config
        
        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return default
        
        return current
    
    def set_value(self, path: str, value: Any) -> None:
        """
        Set a configuration value by path.
        
        Args:
            path: Dot-separated path to the configuration value
            value: Value to set
        """
        parts = path.split('.')
        current = self.config
        
        # Navigate to the parent of the target path
        for part in parts[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]
        
        # Set the value
        current[parts[-1]] = value
    
    def save_config(self) -> bool:
        """
        Save the current configuration to the YAML file.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            
            with open(self.config_path, 'w') as file:
                yaml.dump(self.config, file, default_flow_style=False)
            
            logger.info("Configuration saved successfully")
            return True
        except Exception as e:
            logger.error(f"Error saving configuration: {e}")
            return False
