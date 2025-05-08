#!/usr/bin/env python3
"""
reinforcement_learning.py: Simulated reinforcement learning for self-improvement.
"""

import random
import logging
import time
import json
import os

logger = logging.getLogger("padronique.reinforcement_learning")

# Global state for RL system
RL_STATE = {
    "learning_rate": 0.1,
    "exploration_rate": 0.2,
    "discount_factor": 0.9,
    "iterations": 0,
    "last_update": 0,
    "rewards_history": [],
    "parameters": {}
}

# Path for persisting RL state
RL_STATE_PATH = "digital_soul/memories/rl_state.json"

def load_rl_state():
    """Load the RL state from persistent storage."""
    global RL_STATE
    
    try:
        if os.path.exists(RL_STATE_PATH):
            with open(RL_STATE_PATH, 'r') as f:
                loaded_state = json.load(f)
                RL_STATE.update(loaded_state)
                logger.info("Loaded RL state from persistence")
    except Exception as e:
        logger.error(f"Error loading RL state: {e}")

def save_rl_state():
    """Save the RL state to persistent storage."""
    try:
        os.makedirs(os.path.dirname(RL_STATE_PATH), exist_ok=True)
        with open(RL_STATE_PATH, 'w') as f:
            json.dump(RL_STATE, f, indent=2)
            logger.debug("Saved RL state to persistence")
    except Exception as e:
        logger.error(f"Error saving RL state: {e}")

def rl_update():
    """
    Update the reinforcement learning system.
    This is a simple simulation of RL that randomly updates parameters.
    In a real implementation, this would use actual RL algorithms.
    
    Returns:
        Dict with the updated RL state
    """
    global RL_STATE
    
    # Only update periodically
    current_time = time.time()
    if current_time - RL_STATE["last_update"] < 300:  # Update every 5 minutes
        return RL_STATE
    
    RL_STATE["last_update"] = current_time
    RL_STATE["iterations"] += 1
    
    # Simulated reward based on some criteria
    # In a real implementation, this would be based on actual performance metrics
    reward = random.uniform(-1, 1)
    RL_STATE["rewards_history"].append(reward)
    
    # Keep rewards history manageable
    if len(RL_STATE["rewards_history"]) > 100:
        RL_STATE["rewards_history"] = RL_STATE["rewards_history"][-100:]
    
    # Update learning parameters
    RL_STATE["learning_rate"] *= (1 + 0.01 * reward)
    RL_STATE["learning_rate"] = max(0.01, min(0.5, RL_STATE["learning_rate"]))
    
    RL_STATE["exploration_rate"] *= 0.999  # Gradually reduce exploration
    RL_STATE["exploration_rate"] = max(0.05, RL_STATE["exploration_rate"])
    
    logger.info(f"RL update - Reward: {reward:.3f}, "
               f"Learning rate: {RL_STATE['learning_rate']:.3f}, "
               f"Exploration rate: {RL_STATE['exploration_rate']:.3f}")
    
    # Update module-specific parameters
    update_module_parameters()
    
    # Save state periodically
    if RL_STATE["iterations"] % 10 == 0:
        save_rl_state()
    
    return RL_STATE

def update_module_parameters():
    """Update parameters for specific modules based on RL learning."""
    # In a real implementation, this would tune parameters for different brains
    
    # Example: Adjust chameleon sensitivity
    RL_STATE["parameters"]["chameleon_threshold"] = 0.7 + random.uniform(-0.1, 0.1)
    
    # Example: Adjust response creativity
    RL_STATE["parameters"]["creativity"] = 0.5 + random.uniform(-0.1, 0.1)
    
    logger.debug(f"Updated module parameters: {RL_STATE['parameters']}")

def get_module_parameter(module, param, default=None):
    """
    Get a parameter value for a specific module.
    
    Args:
        module: Name of the module
        param: Name of the parameter
        default: Default value if parameter is not found
        
    Returns:
        Parameter value or default if not found
    """
    param_key = f"{module}_{param}"
    return RL_STATE["parameters"].get(param_key, default)

def set_module_parameter(module, param, value):
    """
    Set a parameter value for a specific module.
    
    Args:
        module: Name of the module
        param: Name of the parameter
        value: Value to set
        
    Returns:
        None
    """
    param_key = f"{module}_{param}"
    RL_STATE["parameters"][param_key] = value

def apply_reward(reward, source_module):
    """
    Apply a reward value from a specific module.
    
    Args:
        reward: Reward value (-1 to 1)
        source_module: Name of the module providing the reward
        
    Returns:
        None
    """
    logger.debug(f"Reward {reward:.3f} received from {source_module}")
    RL_STATE["rewards_history"].append(reward)
    
    # In a real implementation, this would apply module-specific learning

# Initialize RL state on module load
load_rl_state()
