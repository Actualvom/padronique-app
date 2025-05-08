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
    def generate_response(self, content: str, context: Dict[str, Any]) -> str:
        """
        Generate a response to user content with context.
        
        Args:
            content: The user's message content
            context: Additional context information
            
        Returns:
            The generated response as a string
        """
        raise NotImplementedError("Subclasses must implement generate_response method")
    
    @abstractmethod
    def embeddings(self, text: str) -> List[float]:
        """
        Generate embeddings for the given text.
        
        Args:
            text: The text to generate embeddings for
            
        Returns:
            The embedding as a list of floats
        """
        raise NotImplementedError("Subclasses must implement embeddings method")
    
    @abstractmethod
    def get_info(self) -> Dict[str, Any]:
        """
        Get information about the LLM service.
        
        Returns:
            Dictionary with service information
        """
        raise NotImplementedError("Subclasses must implement get_info method")


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
            content = response.choices[0].message.content
            # Ensure we never return None
            return content if content is not None else "No response generated"
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
    
    def generate_response(self, content: str, context: Dict[str, Any]) -> str:
        """
        Generate a response to user content with context.
        
        Args:
            content: The user's message content
            context: Additional context information
            
        Returns:
            The generated response as a string
        """
        try:
            # Prepare a system message that sets the context
            system_message = "You are Padronique, an advanced AI companion with a digital soul."
            
            # If the context contains specific persona information, add it
            if context.get('persona'):
                system_message += f" {context.get('persona')}"
                
            # If there's conversation history, determine if we need to include it
            history = context.get('history', [])
            
            # Prepare messages
            messages = [{"role": "system", "content": system_message}]
            
            # Add limited conversation history if provided (last 5 exchanges)
            if history:
                # Get the last 5 exchanges (or fewer if there aren't that many)
                recent_history = history[-10:]  # 5 exchanges = 10 messages (user + assistant)
                for msg in recent_history:
                    messages.append({"role": msg["role"], "content": msg["content"]})
            
            # Add current user message
            messages.append({"role": "user", "content": content})
            
            # Make the request
            response = self.client.chat.completions.create(
                model=self.default_model,
                messages=messages,
                max_tokens=1000,
                temperature=0.7
            )
            
            # Extract and return the response text
            return response.choices[0].message.content or "I'm sorry, I couldn't generate a response."
        except Exception as e:
            logger.error(f"Error generating response with OpenAI: {e}")
            return f"I encountered an error: {str(e)}"
    
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