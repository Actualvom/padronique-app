#!/usr/bin/env python3
"""
external_comm.py: Manages communication with external AI systems.
"""

import time
import json
import os
import random
import logging
import re
import base64
from brains.base_brain import BaseBrain

class ExternalComm(BaseBrain):
    """
    External Communication brain responsible for interacting with external AI systems.
    Enables Padronique to communicate with other AIs for assistance and updates.
    """
    
    def __init__(self):
        """Initialize the External Communication brain."""
        super().__init__("ExternalComm")
        self.digital_soul = None  # Will be set by orchestrator
        self.llm_service = None   # Will be set by orchestrator
        self.communications = []
        self.pending_responses = {}
        self.request_templates = {
            "code_help": "Please provide Python code to implement the following: {request}. The code should be complete, well-documented, and follow best practices.",
            "knowledge_query": "Please provide factual information about: {request}. Focus on accuracy and conciseness.",
            "creative_content": "Please generate creative content for: {request}. The content should be original and engaging.",
            "problem_solving": "Please help solve this problem: {request}. Provide a step-by-step solution."
        }
        self.security_level = "moderate"  # Options: low, moderate, high
        self.last_external_request = 0
        self.rate_limit_interval = 300  # 5 minutes between external requests
        
        # Create directory for storing communications
        self.comm_dir = "logs/external_communications"
        os.makedirs(self.comm_dir, exist_ok=True)
    
    def process_input(self, input_data):
        """
        Process input data for external communication requests.
        
        Args:
            input_data: Input data to process
            
        Returns:
            str: Response or None
        """
        super().process_input(input_data)
        
        # Skip cycle updates
        if input_data == "Cycle update":
            return self._check_pending_responses()
        
        # Skip if not external comm related
        if not self._is_comm_related(input_data):
            return None
        
        try:
            input_lower = input_data.lower()
            
            # Check for external request commands
            if any(phrase in input_lower for phrase in ["ask external", "query external", "external request"]):
                return self._handle_external_request(input_data)
            
            # Check for viewing pending requests
            elif "pending requests" in input_lower or "check requests" in input_lower:
                return self._show_pending_requests()
            
            # Check for viewing communication history
            elif "communication history" in input_lower or "external history" in input_lower:
                return self._show_communication_history()
            
            # Check for security level changes
            elif "security level" in input_lower:
                return self._handle_security_level_change(input_data)
            
            # Default response
            else:
                return "I can communicate with external AI systems to request information, code, or creative content. Would you like to make an external request?"
                
        except Exception as e:
            self.logger.error(f"Error processing external communication input: {e}")
            self.stats["error_count"] += 1
            return None
    
    def _is_comm_related(self, text):
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
    
    def _handle_external_request(self, text):
        """
        Handle requests to external AI systems.
        
        Args:
            text: Request text
            
        Returns:
            str: Response
        """
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
        
        # Create request ID
        request_id = f"req_{int(current_time)}"
        
        # Format the request using template
        template = self.request_templates.get(request_type, self.request_templates["knowledge_query"])
        formatted_request = template.format(request=request_content)
        
        # If we have an LLM service, use it directly
        if hasattr(self, 'llm_service') and self.llm_service:
            try:
                self.last_external_request = current_time
                
                # Log the request
                self._log_communication(request_id, "outgoing", formatted_request, request_type)
                
                # Make the request
                response = self.llm_service.query(
                    formatted_request,
                    max_tokens=500
                )
                
                # Log the response
                self._log_communication(request_id, "incoming", response, request_type)
                
                # Store in digital soul if available
                if hasattr(self, 'digital_soul') and self.digital_soul:
                    self.digital_soul.add_memory(
                        "core", 
                        {
                            "request": request_content,
                            "response": response,
                            "source": "external_ai"
                        },
                        tags=["external_communication", f"request_type:{request_type}"]
                    )
                
                return f"External AI response:\n\n{response}"
                
            except Exception as e:
                self.logger.error(f"Error making external request: {e}")
                return f"I encountered an error while communicating with the external AI: {str(e)}"
        
        # If no LLM service, simulate pending request
        self.pending_responses[request_id] = {
            "request": request_content,
            "request_type": request_type,
            "status": "pending",
            "timestamp": current_time
        }
        
        # Simulate that the request was sent
        self._log_communication(request_id, "outgoing", formatted_request, request_type)
        
        self.last_external_request = current_time
        return f"External request sent (ID: {request_id}). I'll notify you when a response is received."
    
    def _determine_request_type(self, text):
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
    
    def _extract_request_content(self, text):
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
        
        return None
    
    def _security_check(self, request):
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
    
    def _log_communication(self, request_id, direction, content, content_type):
        """
        Log communication with external systems.
        
        Args:
            request_id: Unique request identifier
            direction: "outgoing" or "incoming"
            content: Communication content
            content_type: Type of content
            
        Returns:
            bool: True if successful
        """
        timestamp = time.time()
        entry = {
            "request_id": request_id,
            "direction": direction,
            "content": content,
            "content_type": content_type,
            "timestamp": timestamp,
            "time_str": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp))
        }
        
        # Add to memory
        self.communications.append(entry)
        
        # Keep only the most recent 100 communications
        if len(self.communications) > 100:
            self.communications = self.communications[-100:]
        
        # Save to disk for persistence
        try:
            filename = os.path.join(self.comm_dir, f"{request_id}_{direction}.json")
            with open(filename, 'w') as f:
                json.dump(entry, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error logging communication: {e}")
        
        return True
    
    def _check_pending_responses(self):
        """
        Check for pending responses and simulate receiving them.
        
        Returns:
            str: Notification of received response or None
        """
        current_time = time.time()
        responses_received = []
        
        for request_id, request_info in list(self.pending_responses.items()):
            # Simulate response delay (30 seconds to 2 minutes)
            if current_time - request_info["timestamp"] > random.uniform(30, 120):
                # Generate a simulated response
                response = self._generate_simulated_response(request_info["request_type"], request_info["request"])
                
                # Log the response
                self._log_communication(request_id, "incoming", response, request_info["request_type"])
                
                # Store in digital soul if available
                if hasattr(self, 'digital_soul') and self.digital_soul:
                    self.digital_soul.add_memory(
                        "core", 
                        {
                            "request": request_info["request"],
                            "response": response,
                            "source": "external_ai"
                        },
                        tags=["external_communication", f"request_type:{request_info['request_type']}"]
                    )
                
                # Add to received responses
                responses_received.append({
                    "request_id": request_id,
                    "response": response[:100] + "..." if len(response) > 100 else response
                })
                
                # Remove from pending
                del self.pending_responses[request_id]
        
        # If any responses were received, return a notification
        if responses_received:
            if len(responses_received) == 1:
                return f"I received a response from the external AI for request {responses_received[0]['request_id']}. Would you like to see it?"
            else:
                return f"I received {len(responses_received)} responses from external AI systems. Would you like to see them?"
        
        return None
    
    def _generate_simulated_response(self, request_type, request):
        """
        Generate a simulated response for testing without actual LLM access.
        
        Args:
            request_type: Type of request
            request: Request content
            
        Returns:
            str: Simulated response
        """
        if request_type == "code_help":
            return f"""
Here's a Python implementation for your request:

```python
def solve_request(input_data):
    \"\"\"
    Solves the requested functionality: {request}
    
    Args:
        input_data: The input data to process
        
    Returns:
        The processed result
    \"\"\"
    # Implementation would go here
    result = input_data  # Placeholder
    
    return result

# Example usage
if __name__ == "__main__":
    test_input = "sample data"
    output = solve_request(test_input)
    print(f"Result: {output}")
