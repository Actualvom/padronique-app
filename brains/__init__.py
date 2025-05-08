"""
Brains Package for Padronique

This package contains the specialized brain modules that provide Padronique's 
cognitive capabilities, including learning, protection, autonomous operation,
and other specialized functions.
"""

from brains.learning_module import get_learning_module, LearningType, LearningPriority
from brains.protection_module import get_protection_module, ThreatType, ThreatLevel
from brains.automaton_module import get_automaton_module, Goal, ActionPriority, ActionStatus

__all__ = [
    'get_learning_module', 'LearningType', 'LearningPriority',
    'get_protection_module', 'ThreatType', 'ThreatLevel',
    'get_automaton_module', 'Goal', 'ActionPriority', 'ActionStatus'
]