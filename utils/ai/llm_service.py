#!/usr/bin/env python3
"""
LLM service abstraction for interacting with different AI service providers.
"""

import os
import json
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Union

logger = logging.getLogger(__name__)

class LLMService(ABC):
    """
    Abstract base class for LLM service providers.
    
    This class defines the common interface for interacting with
    different LLM providers (OpenAI, Anthropic, etc.)
    """
    
    @abstractmethod
    @abstractmethod
    def query(self, prompt: str, max_tokens: int = 1000, 
              temperature: float = 0.7, system_message: Optional[str] = None) -> str:
        """
        Query the LLM with a prompt.
        
        Args:
            prompt: The user prompt
            max_tokens: Maximum number of tokens to generate
            temperature: Temperature for generation (0.0 to 1.0)
            system_message: Optional system message for models that support it
            
        Returns:
            The generated response as a string
        """
        raise NotImplementedError("Subclasses must implement query method")
    
    @abstractmethod
    def embeddings(self, text: str) -> List[float]:
        """
        Generate embeddings for the given text.
        
        Args:
            text: The text to generate embeddings for
            
        Returns:
            The embedding as a list of floats
        """
        pass
    
    @abstractmethod
    def get_info(self) -> Dict[str, Any]:
        """
        Get information about the LLM service.
        
        Returns:
            Dictionary with service information
        """
        pass


class OpenAIService(LLMService):
    """
    OpenAI service implementation.
    """
    
    def __init__(self):
        """Initialize the OpenAI service."""
        try:
            from openai import OpenAI
            
            # Initialize client
            api_key = os.environ.get("OPENAI_API_KEY")
            if not api_key:
                logger.error("OPENAI_API_KEY environment variable not set")
                raise ValueError("OPENAI_API_KEY not set")
                
            self.client = OpenAI(api_key=api_key)
            logger.info("OpenAI service initialized successfully")
            
            # Default model settings
            self.default_model = "gpt-4o"  # The newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            self.embedding_model = "text-embedding-3-large"
        except ImportError:
            logger.error("OpenAI package is not installed")
            raise ImportError("Please install the OpenAI package: pip install openai")
        except Exception as e:
            logger.error(f"Error initializing OpenAI client: {e}")
            raise
    
    def query(self, prompt: str, max_tokens: int = 1000, 
              temperature: float = 0.7, system_message: Optional[str] = None) -> str:
        """
        Query the OpenAI model with a prompt.
        
        Args:
            prompt: The user prompt
            max_tokens: Maximum number of tokens to generate
            temperature: Temperature for generation (0.0 to 1.0)
            system_message: System message to set the context
            
        Returns:
            The generated response as a string
        """
        try:
            messages = []
            
            # Add system message if provided
            if system_message:
                messages.append({"role": "system", "content": system_message})
            
            # Add user prompt
            messages.append({"role": "user", "content": prompt})
            
            # Make the request
            response = self.client.chat.completions.create(
                model=self.default_model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            # Extract and return the response text
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error querying OpenAI: {e}")
            return f"Error: {str(e)}"
    
    def embeddings(self, text: str) -> List[float]:
        """
        Generate embeddings for the given text using OpenAI.
        
        Args:
            text: The text to generate embeddings for
            
        Returns:
            The embedding as a list of floats
        """
        try:
            response = self.client.embeddings.create(
                input=text,
                model=self.embedding_model
            )
            
            # Extract and return the embedding
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Error generating embeddings with OpenAI: {e}")
            raise
    
    def get_info(self) -> Dict[str, Any]:
        """
        Get information about the OpenAI service.
        
        Returns:
            Dictionary with service information
        """
        return {
            "name": "OpenAI",
            "type": "commercial_api",
            "model": self.default_model,
            "embedding_model": self.embedding_model,
            "features": ["text_generation", "embeddings"],
            "requires_api_key": True
        }


def get_llm_service(provider: str = "openai") -> LLMService:
    """
    Factory function to get the appropriate LLM service.
    
    Args:
        provider: The LLM provider to use ("openai", "anthropic", etc.)
        
    Returns:
        An instance of the requested LLM service
    """
    providers = {
        "openai": OpenAIService
    }
    
    if provider not in providers:
        raise ValueError(f"Unsupported LLM provider: {provider}")
    
    return providers[provider]()