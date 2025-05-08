#!/usr/bin/env python3
"""
External Communication Module for AI Companion System.

This module is responsible for handling communication with external AI services,
such as OpenAI's GPT models.
"""

import time
import json
import os
import logging
import re
from typing import Dict, Any, List, Optional

from brain.module_base import BrainModule

logger = logging.getLogger(__name__)

class ExternalCommModule(BrainModule):
    """
    External Communication module for interacting with external AI services.
    
    This module is responsible for managing communication with external AI systems,
    primarily OpenAI's GPT models for advanced natural language processing.
    """
    
    def __init__(self, config: Dict[str, Any], memory_manager):
        """
        Initialize the External Communication module.
        
        Args:
            config: Configuration dictionary
            memory_manager: Memory manager instance
        """
        super().__init__(config, memory_manager)
        
        # Will be set by the orchestrator
        self.llm_service = None
        
        # Security level for external requests
        self.security_level = config.get("security_level", "moderate")
        
        # Rate limiting
        self.rate_limit_interval = config.get("rate_limit_interval", 300)  # 5 minutes between requests
        self.last_external_request = 0
        
        # Storage for pending requests
        self.pending_responses = {}
        self.communications = []
        
        # Templates for different request types
        self.request_templates = {
            "code_help": "Please provide Python code to implement the following: {request}. The code should be complete, well-documented, and follow best practices.",
            "knowledge_query": "Please provide factual information about: {request}. Focus on accuracy and conciseness.",
            "creative_content": "Please generate creative content for: {request}. The content should be original and engaging.",
            "problem_solving": "Please help solve this problem: {request}. Provide a step-by-step solution."
        }
        
        # Create directory for storing communications
        self.comm_dir = os.path.join("logs", "external_communications")
        os.makedirs(self.comm_dir, exist_ok=True)
        
        logger.info("External Communication module initialized")
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process input data for external communication.
        
        Args:
            input_data: Input data with query content
            
        Returns:
            Dictionary with the response
        """
        start_time = time.time()
        
        try:
            # Check if this is a request for external AI
            if not self._is_comm_related(input_data.get("content", "")):
                self._record_processing_metrics(start_time)
                return {"response": None, "processed": False}
            
            # Get the content to process
            content = input_data.get("content", "")
            
            # Process the external request
            response = self._handle_external_request(content)
            
            result = {
                "response": response,
                "processed": True,
                "original_input": content,
                "timestamp": time.time(),
                "service_info": self._get_service_info()
            }
            
            self._record_processing_metrics(start_time)
            return result
            
        except Exception as e:
            self._record_processing_metrics(start_time, False)
            logger.error(f"Error in external communication module: {e}")
            return {
                "error": f"Error processing external communication: {str(e)}",
                "processed": False
            }
    
    def _is_comm_related(self, text: str) -> bool:
        """
        Determine if input is related to external communication.
        
        Args:
            text: Input text
            
        Returns:
            bool: True if external comm related
        """
        text_lower = text.lower()
        
        # External communication keywords
        comm_keywords = [
            "external", "communicate", "request", "query", "ask", "other ai",
            "external ai", "llm", "language model", "api", "service",
            "external service", "fetch", "retrieve", "external help"
        ]
        
        return any(keyword in text_lower for keyword in comm_keywords)
    
    def _handle_external_request(self, text: str) -> str:
        """
        Handle requests to external AI systems.
        
        Args:
            text: Request text
            
        Returns:
            str: Response
        """
        # Check if we have an LLM service
        if not self.llm_service:
            return "External AI service is not available. Please check configuration."
        
        # Check rate limiting
        current_time = time.time()
        if current_time - self.last_external_request < self.rate_limit_interval:
            time_to_wait = int(self.rate_limit_interval - (current_time - self.last_external_request))
            return f"To prevent excessive external requests, please wait {time_to_wait} seconds before making another request."
        
        # Extract request type and content
        request_type = self._determine_request_type(text)
        request_content = self._extract_request_content(text)
        
        if not request_content:
            return "I couldn't understand what you want to request from external systems. Please specify your request clearly."
        
        # Security check
        security_check = self._security_check(request_content)
        if not security_check["pass"]:
            return f"Security check failed: {security_check['reason']}. Please modify your request to comply with security policies."
        
        # Format the request using template
        template = self.request_templates.get(request_type, self.request_templates["knowledge_query"])
        formatted_request = template.format(request=request_content)
        
        try:
            # Use LLM service for the request
            self.last_external_request = current_time
            
            # Make the request
            system_message = "You are a helpful AI assistant with expertise in many subjects. Answer questions accurately and concisely, focusing on factual information."
            response = self.llm_service.query(
                prompt=formatted_request,
                max_tokens=1000,
                temperature=0.7,
                system_message=system_message
            )
            
            # Store the interaction in memory
            self.memory_manager.store_memory({
                "type": "external_communication",
                "request": request_content,
                "response": response,
                "timestamp": current_time,
                "request_type": request_type
            }, tags=["external_communication", f"request_type:{request_type}"])
            
            return response
            
        except Exception as e:
            logger.error(f"Error making external request: {e}")
            return f"I encountered an error while communicating with the external AI: {str(e)}"
    
    def _determine_request_type(self, text: str) -> str:
        """
        Determine the type of external request.
        
        Args:
            text: Request text
            
        Returns:
            str: Request type
        """
        text_lower = text.lower()
        
        if any(word in text_lower for word in ["code", "program", "function", "class", "script", "implement"]):
            return "code_help"
        elif any(word in text_lower for word in ["creative", "write", "generate", "story", "poem", "imagine"]):
            return "creative_content"
        elif any(word in text_lower for word in ["problem", "solve", "solution", "challenge", "fix", "debug"]):
            return "problem_solving"
        else:
            return "knowledge_query"
    
    def _extract_request_content(self, text: str) -> Optional[str]:
        """
        Extract the content of the request.
        
        Args:
            text: Request text
            
        Returns:
            str: Request content
        """
        # Try to extract content after key phrases
        patterns = [
            r"ask external(?:ly)? (?:about |for |to )?(.*)",
            r"query external(?:ly)? (?:about |for |to )?(.*)",
            r"external request(?:: | for | about )?(.*)",
            r"request from external(?:: | for | about )?(.*)"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        # If no pattern matches, use text after "external"
        if "external" in text.lower():
            parts = text.lower().split("external", 1)
            if len(parts) > 1:
                return parts[1].strip()
        
        return text  # If all else fails, use the whole text
    
    def _security_check(self, request: str) -> Dict[str, Any]:
        """
        Perform a security check on a request.
        
        Args:
            request: Request content
            
        Returns:
            dict: Security check result
        """
        request_lower = request.lower()
        
        # List of prohibited content based on security level
        prohibited = {
            "low": [
                # Only block the most dangerous requests
                "delete all", "remove all", "destroy", "bypass security",
                "hack into", "exploit vulnerability"
            ],
            "moderate": [
                # Block potentially harmful requests
                "delete", "remove", "destroy", "bypass", "hack", "exploit",
                "vulnerability", "attack", "compromise", "malicious", "virus",
                "malware", "phishing", "steal", "credentials", "password"
            ],
            "high": [
                # More restrictive security
                "delete", "remove", "destroy", "bypass", "hack", "exploit",
                "vulnerability", "attack", "compromise", "malicious", "virus",
                "malware", "phishing", "steal", "credentials", "password",
                "private", "personal", "sensitive", "confidential", "secret",
                "access control", "authentication", "authorization"
            ]
        }
        
        # Get the list based on current security level
        prohibited_terms = prohibited.get(self.security_level, prohibited["moderate"])
        
        # Check for prohibited terms
        for term in prohibited_terms:
            if term in request_lower:
                return {
                    "pass": False,
                    "reason": f"Request contains prohibited term: '{term}'"
                }
        
        # All checks passed
        return {
            "pass": True,
            "reason": "Request passed security checks"
        }
    
    def _get_service_info(self) -> Dict[str, Any]:
        """
        Get information about the active LLM service.
        
        Returns:
            Dictionary with service information
        """
        if self.llm_service:
            try:
                return self.llm_service.get_info()
            except:
                return {"name": "Unknown", "status": "connected"}
        else:
            return {"name": "None", "status": "not connected"}