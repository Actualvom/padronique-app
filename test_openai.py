#!/usr/bin/env python3
"""
Test script for verifying OpenAI integration.

This script tests the OpenAI integration by initializing the service and 
making a simple query.
"""

import os
import logging
import sys
from utils.ai import get_llm_service

# Configure basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_openai_integration():
    """Test the OpenAI integration."""
    logger.info("Testing OpenAI integration")
    
    # Check for API key
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        logger.error("OPENAI_API_KEY environment variable not set")
        return False
    
    try:
        # Initialize the OpenAI service
        llm_service = get_llm_service("openai")
        logger.info("OpenAI service initialized successfully")
        
        # Get service info
        service_info = llm_service.get_info()
        logger.info(f"Service info: {service_info}")
        
        # Test a simple query
        test_prompt = "What is the capital of France? Keep your answer very brief."
        logger.info(f"Sending test query: '{test_prompt}'")
        
        response = llm_service.query(test_prompt)
        logger.info(f"Response received: '{response}'")
        
        # Test embeddings
        test_text = "This is a test sentence for embeddings."
        logger.info(f"Generating embeddings for: '{test_text}'")
        
        embeddings = llm_service.embeddings(test_text)
        logger.info(f"Generated {len(embeddings)} embedding dimensions")
        logger.info(f"First 5 dimensions: {embeddings[:5]}")
        
        logger.info("All tests completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Error testing OpenAI integration: {e}")
        return False

if __name__ == "__main__":
    success = test_openai_integration()
    sys.exit(0 if success else 1)