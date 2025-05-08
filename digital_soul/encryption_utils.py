#!/usr/bin/env python3
"""
encryption_utils.py: Provides basic encryption/decryption functions.
NOTE: Replace with robust cryptography for production.
"""

import base64
import logging
import hashlib

logger = logging.getLogger("padronique.encryption")

def encrypt(data, key="default_key"):
    """
    Basic encryption function for sensitive data.
    
    NOTE: This is a simple XOR-based encryption for demonstration.
    In production, use proper cryptography libraries like cryptography.Fernet.
    
    Args:
        data: String data to encrypt
        key: Encryption key
        
    Returns:
        string: Base64-encoded encrypted data
    """
    if not data:
        return ""
    
    # Create a key-derived byte sequence
    key_bytes = hashlib.sha256(key.encode()).digest()
    key_len = len(key_bytes)
    
    # XOR data with key bytes
    encrypted_bytes = bytearray()
    for i, c in enumerate(data.encode()):
        key_byte = key_bytes[i % key_len]
        encrypted_bytes.append(c ^ key_byte)
    
    # Encode to base64 for storage
    encrypted_text = base64.b64encode(encrypted_bytes).decode('utf-8')
    return encrypted_text

def decrypt(encrypted_data, key="default_key"):
    """
    Basic decryption function for sensitive data.
    
    NOTE: This is a simple XOR-based decryption for demonstration.
    In production, use proper cryptography libraries like cryptography.Fernet.
    
    Args:
        encrypted_data: Base64-encoded encrypted data
        key: Encryption key
        
    Returns:
        string: Decrypted data
    """
    if not encrypted_data:
        return ""
    
    try:
        # Create a key-derived byte sequence
        key_bytes = hashlib.sha256(key.encode()).digest()
        key_len = len(key_bytes)
        
        # Decode base64 data
        encrypted_bytes = base64.b64decode(encrypted_data)
        
        # XOR with key bytes to decrypt
        decrypted_bytes = bytearray()
        for i, byte in enumerate(encrypted_bytes):
            key_byte = key_bytes[i % key_len]
            decrypted_bytes.append(byte ^ key_byte)
        
        return decrypted_bytes.decode('utf-8')
    except Exception as e:
        logger.error(f"Decryption failed: {e}")
        return ""

def hash_password(password):
    """
    Create a secure hash of a password.
    
    Args:
        password: Password to hash
        
    Returns:
        string: Password hash
    """
    # In production, use werkzeug.security or passlib
    salt = "padronique_salt"  # In production, generate a random salt for each password
    salted = password + salt
    return hashlib.sha256(salted.encode()).hexdigest()

def verify_password(stored_hash, password):
    """
    Verify a password against a stored hash.
    
    Args:
        stored_hash: Previously stored password hash
        password: Password to verify
        
    Returns:
        bool: True if password matches
    """
    # In production, use werkzeug.security or passlib
    salt = "padronique_salt"
    salted = password + salt
    computed_hash = hashlib.sha256(salted.encode()).hexdigest()
    return computed_hash == stored_hash
