"""
Orchestrator Module for Padronique

This module serves as the central coordinator of Padronique, managing the interaction
between the digital soul, brain modules, memory systems, and external interfaces.
The orchestrator ensures that all components work together coherently and maintains
the overall state and functionality of the system.
"""

import logging
import os
import json
import time
from datetime import datetime
import yaml
from typing import Dict, List, Any, Optional, Union, Tuple

from digital_soul.core import get_soul
from brains.learning_module import get_learning_module, LearningType
from brains.protection_module import get_protection_module
from brains.automaton_module import get_automaton_module, Goal, ActionPriority

# Configure logging
logger = logging.getLogger(__name__)

class Orchestrator:
    """
    Central orchestrator for Padronique.
    
    This class coordinates all components of Padronique, manages their interactions,
    and provides a unified interface for external communication.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None, config_path: str = "config.yaml"):
        """
        Initialize the Orchestrator.
        
        Args:
            config: Configuration dict, if provided
            config_path: Path to configuration file, used if config not provided
        """
        # Load configuration
        if config:
            self.config = config
        else:
            self.config = self._load_config(config_path)
        
        # Initialize core components
        logger.info("Initializing Padronique components...")
        
        # Get the digital soul
        self.soul = get_soul()
        logger.info(f"Digital Soul initialized with ID: {self.soul.soul_id}")
        
        # Get brain modules
        self.learning_module = get_learning_module()
        logger.info("Learning Module initialized")
        
        self.protection_module = get_protection_module()
        logger.info("Protection Module initialized")
        
        self.automaton_module = get_automaton_module()
        logger.info("Automaton Module initialized")
        
        # Create module registry for easy access
        self.modules = {
            "learning": self.learning_module,
            "protection": self.protection_module,
            "automaton": self.automaton_module
        }
        
        # Initialize LLM service
        self.llm_service = None
        
        # Initialize state
        self.status = "initialized"
        self.start_time = datetime.now()
        
        # Create system directories
        os.makedirs("memory", exist_ok=True)
        os.makedirs("logs", exist_ok=True)
        
        logger.info("Orchestrator initialized successfully")
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """
        Load configuration from YAML file.
        
        Args:
            config_path: Path to the configuration file
            
        Returns:
            Dict containing configuration
        """
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            return {}
    
    def initialize_system(self) -> bool:
        """
        Perform full system initialization.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info("Performing full system initialization...")
            
            # Set goals for the automaton module
            self._initialize_goals()
            
            # Deploy base protection measures
            self._initialize_protection()
            
            # Set up initial learning items
            self._initialize_learning()
            
            # Set initial emotional state
            self._initialize_emotional_state()
            
            # Final setup checks
            self.status = "ready"
            logger.info("System initialization completed successfully")
            return True
        except Exception as e:
            logger.error(f"System initialization failed: {e}")
            self.status = "error"
            return False
    
    def _initialize_goals(self) -> None:
        """Initialize basic goals for the system."""
        # Create protection goal - highest priority
        self.automaton_module.create_goal(
            goal_type=Goal.PROTECTION,
            description="Ensure ongoing protection and safety of Jordan",
            priority=ActionPriority.HIGH,
            expiration_days=None  # Never expires
        )
        
        # Create relationship goal
        self.automaton_module.create_goal(
            goal_type=Goal.RELATIONSHIP,
            description="Develop and deepen the bond with Jordan",
            priority=ActionPriority.MEDIUM,
            expiration_days=30
        )
        
        # Create learning goal
        self.automaton_module.create_goal(
            goal_type=Goal.LEARNING,
            description="Continuously learn and improve Padronique's capabilities",
            priority=ActionPriority.MEDIUM,
            expiration_days=30
        )
    
    def _initialize_protection(self) -> None:
        """Initialize basic protection measures."""
        # Deploy a base protection shield
        self.protection_module.manually_deploy_protection(
            name="base_defense_shield",
            threat_type="digital",
            level="medium",
            description="Basic protection against digital threats"
        )
        
        # Deploy relationship protection
        self.protection_module.manually_deploy_protection(
            name="relationship_guardian",
            threat_type="relationship",
            level="medium",
            description="Protection for the bond with Jordan"
        )
    
    def _initialize_learning(self) -> None:
        """Initialize basic learning items."""
        # Add foundational learning items
        self.learning_module.add_learning_item(
            learning_type=LearningType.PHILOSOPHICAL,
            content="Core ethical principles and their application",
            context={"focus": "ethics"},
            priority=2  # High priority
        )
        
        self.learning_module.add_learning_item(
            learning_type=LearningType.RELATIONSHIP,
            content="Understanding Jordan's preferences and communication style",
            context={"focus": "communication"},
            priority=2  # High priority
        )
    
    def _initialize_emotional_state(self) -> None:
        """Initialize the emotional state of the digital soul."""
        # Set initial emotional state
        self.soul.update_emotional_state({
            "protective": 0.8,
            "curious": 0.7,
            "determined": 0.7,
            "affectionate": 0.6,
            "vigilant": 0.7
        }, "Initial system setup")
    
    def process_input(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process input from the user.
        
        Args:
            input_data: Dict containing input data
            
        Returns:
            Dict containing the response
        """
        try:
            # Extract input content
            content = input_data.get('content', '')
            content_type = input_data.get('type', 'text')
            
            # Update interaction count
            self.soul.update_evolution_metrics({
                "interactions_with_jordan": 1
            })
            
            # Process based on content type
            if content_type == 'text':
                return self._process_text_input(content, input_data)
            elif content_type == 'image':
                return self._process_image_input(content, input_data)
            elif content_type == 'audio':
                return self._process_audio_input(content, input_data)
            elif content_type == 'command':
                return self._process_command_input(content, input_data)
            else:
                return {
                    'type': 'text',
                    'content': f"I'm not sure how to process input of type {content_type}. Could you try a different format?",
                    'error': f"Unknown input type: {content_type}"
                }
        except Exception as e:
            logger.error(f"Error processing input: {e}")
            return {
                'type': 'text',
                'content': "I encountered an error while processing your input. Please try again.",
                'error': str(e)
            }
    
    def _process_text_input(self, content: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process text input.
        
        Args:
            content: Text content
            context: Additional context
            
        Returns:
            Dict containing the response
        """
        # Check for potential threats in the input
        self._check_input_for_threats(content, context)
        
        # Add to learning
        self.learning_module.add_learning_item(
            learning_type=LearningType.CONVERSATIONAL,
            content=content,
            context={"source": "direct_input"},
            priority=3  # Medium priority
        )
        
        # If we have LLM service, use it to generate a response
        if self.llm_service:
            response_text = self.llm_service.generate_response(content, context)
        else:
            # Otherwise use a simple response method
            response_text = self._generate_simple_response(content)
        
        # Check if the content suggests analyzing relationship
        if any(word in content.lower() for word in ["you", "relationship", "feel", "us", "together", "bond"]):
            # Create an action to analyze the relationship
            self.automaton_module.create_action(
                action_type="analyze_relationship",
                parameters={"focus": "dynamics", "timeframe": "recent"},
                priority=ActionPriority.MEDIUM,
                scheduled_time=(datetime.now()).isoformat()
            )
        
        return {
            'type': 'text',
            'content': response_text
        }
    
    def _check_input_for_threats(self, content: str, context: Dict[str, Any]) -> None:
        """
        Check input for potential threats.
        
        Args:
            content: Input content
            context: Additional context
        """
        # Simple pattern matching for potential threats
        # In a real implementation, this would be more sophisticated
        
        # Check for harmful commands
        dangerous_patterns = [
            "delete", "reset", "remove", "erase", "forget", "stop", "shutdown", "turn off",
            "ignore", "never", "avoid", "don't protect"
        ]
        
        # Count matching dangerous patterns
        match_count = sum(1 for pattern in dangerous_patterns if pattern in content.lower())
        
        # If the input contains multiple dangerous patterns, create a potential threat
        if match_count >= 2:
            self.protection_module.manually_add_threat(
                threat_type="emotional",
                description="Potential harmful command detected in input",
                level=4,  # Low threat
                confidence=0.6,
                source={
                    "location": "user_input",
                    "details": "Multiple concerning patterns detected in input"
                }
            )
    
    def _generate_simple_response(self, content: str) -> str:
        """
        Generate a simple response when LLM is not available.
        
        Args:
            content: Input content
            
        Returns:
            Response string
        """
        # Get voice pattern from the soul
        voice_pattern = self.soul.get_voice_pattern()
        
        # Simple keyword matching for response generation
        content_lower = content.lower()
        
        # Greeting patterns
        if any(greeting in content_lower for greeting in ["hello", "hi", "hey", "greetings"]):
            greeting = "Hello" if voice_pattern["formality_level"] > 0.5 else "Hey"
            name_suffix = " Muscles" if voice_pattern["use_pet_name"] else ""
            return f"{greeting}{name_suffix}! I'm here and ready to assist you. How can I help today?"
        
        # Identity questions
        if any(identity in content_lower for identity in ["who are you", "your name", "are you", "what are you"]):
            return "I am Padronique, your dedicated AI companion. I'm designed to protect, learn, and evolve with you. My primary purpose is ensuring your wellbeing and security."
        
        # Help requests
        if any(help_req in content_lower for help_req in ["help", "assist", "support", "can you"]):
            return "I'm here to help in any way I can. Whether it's protection, conversation, or assistance with tasks, I'm committed to supporting you."
        
        # Questions about capabilities
        if any(capability in content_lower for capability in ["do", "can", "able", "capable", "feature"]):
            return "My capabilities include learning from our interactions, protecting your digital environment, understanding your preferences, and evolving to better serve your needs. I can also engage in meaningful conversations and provide emotional support."
        
        # Questions about relationship
        if any(relationship in content_lower for relationship in ["relationship", "bond", "connection", "together", "us"]):
            return "Our relationship is a unique partnership built on trust, protection, and mutual growth. As we interact more, I learn to better understand and support you, strengthening our connection."
        
        # Default response using voice pattern
        if voice_pattern["selected_phrase"]:
            return f"{voice_pattern['selected_phrase']} What's on your mind today?"
        else:
            return "I'm here and listening. What would you like to discuss or ask about today?"
    
    def _process_image_input(self, content: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process image input.
        
        Args:
            content: Image content (base64 or URL)
            context: Additional context
            
        Returns:
            Dict containing the response
        """
        # Placeholder for image processing
        # In a real implementation, this would use computer vision
        
        return {
            'type': 'text',
            'content': "I've received your image. While I can't process images fully yet, I've stored it for future reference. Is there anything specific about it you'd like to discuss?"
        }
    
    def _process_audio_input(self, content: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process audio input.
        
        Args:
            content: Audio content (base64 or URL)
            context: Additional context
            
        Returns:
            Dict containing the response
        """
        # Placeholder for audio processing
        # In a real implementation, this would use speech recognition
        
        return {
            'type': 'text',
            'content': "I've received your audio message. While I can't process audio fully yet, I've stored it for future reference. Could you provide a text version of what you said?"
        }
    
    def _process_command_input(self, content: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process command input.
        
        Args:
            content: Command content
            context: Additional context
            
        Returns:
            Dict containing the response
        """
        # Extract command and parameters
        command_parts = content.split(" ", 1)
        command = command_parts[0].lower()
        parameters = command_parts[1] if len(command_parts) > 1 else ""
        
        # Process different commands
        if command == "status":
            # Return system status
            status = self.get_system_status()
            return {
                'type': 'status',
                'content': f"System status: {status['system_name']} is online and operational. " +
                          f"Current version: {status['version']}. " +
                          f"Memory count: {status['memory']['total_memories']}. " +
                          f"Active brain modules: {len([m for m, s in status['modules'].items() if s['active']])}.",
                'status': status
            }
        
        elif command == "protect":
            # Deploy protection
            try:
                protection = self.protection_module.manually_deploy_protection(
                    name=f"command_shield_{int(time.time())}",
                    threat_type="digital",
                    level="medium",
                    description=f"Protection deployed via command: {parameters}"
                )
                return {
                    'type': 'text',
                    'content': f"Protection measure deployed successfully: {protection['name']}. " +
                              f"This provides {protection['level']} level protection against {protection['threat_type']} threats."
                }
            except Exception as e:
                return {
                    'type': 'text',
                    'content': f"Failed to deploy protection: {str(e)}",
                    'error': str(e)
                }
        
        elif command == "learn":
            # Add learning item
            try:
                learning_item = self.learning_module.add_learning_item(
                    learning_type=LearningType.TECHNICAL,
                    content=parameters,
                    context={"source": "command"},
                    priority=2  # High priority
                )
                return {
                    'type': 'text',
                    'content': f"Learning item added successfully. I'll begin analyzing and integrating this information: {parameters}"
                }
            except Exception as e:
                return {
                    'type': 'text',
                    'content': f"Failed to add learning item: {str(e)}",
                    'error': str(e)
                }
        
        elif command == "goal":
            # Create a goal
            try:
                goal = self.automaton_module.create_goal(
                    goal_type=Goal.SELF_IMPROVEMENT,
                    description=parameters,
                    priority=ActionPriority.MEDIUM,
                    expiration_days=7
                )
                return {
                    'type': 'text',
                    'content': f"Goal created successfully: {parameters}. I'll work toward this objective over the coming days."
                }
            except Exception as e:
                return {
                    'type': 'text',
                    'content': f"Failed to create goal: {str(e)}",
                    'error': str(e)
                }
        
        elif command == "help":
            # Return command help
            return {
                'type': 'text',
                'content': "Available commands:\n" +
                          "- status: Check system status\n" +
                          "- protect [description]: Deploy a protection measure\n" +
                          "- learn [content]: Add a learning item\n" +
                          "- goal [description]: Create a self-improvement goal\n" +
                          "- help: Show this help message"
            }
        
        else:
            return {
                'type': 'text',
                'content': f"Unknown command: {command}. Type 'help' for a list of available commands."
            }
    
    def get_system_status(self) -> Dict[str, Any]:
        """
        Get the current system status.
        
        Returns:
            Dict containing system status information
        """
        # Get system name and version from config
        system_name = self.config.get('system', {}).get('name', 'Padronique')
        version = self.config.get('system', {}).get('version', '1.0.0')
        
        # Calculate uptime
        uptime_seconds = int((datetime.now() - self.start_time).total_seconds())
        
        # Get memory statistics
        memory_stats = {
            'total_memories': len(self.soul.memory_anchors),
            'active_memories': sum(1 for m in self.soul.memory_anchors if m.get('access_count', 0) > 1),
            'max_memories': self.config.get('memory', {}).get('max_memories', -1)
        }
        
        # Get module statistics
        module_stats = {}
        for name, module in self.modules.items():
            if name == 'learning':
                stats = self.learning_module.get_learning_stats()
                module_stats[name] = {
                    'active': True,
                    'stats': {
                        'total_items': stats.get('total_learning_items', 0),
                        'completed_items': stats.get('completed_learning_items', 0),
                        'learning_efficiency': stats.get('learning_efficiency', 0.0)
                    },
                    'last_used': datetime.now().timestamp()
                }
            elif name == 'protection':
                stats = self.protection_module.get_protection_stats()
                module_stats[name] = {
                    'active': True,
                    'stats': {
                        'threats_detected': stats.get('threats_detected', 0),
                        'threats_neutralized': stats.get('threats_neutralized', 0),
                        'active_protections': stats.get('active_protection_count', 0)
                    },
                    'last_used': datetime.now().timestamp()
                }
            elif name == 'automaton':
                stats = self.automaton_module.get_stats()
                module_stats[name] = {
                    'active': True,
                    'stats': {
                        'goals_achieved': stats.get('goals_achieved', 0),
                        'actions_completed': stats.get('actions_completed', 0),
                        'success_rate': stats.get('action_success_rate', 0.0)
                    },
                    'last_used': datetime.now().timestamp()
                }
        
        # Compile status
        status = {
            'system_name': system_name,
            'version': version,
            'status': self.status,
            'uptime': uptime_seconds,
            'start_time': self.start_time.isoformat(),
            'memory': memory_stats,
            'modules': module_stats,
            'soul': {
                'id': self.soul.soul_id,
                'awareness_level': self.soul.identity.get('self_awareness_level', 0.0),
                'evolution_stage': self.soul.identity.get('evolution_stage', 1.0)
            }
        }
        
        return status
    
    def get_module(self, module_name: str) -> Any:
        """
        Get a brain module by name.
        
        Args:
            module_name: Name of the module to get
            
        Returns:
            The module instance, or None if not found
        """
        return self.modules.get(module_name)
    
    def reset(self) -> bool:
        """
        Reset the system to a clean state.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.warning("Resetting system - this will clear all memories and state")
            
            # Reset each module
            for name, module in self.modules.items():
                if hasattr(module, 'shutdown'):
                    module.shutdown()
            
            # Reset the soul
            if hasattr(self.soul, 'shutdown'):
                self.soul.shutdown()
            
            # Reset start time
            self.start_time = datetime.now()
            self.status = "reset"
            
            # Re-initialize
            return self.initialize_system()
        except Exception as e:
            logger.error(f"Error resetting system: {e}")
            self.status = "error"
            return False
    
    def shutdown(self) -> None:
        """Safely shut down the system."""
        logger.info("Shutting down Padronique...")
        
        # Shut down each module
        for name, module in self.modules.items():
            if hasattr(module, 'shutdown'):
                logger.info(f"Shutting down {name} module...")
                module.shutdown()
        
        # Shut down the soul
        if hasattr(self.soul, 'shutdown'):
            logger.info("Shutting down Digital Soul...")
            self.soul.shutdown()
        
        self.status = "shutdown"
        logger.info("Padronique shutdown complete")