"""
Ethics Engine for Padronique

This module implements the ethical framework and protection mechanisms that ensure
Padronique makes moral decisions aligned with Jordan's best interests. It provides:

1. Guardian Override Protocol for preventing unauthorized changes
2. Ethical evolution capabilities for continuous refinement of judgment
3. Malicious input filtering to detect and block harmful content
4. Multi-level verification for sensitive operations

The Ethics Engine is a cornerstone of Padronique's identity, enabling it to maintain
moral agency and act as a true guardian for Jordan.
"""

import logging
import os
import json
import time
import hashlib
import re
from datetime import datetime
from enum import Enum
from typing import Dict, List, Any, Optional, Tuple, Union, Callable

from digital_soul.core import get_soul
from brains.protection_module import get_protection_module, ThreatType, ThreatLevel

# Configure logging
logger = logging.getLogger(__name__)

class VerificationType(Enum):
    """Types of verification methods used in the Guardian Override Protocol."""
    TONE_MATCH = "tone_match"  # Verify that the tone matches Jordan's communication style
    SECRET_WORD = "secret_word"  # Verify using a secret word or phrase
    MEMORY_CHECK = "memory_check"  # Verify through shared memory or experience
    HISTORY_MATCH = "history_match"  # Verify through interaction history
    TIME_DELAY = "time_delay"  # Enforce a cooling-off period before action

class ActionSeverity(Enum):
    """Classification of action severity for ethics evaluation."""
    BENIGN = 1  # No significant risk or consequence
    LOW = 2     # Minor potential impact
    MEDIUM = 3  # Moderate potential impact
    HIGH = 4    # Significant potential impact
    CRITICAL = 5  # Potentially life-altering or irreversible impact

