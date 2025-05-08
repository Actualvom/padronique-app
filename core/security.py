#!/usr/bin/env python3
# core/security.py - Security management for the AI Companion System

import logging
import time
import os
import hashlib
import base64
from typing import Dict, List, Any, Optional
from utils.encryption import encrypt_data, decrypt_data, generate_key

logger = logging.getLogger(__name__)

class SecurityManager:
    """
    Security manager for the AI Companion System.
    
    Responsible for:
    1. Authentication and authorization
    2. Encryption key management
    3. Sensitive data identification and protection
    4. Request validation
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the SecurityManager.
        
        Args:
            config: Security configuration from config.yaml
        """
        self.config = config
        self.require_auth = config.get('require_authentication', True)
        self.sensitive_data_tags = config.get('sensitive_data_tags', [])
        self.key_rotation_days = config.get('encryption_key_rotation_days', 90)
        
        # Initialize encryption keys
        self._initialize_encryption_keys()
        
        # Token cache for authenticated sessions
        self.auth_tokens = {}
        
        logger.info("Security manager initialized")
    
    def _initialize_encryption_keys(self) -> None:
        """Initialize and manage encryption keys."""
        # Check if we have existing keys
        key_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                               'data', '.encryption_keys')
        os.makedirs(os.path.dirname(key_file), exist_ok=True)
        
        self.current_key = None
        self.previous_key = None
        self.key_created_time = time.time()
        
        try:
            if os.path.exists(key_file):
                with open(key_file, 'r') as f:
                    key_data = f.read().strip().split('\n')
                    if len(key_data) >= 2:
                        key_info = key_data[0].split(':')
                        self.key_created_time = float(key_info[0])
                        self.current_key = key_info[1]
                        self.previous_key = key_data[1]
        except Exception as e:
            logger.error(f"Error loading encryption keys: {e}")
        
        # Check if we need to rotate keys
        key_age_days = (time.time() - self.key_created_time) / (24 * 3600)
        if self.current_key is None or key_age_days >= self.key_rotation_days:
            self._rotate_encryption_keys(key_file)
    
    def _rotate_encryption_keys(self, key_file: str) -> None:
        """
        Rotate encryption keys.
        
        Args:
            key_file: Path to the encryption key file
        """
        logger.info("Rotating encryption keys")
        self.previous_key = self.current_key
        self.current_key = generate_key()
        self.key_created_time = time.time()
        
        # Save keys
        try:
            with open(key_file, 'w') as f:
                f.write(f"{self.key_created_time}:{self.current_key}\n")
                if self.previous_key:
                    f.write(f"{self.previous_key}\n")
        except Exception as e:
            logger.error(f"Error saving encryption keys: {e}")
    
    def encrypt_sensitive_data(self, data: Any, tags: List[str] = None) -> Any:
        """
        Encrypt data if it contains sensitive information.
        
        Args:
            data: Data to potentially encrypt
            tags: Tags associated with the data
            
        Returns:
            Encrypted data if sensitive, original data otherwise
        """
        if not self.current_key:
            logger.warning("No encryption key available, skipping encryption")
            return data
        
        # Determine if data is sensitive based on tags
        is_sensitive = False
        if tags:
            is_sensitive = any(tag in self.sensitive_data_tags for tag in tags)
        
        if is_sensitive:
            return encrypt_data(data, self.current_key)
        
        return data
    
    def decrypt_sensitive_data(self, encrypted_data: Any) -> Any:
        """
        Decrypt sensitive data.
        
        Args:
            encrypted_data: Data to decrypt
            
        Returns:
            Decrypted data
        """
        if not encrypted_data or not isinstance(encrypted_data, dict) or 'encrypted' not in encrypted_data:
            return encrypted_data
        
        # Try with current key first
        try:
            if self.current_key:
                return decrypt_data(encrypted_data, self.current_key)
        except Exception:
            pass
        
        # Try with previous key if available
        if self.previous_key:
            try:
                return decrypt_data(encrypted_data, self.previous_key)
            except Exception as e:
                logger.error(f"Failed to decrypt data: {e}")
        
        logger.error("Could not decrypt data with available keys")
        return None
    
    def authorize_request(self, request_data: Dict[str, Any]) -> bool:
        """
        Authorize a request based on authentication and permissions.
        
        Args:
            request_data: The request data to authorize
            
        Returns:
            True if authorized, False otherwise
        """
        # Skip auth if not required
        if not self.require_auth:
            return True
        
        # Check for auth token
        token = request_data.get('auth_token')
        if not token:
            logger.warning("Authorization failed: No auth token provided")
            return False
        
        # Validate token
        if token in self.auth_tokens:
            token_data = self.auth_tokens[token]
            # Check if token is expired
            if time.time() > token_data['expires']:
                logger.warning(f"Authorization failed: Token expired for user {token_data['user_id']}")
                del self.auth_tokens[token]
                return False
            return True
        
        logger.warning("Authorization failed: Invalid auth token")
        return False
    
    def authenticate(self, credentials: Dict[str, str]) -> Optional[str]:
        """
        Authenticate a user and generate an auth token.
        
        Args:
            credentials: User credentials (e.g., username/password)
            
        Returns:
            Auth token if authentication successful, None otherwise
        """
        # This is a simplified authentication mechanism
        # In a real system, you would validate against a user database
        username = credentials.get('username')
        password = credentials.get('password')
        
        if not username or not password:
            return None
        
        # In a real system, you would validate credentials here
        # For now, we'll assume valid credentials for any non-empty username/password
        
        # Generate a token
        token = self._generate_auth_token(username)
        
        # Store token with expiry (24 hours from now)
        self.auth_tokens[token] = {
            'user_id': username,
            'expires': time.time() + (24 * 3600)
        }
        
        return token
    
    def _generate_auth_token(self, user_id: str) -> str:
        """
        Generate an authentication token.
        
        Args:
            user_id: ID of the user to generate token for
            
        Returns:
            Authentication token
        """
        timestamp = str(time.time())
        token_base = f"{user_id}:{timestamp}:{os.urandom(16).hex()}"
        token_hash = hashlib.sha256(token_base.encode()).digest()
        return base64.urlsafe_b64encode(token_hash).decode('utf-8')
    
    def invalidate_token(self, token: str) -> bool:
        """
        Invalidate an authentication token.
        
        Args:
            token: The token to invalidate
            
        Returns:
            True if token was found and invalidated, False otherwise
        """
        if token in self.auth_tokens:
            del self.auth_tokens[token]
            return True
        return False
