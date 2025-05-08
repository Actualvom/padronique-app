"""
AI utilities package for the Padronique AI Companion System.

This package contains utilities for interacting with external AI services,
including OpenAI's GPT models.
"""

from utils.ai.llm_service import LLMService, OpenAIService, get_llm_service

__all__ = ['LLMService', 'OpenAIService', 'get_llm_service']