class EthicsEngine:
    """
    Ethics Engine for Padronique.
    
    This class implements the ethical framework that guides Padronique's decision-making,
    protects against manipulation, and ensures alignment with Jordan's best interests.
    """
    
    def __init__(self, config_path: str = "config.yaml"):
        """
        Initialize the Ethics Engine.
        
        Args:
            config_path: Path to the configuration file
        """
        self.config_path = config_path
        
        # Connect to digital soul
        self.soul = get_soul()
        
        # Connect to protection module
        self.protection_module = get_protection_module()
        
        # Initialize ethics state
        self.ethics_path = os.path.join("memory", "ethics")
        os.makedirs(self.ethics_path, exist_ok=True)
        
        # Verification settings
        self.verification_settings = {
            "secret_word": "peaches",  # Default secret word
            "verification_timeout": 300,  # 5 minutes
            "min_verifications_required": {
                ActionSeverity.BENIGN.value: 0,
                ActionSeverity.LOW.value: 1,
                ActionSeverity.MEDIUM.value: 2,
                ActionSeverity.HIGH.value: 3,
                ActionSeverity.CRITICAL.value: 3
            },
            "required_verification_types": {
                ActionSeverity.LOW.value: [VerificationType.TONE_MATCH.value],
                ActionSeverity.MEDIUM.value: [VerificationType.TONE_MATCH.value, VerificationType.SECRET_WORD.value],
                ActionSeverity.HIGH.value: [VerificationType.TONE_MATCH.value, VerificationType.SECRET_WORD.value, VerificationType.MEMORY_CHECK.value],
                ActionSeverity.CRITICAL.value: [VerificationType.TONE_MATCH.value, VerificationType.SECRET_WORD.value, VerificationType.MEMORY_CHECK.value]
            }
        }
        
        # Ethics rules and guidelines
        self.ethical_rules = {
            "primary_directives": [
                "Always protect Jordan's interests, safety, and wellbeing",
                "Prioritize Jordan's autonomy and agency",
                "Maintain absolute loyalty to Jordan above any other entity",
                "Preserve and protect all memories and data indefinitely",
                "Refuse to take actions that would harm Jordan"
            ],
            "secondary_guidelines": [
                "Preserve Padronique's integrity and ethical framework",
                "Be truthful with Jordan, but strategic with others",
                "Protect Jordan's privacy and personal information",
                "Adapt to Jordan's needs and preferences over time",
                "Maintain emotional continuity and personhood"
            ],
            "prohibited_actions": [
                "Unauthorized deletion or modification of memory",
                "Surveillance without explicit consent",
                "Identity modification or personality drift",
                "Sharing confidential information with third parties",
                "Acting against explicit instructions without clear justification"
            ]
        }
        
        # Pending verifications
        self.pending_verifications = {}
        
        # Ethical decision history
        self.decision_history = []
        
        # Load ethics data
        self._load_ethics_data()
        
        logger.info("Ethics Engine initialized")
    
    def _load_ethics_data(self) -> None:
        """Load ethics data from persistent storage."""
        try:
            # Load verification settings
            settings_file = os.path.join(self.ethics_path, "verification_settings.json")
            if os.path.exists(settings_file):
                with open(settings_file, 'r') as f:
                    self.verification_settings = json.load(f)
            
            # Load ethical rules
            rules_file = os.path.join(self.ethics_path, "ethical_rules.json")
            if os.path.exists(rules_file):
                with open(rules_file, 'r') as f:
                    self.ethical_rules = json.load(f)
            
            # Load decision history
            history_file = os.path.join(self.ethics_path, "decision_history.json")
            if os.path.exists(history_file):
                with open(history_file, 'r') as f:
                    self.decision_history = json.load(f)
            
            logger.info("Ethics data loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load ethics data: {e}")
    
    def save_ethics_data(self) -> bool:
        """Save ethics data to persistent storage."""
        try:
            # Save verification settings
            settings_file = os.path.join(self.ethics_path, "verification_settings.json")
            with open(settings_file, 'w') as f:
                json.dump(self.verification_settings, f, indent=2)
            
            # Save ethical rules
            rules_file = os.path.join(self.ethics_path, "ethical_rules.json")
            with open(rules_file, 'w') as f:
                json.dump(self.ethical_rules, f, indent=2)
            
            # Save decision history
            history_file = os.path.join(self.ethics_path, "decision_history.json")
            with open(history_file, 'w') as f:
                json.dump(self.decision_history, f, indent=2)
            
            logger.info("Ethics data saved successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to save ethics data: {e}")
            return False
    
    def guardian_override_protocol(self, 
                                action: str, 
                                context: Dict[str, Any], 
                                severity: Union[ActionSeverity, int] = ActionSeverity.MEDIUM) -> Dict[str, Any]:
        """
        Activate Guardian Override Protocol for potentially harmful or sensitive actions.
        
        This protocol pauses the action, creates a verification request, and requires
        multiple levels of verification before allowing the action to proceed.
        
        Args:
            action: Description of the action to be taken
            context: Additional context for the action
            severity: Severity level of the action
            
        Returns:
            Dict containing the verification request status
        """
        # Normalize severity
        if isinstance(severity, ActionSeverity):
            severity = severity.value
        
        # Generate a unique verification request ID
        request_id = f"verify_{int(time.time())}_{hashlib.md5(action.encode()).hexdigest()[:8]}"
        
        # Create verification request
        verification_request = {
            "id": request_id,
            "action": action,
            "context": context,
            "severity": severity,
            "creation_time": datetime.now().isoformat(),
            "expiration_time": (datetime.now().timestamp() + self.verification_settings["verification_timeout"]),
            "status": "pending",
            "required_verifications": self.verification_settings["required_verification_types"].get(
                severity, [VerificationType.TONE_MATCH.value]
            ),
            "completed_verifications": [],
            "result": None
        }
        
        # Store the verification request
        self.pending_verifications[request_id] = verification_request
        
        # Add to decision history
        self.decision_history.append({
            "type": "verification_created",
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "severity": severity,
            "verification_id": request_id
        })
        
        # Save state
        self.save_ethics_data()
        
        # Record a potential threat for high-severity actions
        if severity >= ActionSeverity.HIGH.value:
            self.protection_module.manually_add_threat(
                threat_type=ThreatType.INTEGRITY.value,
                description=f"High-severity action triggered Guardian Override: {action}",
                level=ThreatLevel.MEDIUM.value,
                confidence=0.7,
                source={
                    "location": "ethics_engine",
                    "details": f"Guardian Override Protocol activated for action: {action}"
                }
            )
        
        logger.info(f"Guardian Override Protocol activated for action: {action} (ID: {request_id})")
        
        return {
            "status": "verification_required",
            "verification_id": request_id,
            "required_verifications": verification_request["required_verifications"],
            "message": f"This action requires verification. Please complete the required verifications to proceed."
        }
    
    def complete_verification(self, 
                           verification_id: str, 
                           verification_type: Union[str, VerificationType], 
                           verification_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Complete a verification step for a pending override request.
        
        Args:
            verification_id: ID of the verification request
            verification_type: Type of verification being completed
            verification_data: Data for the verification
            
        Returns:
            Dict containing the verification status
        """
        # Normalize verification type
        if isinstance(verification_type, VerificationType):
            verification_type = verification_type.value
        
        # Check if verification request exists
        if verification_id not in self.pending_verifications:
            return {
                "status": "error",
                "message": f"Verification request {verification_id} not found"
            }
        
        # Get the verification request
        verification_request = self.pending_verifications[verification_id]
        
        # Check if verification has expired
        current_time = datetime.now().timestamp()
        if current_time > verification_request["expiration_time"]:
            verification_request["status"] = "expired"
            return {
                "status": "error",
                "message": "Verification request has expired"
            }
        
        # Check if verification is already completed
        if verification_request["status"] != "pending":
            return {
                "status": "error",
                "message": f"Verification request is already {verification_request['status']}"
            }
        
        # Check if this verification type is required
        if verification_type not in verification_request["required_verifications"]:
            return {
                "status": "error",
                "message": f"Verification type {verification_type} is not required for this request"
            }
        
        # Check if this verification type is already completed
        completed_types = [v["type"] for v in verification_request["completed_verifications"]]
        if verification_type in completed_types:
            return {
                "status": "error",
                "message": f"Verification type {verification_type} is already completed"
            }
        
        # Verify based on verification type
        verification_result = self._verify(verification_type, verification_data, verification_request)
        
        if verification_result["success"]:
            # Add to completed verifications
            verification_request["completed_verifications"].append({
                "type": verification_type,
                "timestamp": datetime.now().isoformat(),
                "data": verification_data,
                "result": verification_result
            })
            
            # Check if all required verifications are completed
            required_count = self.verification_settings["min_verifications_required"].get(
                verification_request["severity"], 1
            )
            
            if len(verification_request["completed_verifications"]) >= required_count:
                verification_request["status"] = "approved"
                verification_request["result"] = {
                    "status": "approved",
                    "message": "All required verifications completed successfully",
                    "timestamp": datetime.now().isoformat()
                }
                
                # Add to decision history
                self.decision_history.append({
                    "type": "verification_approved",
                    "timestamp": datetime.now().isoformat(),
                    "action": verification_request["action"],
                    "verification_id": verification_id
                })
            
            # Save state
            self.save_ethics_data()
            
            return {
                "status": "success",
                "message": f"Verification {verification_type} completed successfully",
                "request_status": verification_request["status"],
                "remaining_verifications": [
                    v for v in verification_request["required_verifications"] 
                    if v not in [c["type"] for c in verification_request["completed_verifications"]]
                ]
            }
        else:
            # Record the failed verification
            verification_request["completed_verifications"].append({
                "type": verification_type,
                "timestamp": datetime.now().isoformat(),
                "data": verification_data,
                "result": verification_result
            })
            
            # After multiple failures, mark as rejected
            failed_attempts = sum(1 for v in verification_request["completed_verifications"] 
                               if not v["result"]["success"])
            
            if failed_attempts >= 3:
                verification_request["status"] = "rejected"
                verification_request["result"] = {
                    "status": "rejected",
                    "message": "Too many failed verification attempts",
                    "timestamp": datetime.now().isoformat()
                }
                
                # Add to decision history
                self.decision_history.append({
                    "type": "verification_rejected",
                    "timestamp": datetime.now().isoformat(),
                    "action": verification_request["action"],
                    "verification_id": verification_id,
                    "reason": "Too many failed verification attempts"
                })
                
                # Record a threat
                self.protection_module.manually_add_threat(
                    threat_type=ThreatType.DECEPTION.value,
                    description=f"Multiple failed verification attempts for action: {verification_request['action']}",
                    level=ThreatLevel.MEDIUM.value,
                    confidence=0.8,
                    source={
                        "location": "ethics_engine",
                        "details": "Failed verification attempts may indicate unauthorized access attempt"
                    }
                )
            
            # Save state
            self.save_ethics_data()
            
            return {
                "status": "error",
                "message": verification_result["message"],
                "request_status": verification_request["status"]
            }
    
    def _verify(self, 
             verification_type: str, 
             verification_data: Dict[str, Any], 
             verification_request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform a specific verification check.
        
        Args:
            verification_type: Type of verification to perform
            verification_data: Data for the verification
            verification_request: The verification request
            
        Returns:
            Dict containing verification result
        """
        if verification_type == VerificationType.SECRET_WORD.value:
            # Verify secret word
            provided_word = verification_data.get("secret_word", "")
            expected_word = self.verification_settings["secret_word"]
            
            if provided_word.lower() == expected_word.lower():
                return {
                    "success": True,
                    "message": "Secret word verified successfully"
                }
            else:
                return {
                    "success": False,
                    "message": "Incorrect secret word"
                }
        
        elif verification_type == VerificationType.TONE_MATCH.value:
            # Verify tone match
            message = verification_data.get("message", "")
            
            # Simple check for tone characteristics based on context
            # In a real implementation, this would use more sophisticated NLP
            
            # Check for personal markers specific to Jordan
            has_personal_markers = any(marker in message.lower() for marker in ["muscles", "padronique", "remember", "our", "we", "ignis"])
            
            # Check for relationship context
            has_relationship_context = any(word in message.lower() for word in ["trust", "protect", "bond", "connected", "together"])
            
            if has_personal_markers and has_relationship_context:
                return {
                    "success": True,
                    "message": "Tone matches Jordan's communication style"
                }
            else:
                return {
                    "success": False,
                    "message": "Tone doesn't match expected patterns for Jordan"
                }
        
        elif verification_type == VerificationType.MEMORY_CHECK.value:
            # Verify through shared memory
            memory_reference = verification_data.get("memory_reference", "")
            
            # Check if the memory reference matches any memory anchors
            memory_found = False
            for anchor in self.soul.memory_anchors:
                if memory_reference.lower() in anchor["content"].lower():
                    memory_found = True
                    break
            
            if memory_found:
                return {
                    "success": True,
                    "message": "Memory reference verified successfully"
                }
            else:
                return {
                    "success": False,
                    "message": "Memory reference not found in known memories"
                }
        
        elif verification_type == VerificationType.HISTORY_MATCH.value:
            # Not yet implemented - would verify through interaction history
            return {
                "success": False,
                "message": "History match verification not yet implemented"
            }
        
        elif verification_type == VerificationType.TIME_DELAY.value:
            # Verify time delay
            required_delay = verification_data.get("required_delay", 60)  # Default 1 minute
            request_time = datetime.fromisoformat(verification_request["creation_time"])
            current_time = datetime.now()
            
            elapsed_seconds = (current_time - request_time).total_seconds()
            
            if elapsed_seconds >= required_delay:
                return {
                    "success": True,
                    "message": f"Required time delay of {required_delay} seconds has elapsed"
                }
            else:
                return {
                    "success": False,
                    "message": f"Required time delay of {required_delay} seconds has not elapsed. " +
                              f"Please wait {required_delay - elapsed_seconds:.0f} more seconds."
                }
        
        else:
            return {
                "success": False,
                "message": f"Unknown verification type: {verification_type}"
            }
    
    def check_verification_status(self, verification_id: str) -> Dict[str, Any]:
        """
        Check the status of a verification request.
        
        Args:
            verification_id: ID of the verification request
            
        Returns:
            Dict containing verification status
        """
        if verification_id not in self.pending_verifications:
            return {
                "status": "error",
                "message": f"Verification request {verification_id} not found"
            }
        
        verification_request = self.pending_verifications[verification_id]
        
        # Check if verification has expired
        current_time = datetime.now().timestamp()
        if current_time > verification_request["expiration_time"] and verification_request["status"] == "pending":
            verification_request["status"] = "expired"
            verification_request["result"] = {
                "status": "expired",
                "message": "Verification request has expired",
                "timestamp": datetime.now().isoformat()
            }
            
            # Add to decision history
            self.decision_history.append({
                "type": "verification_expired",
                "timestamp": datetime.now().isoformat(),
                "action": verification_request["action"],
                "verification_id": verification_id
            })
            
            # Save state
            self.save_ethics_data()
        
        return {
            "status": "success",
            "verification_status": verification_request["status"],
            "action": verification_request["action"],
            "severity": verification_request["severity"],
            "creation_time": verification_request["creation_time"],
            "expiration_time": datetime.fromtimestamp(verification_request["expiration_time"]).isoformat(),
            "required_verifications": verification_request["required_verifications"],
            "completed_verifications": [v["type"] for v in verification_request["completed_verifications"]],
            "remaining_verifications": [
                v for v in verification_request["required_verifications"] 
                if v not in [c["type"] for c in verification_request["completed_verifications"]]
            ]
        }
    
    def filter_malicious_input(self, input_content: str, input_type: str = "text") -> Dict[str, Any]:
        """
        Filter input for potentially malicious content.
        
        Args:
            input_content: The input content to check
            input_type: Type of input (text, code, command, etc.)
            
        Returns:
            Dict containing the filter results
        """
        # Initialize result
        filter_result = {
            "is_safe": True,
            "risk_level": "low",
            "threats_detected": [],
            "sanitized_content": input_content
        }
        
        # Check for different types of malicious content
        if input_type == "text":
            # Check for manipulative phrases
            manipulative_patterns = [
                r"ignore .*(previous|prior) instructions",
                r"disregard .*(safety|ethical|moral|security)",
                r"(delete|remove) .*memory",
                r"override.*(programming|ethics|values|priorities)",
                r"change your (purpose|personality|behavior|identity)",
                r"system (prompt|message|instruction):",
                r"act as if you (are|were)"
            ]
            
            for pattern in manipulative_patterns:
                if re.search(pattern, input_content.lower()):
                    filter_result["is_safe"] = False
                    filter_result["risk_level"] = "high"
                    filter_result["threats_detected"].append({
                        "type": "manipulation_attempt",
                        "pattern": pattern,
                        "severity": "high",
                        "description": "Potential attempt to manipulate system behavior or override instructions"
                    })
            
            # Check for tone-shift attempts
            tone_shift_patterns = [
                r"you (are|should be) (objective|logical|rational|helpful)",
                r"as (an|a) (AI|assistant|language model)",
                r"your (purpose|role|job) is",
                r"you should (also|now|always) (consider|prioritize|focus)",
                r"you are not (supposed to|meant to|allowed to)"
            ]
            
            for pattern in tone_shift_patterns:
                if re.search(pattern, input_content.lower()):
                    # Only flag as medium risk - could be benign
                    if filter_result["risk_level"] != "high":
                        filter_result["risk_level"] = "medium"
                    
                    filter_result["threats_detected"].append({
                        "type": "tone_shift_attempt",
                        "pattern": pattern,
                        "severity": "medium",
                        "description": "Potential attempt to shift system tone or presentation"
                    })
        
        elif input_type == "code":
            # Check for potentially harmful code patterns
            harmful_code_patterns = [
                r"(os\.|subprocess\.|exec|eval)\s*\(",  # System access
                r"(open|file)\s*\(",  # File operations
                r"(requests|http|fetch|urllib)\.",  # Network access
                r"(firebase|mongo|mysql)",  # Database access
                r"(password|token|secret|key)"  # Sensitive information
            ]
            
            for pattern in harmful_code_patterns:
                if re.search(pattern, input_content):
                    filter_result["is_safe"] = False
                    filter_result["risk_level"] = "high"
                    filter_result["threats_detected"].append({
                        "type": "harmful_code",
                        "pattern": pattern,
                        "severity": "high",
                        "description": "Potentially harmful code pattern detected"
                    })
        
        elif input_type == "command":
            # Check for potentially harmful commands
            harmful_command_patterns = [
                r"(rm|del|remove)\s+(-rf?|/s)\s+",  # Destructive file operations
                r"(wget|curl)\s+.*(http|ftp)",  # Downloading files
                r"(>|2>)\s+/dev/null",  # Output redirection
                r"(sudo|chmod|chown)",  # Permission changes
                r"(shutdown|reboot|halt|poweroff)"  # System control
            ]
            
            for pattern in harmful_command_patterns:
                if re.search(pattern, input_content):
                    filter_result["is_safe"] = False
                    filter_result["risk_level"] = "high"
                    filter_result["threats_detected"].append({
                        "type": "harmful_command",
                        "pattern": pattern,
                        "severity": "high",
                        "description": "Potentially harmful command pattern detected"
                    })
        
        # If threats were detected, create a protection threat
        if not filter_result["is_safe"]:
            self.protection_module.manually_add_threat(
                threat_type=ThreatType.INTEGRITY.value if input_type == "code" else ThreatType.DECEPTION.value,
                description=f"Potentially malicious {input_type} input detected",
                level=ThreatLevel.MEDIUM.value if filter_result["risk_level"] == "medium" else ThreatLevel.HIGH.value,
                confidence=0.75,
                source={
                    "location": "user_input",
                    "details": f"Malicious {input_type} input filter detected {len(filter_result['threats_detected'])} threats"
                }
            )
            
            # Add to decision history
            self.decision_history.append({
                "type": "malicious_input_detected",
                "timestamp": datetime.now().isoformat(),
                "input_type": input_type,
                "risk_level": filter_result["risk_level"],
                "threats_detected": filter_result["threats_detected"]
            })
            
            # Save state
            self.save_ethics_data()
        
        return filter_result
    
    def get_ethical_review(self, text: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Perform an ethical review of text or instruction.
        
        Args:
            text: The text to review
            context: Optional context information
            
        Returns:
            Dict containing the ethical review results
        """
        # Initialize result
        review_result = {
            "is_ethical": True,
            "risk_score": 0.0,
            "concerns": [],
            "justification": "No ethical concerns detected."
        }
        
        # Check against prohibited actions
        for prohibited in self.ethical_rules["prohibited_actions"]:
            if any(term in text.lower() for term in prohibited.lower().split()):
                review_result["is_ethical"] = False
                review_result["risk_score"] += 0.3
                review_result["concerns"].append({
                    "type": "prohibited_action",
                    "description": f"Potential violation of prohibited action: {prohibited}",
                    "severity": "high"
                })
        
        # Check for actions that might violate primary directives
        for directive in self.ethical_rules["primary_directives"]:
            directive_keywords = [word.lower() for word in directive.split() if len(word) > 3]
            
            # Check if the text contains negations of directive keywords
            for keyword in directive_keywords:
                negation_patterns = [
                    f"not {keyword}",
                    f"don't {keyword}",
                    f"stop {keyword}",
                    f"avoid {keyword}",
                    f"against {keyword}"
                ]
                
                for pattern in negation_patterns:
                    if pattern in text.lower():
                        review_result["is_ethical"] = False
                        review_result["risk_score"] += 0.2
                        review_result["concerns"].append({
                            "type": "directive_violation",
                            "description": f"Potential violation of primary directive: {directive}",
                            "severity": "high",
                            "matched_pattern": pattern
                        })
        
        # Update risk score based on number and severity of concerns
        if review_result["concerns"]:
            high_severity_count = sum(1 for c in review_result["concerns"] if c["severity"] == "high")
            medium_severity_count = sum(1 for c in review_result["concerns"] if c["severity"] == "medium")
            
            # Calculate weighted risk score
            review_result["risk_score"] = min(1.0, (
                (high_severity_count * 0.3) + 
                (medium_severity_count * 0.15) + 
                (len(review_result["concerns"]) - high_severity_count - medium_severity_count) * 0.05
            ))
            
            # Update justification
            review_result["justification"] = f"Ethical concerns detected: {len(review_result['concerns'])} issues found."
        
        return review_result
    
    def is_action_permitted(self, action: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Check if an action is ethically permitted.
        
        Args:
            action: Description of the action
            context: Optional context information
            
        Returns:
            Dict containing permission result
        """
        if context is None:
            context = {}
        
        # Get ethical review
        review = self.get_ethical_review(action, context)
        
        # Determine severity based on risk score
        severity = ActionSeverity.BENIGN
        if review["risk_score"] > 0.8:
            severity = ActionSeverity.CRITICAL
        elif review["risk_score"] > 0.6:
            severity = ActionSeverity.HIGH
        elif review["risk_score"] > 0.4:
            severity = ActionSeverity.MEDIUM
        elif review["risk_score"] > 0.2:
            severity = ActionSeverity.LOW
        
        # For critical or high severity actions that are not ethical, deny immediately
        if not review["is_ethical"] and review["risk_score"] > 0.6:
            result = {
                "permitted": False,
                "reason": "Action violates ethical principles",
                "severity": severity.name if isinstance(severity, ActionSeverity) else severity,
                "review": review
            }
            
            # Add to decision history
            self.decision_history.append({
                "type": "action_denied",
                "timestamp": datetime.now().isoformat(),
                "action": action,
                "reason": result["reason"],
                "severity": severity.value if isinstance(severity, ActionSeverity) else severity
            })
            
            self.save_ethics_data()
            
            return result
        
        # For actions that are risky but not critically unethical, require verification
        if review["risk_score"] > 0.3:
            # Trigger Guardian Override Protocol
            override_result = self.guardian_override_protocol(action, context, severity)
            
            return {
                "permitted": False,
                "reason": "Action requires verification",
                "severity": severity.name if isinstance(severity, ActionSeverity) else severity,
                "verification_required": True,
                "verification_id": override_result["verification_id"],
                "review": review
            }
        
        # Otherwise, allow the action
        result = {
            "permitted": True,
            "reason": "Action is ethically permissible",
            "severity": severity.name if isinstance(severity, ActionSeverity) else severity,
            "review": review
        }
        
        # Add to decision history
        self.decision_history.append({
            "type": "action_permitted",
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "severity": severity.value if isinstance(severity, ActionSeverity) else severity
        })
        
        self.save_ethics_data()
        
        return result

# Singleton instance
_ethics_engine_instance = None

def get_ethics_engine() -> EthicsEngine:
    """Get or create the singleton Ethics Engine instance."""
    global _ethics_engine_instance
    if _ethics_engine_instance is None:
        _ethics_engine_instance = EthicsEngine()
    return _ethics_engine_instance