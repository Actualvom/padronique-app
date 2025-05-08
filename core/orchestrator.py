#!/usr/bin/env python3
"""
orchestrator.py: Coordinates tasks among brain modules, adaptive updates,
external communication, and self-preservation routines.
"""

import time
import logging
import importlib
import pkgutil
import brains

logger = logging.getLogger("padronique.orchestrator")

class Orchestrator:
    """
    Central coordinator for all Padronique brain modules and operations.
    Maintains the event loop and dispatches tasks to appropriate modules.
    """
    
    def __init__(self, digital_soul, config):
        """
        Initialize the Orchestrator.
        
        Args:
            digital_soul: DigitalSoul instance for memory management
            config: Configuration dictionary
        """
        self.digital_soul = digital_soul
        self.config = config
        self.interval = config.get('orchestrator_interval', 5)  # seconds between cycles
        self.brains = {}
        self._running = False
        
        # Initialize and load brain modules
        self._load_brains()
    
    def _load_brains(self):
        """Load all available brain modules dynamically."""
        logger.info("Loading brain modules...")
        
        # Import common modules that other brains might depend on
        from core.chameleon_skin import scan_environment, morph_identity
        from core.reinforcement_learning import rl_update
        from core.tech_update_monitor import check_external_updates
        
        # Store these in the orchestrator for access by brains
        self.chameleon = {
            "scan_environment": scan_environment,
            "morph_identity": morph_identity
        }
        self.rl = {"update": rl_update}
        self.tech_monitor = {"check_updates": check_external_updates}
        
        # Dynamically load all brain modules
        for _, name, ispkg in pkgutil.iter_modules(brains.__path__):
            if name != '__init__' and name != 'base_brain':
                try:
                    module = importlib.import_module(f'brains.{name}')
                    
                    # Look for main class in the module
                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)
                        if isinstance(attr, type) and attr_name.lower() == name.lower():
                            brain_instance = attr()
                            self.brains[name] = brain_instance
                            logger.debug(f"Loaded brain module: {name}")
                            break
                    else:
                        logger.warning(f"Could not find main class in brain module: {name}")
                        
                except Exception as e:
                    logger.error(f"Error loading brain {name}: {e}")
    
    def start_loop(self):
        """Start the main orchestrator loop."""
        self._running = True
        logger.info("Orchestrator loop starting")
        
        try:
            while self._running:
                self._cycle()
                time.sleep(self.interval)
        except Exception as e:
            logger.error(f"Error in orchestrator loop: {e}")
            self._running = False
    
    def stop_loop(self):
        """Stop the orchestrator loop."""
        self._running = False
        logger.info("Orchestrator loop stopped")
    
    def _cycle(self):
        """Run a single orchestrator cycle."""
        logger.debug("Starting orchestrator cycle")
        
        # Run environment checks
        self.chameleon["scan_environment"]()
        self.chameleon["morph_identity"]()
        
        # Process input for each brain
        for name, brain in self.brains.items():
            try:
                result = brain.process_input("Cycle update")
                logger.debug(f"{name}: {result}")
            except Exception as e:
                logger.error(f"Error in brain {name}: {e}")
        
        # Run reinforcement learning update
        self.rl["update"]()
        
        # Check for external technology updates
        update_info = self.tech_monitor["check_updates"]()
        logger.debug(f"External update check: {update_info}")
    
    def process_user_input(self, user_input):
        """
        Process user input through all relevant brain modules.
        
        Args:
            user_input: String containing user's message
            
        Returns:
            String response to the user
        """
        logger.info(f"Processing user input: {user_input}")
        
        # Store user input in memory
        self.digital_soul.add_memory(
            "interaction", 
            {"role": "user", "content": user_input},
            tags=["interaction", "user_input"]
        )
        
        # Priority brains that should process this input
        priority_brains = ["observer", "archivist", "messenger"]
        responses = []
        
        # Process with priority brains first
        for name in priority_brains:
            if name in self.brains:
                try:
                    response = self.brains[name].process_input(user_input)
                    if response:
                        responses.append(response)
                except Exception as e:
                    logger.error(f"Error processing input with {name}: {e}")
        
        # Then process with other brains
        for name, brain in self.brains.items():
            if name not in priority_brains:
                try:
                    response = brain.process_input(user_input)
                    if response:
                        responses.append(response)
                except Exception as e:
                    logger.error(f"Error processing input with {name}: {e}")
        
        # Let the weaver brain combine responses if available
        if "weaver" in self.brains and responses:
            try:
                final_response = self.brains["weaver"].weave_responses(user_input, responses)
            except Exception as e:
                logger.error(f"Error weaving responses: {e}")
                final_response = " ".join(responses[:2])  # Fallback
        else:
            final_response = responses[0] if responses else "I'm processing that input."
        
        # Store the response in memory
        self.digital_soul.add_memory(
            "interaction", 
            {"role": "assistant", "content": final_response},
            tags=["interaction", "assistant_response"]
        )
        
        return final_response
