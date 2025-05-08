"""
Core Package for Padronique

This package contains the core components of Padronique, including the central
orchestrator that coordinates all modules and functionalities, the ethics engine
that ensures ethical behavior, and the voice module that manages emotional expression.
"""

from core.orchestrator import Orchestrator
from core.ethics_engine import get_ethics_engine, EthicsEngine, ActionSeverity, VerificationType
from core.voice_module import get_voice_module, VoiceModule, EmotionalTone

__all__ = ['Orchestrator', 
           'get_ethics_engine', 'EthicsEngine', 'ActionSeverity', 'VerificationType',
           'get_voice_module', 'VoiceModule', 'EmotionalTone']