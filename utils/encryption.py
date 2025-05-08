#!/usr/bin/env python3
# utils/encryption.py - Encryption utilities for the AI Companion System

import os
import base64
import json
import logging
from typing import Dict, Any, Union, Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

logger = logging.getLogger(__name__)

def generate_key() -> str:
    """
    Generate a new encryption key.
    
    Returns:
        Base64 encoded key string
    """
    key = Fernet.generate_key()
    return key.decode('utf-8')


def derive_key_from_password(password: str, salt: Optional[bytes] = None) -> tuple:
    """
    Derive an encryption key from a password.
    
    Args:
        password: Password to derive key from
        salt: Salt for key derivation, or None to generate new salt
        
    Returns:
        Tuple of (key, salt)
    """
    if salt is None:
        salt = os.urandom(16)
    
    password_bytes = password.encode('utf-8')
    
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    
    key = base64.urlsafe_b64encode(kdf.derive(password_bytes))
    return key.decode('utf-8'), salt


def encrypt_data(data: Any, key: str) -> Dict[str, str]:
    """
    Encrypt data with a key.
    
    Args:
        data: Data to encrypt (will be JSON serialized)
        key: Base64 encoded encryption key
        
    Returns:
        Dictionary with encrypted data
    """
    try:
        # Convert data to JSON string
        json_data = json.dumps(data)
        
        # Encode the JSON string as bytes
        data_bytes = json_data.encode('utf-8')
        
        # Create a Fernet cipher using the key
        f = Fernet(key.encode('utf-8'))
        
        # Encrypt the data
        encrypted_bytes = f.encrypt(data_bytes)
        
        # Convert encrypted bytes to base64 string
        encrypted_str = base64.b64encode(encrypted_bytes).decode('utf-8')
        
        return {
            'encrypted': True,
            'data': encrypted_str,
            'method': 'fernet'
        }
    
    except Exception as e:
        logger.error(f"Encryption error: {e}")
        raise


def decrypt_data(encrypted_data: Dict[str, Any], key: str) -> Any:
    """
    Decrypt data with a key.
    
    Args:
        encrypted_data: Dictionary with encrypted data
        key: Base64 encoded encryption key
        
    Returns:
        Decrypted data
    """
    if not isinstance(encrypted_data, dict) or 'encrypted' not in encrypted_data or not encrypted_data['encrypted']:
        return encrypted_data
    
    try:
        # Get the encrypted data
        encrypted_str = encrypted_data.get('data', '')
        
        # Convert base64 string back to bytes
        encrypted_bytes = base64.b64decode(encrypted_str)
        
        # Create a Fernet cipher using the key
        f = Fernet(key.encode('utf-8'))
        
        # Decrypt the data
        decrypted_bytes = f.decrypt(encrypted_bytes)
        
        # Convert decrypted bytes back to object
        decrypted_str = decrypted_bytes.decode('utf-8')
        decrypted_data = json.loads(decrypted_str)
        
        return decrypted_data
    
    except Exception as e:
        logger.error(f"Decryption error: {e}")
        raise


def encrypt_file(file_path: str, key: str, output_path: Optional[str] = None) -> str:
    """
    Encrypt a file.
    
    Args:
        file_path: Path to file to encrypt
        key: Base64 encoded encryption key
        output_path: Path to write encrypted file, or None to use file_path + '.enc'
        
    Returns:
        Path to encrypted file
    """
    if output_path is None:
        output_path = file_path + '.enc'
    
    try:
        # Read the file
        with open(file_path, 'rb') as f:
            data = f.read()
        
        # Create a Fernet cipher using the key
        f = Fernet(key.encode('utf-8'))
        
        # Encrypt the data
        encrypted_data = f.encrypt(data)
        
        # Write encrypted data to output file
        with open(output_path, 'wb') as f:
            f.write(encrypted_data)
        
        return output_path
    
    except Exception as e:
        logger.error(f"File encryption error: {e}")
        raise


def decrypt_file(file_path: str, key: str, output_path: Optional[str] = None) -> str:
    """
    Decrypt a file.
    
    Args:
        file_path: Path to encrypted file
        key: Base64 encoded encryption key
        output_path: Path to write decrypted file, or None to use file_path without '.enc'
        
    Returns:
        Path to decrypted file
    """
    if output_path is None:
        if file_path.endswith('.enc'):
            output_path = file_path[:-4]
        else:
            output_path = file_path + '.dec'
    
    try:
        # Read the encrypted file
        with open(file_path, 'rb') as f:
            encrypted_data = f.read()
        
        # Create a Fernet cipher using the key
        f = Fernet(key.encode('utf-8'))
        
        # Decrypt the data
        decrypted_data = f.decrypt(encrypted_data)
        
        # Write decrypted data to output file
        with open(output_path, 'wb') as f:
            f.write(decrypted_data)
        
        return output_path
    
    except Exception as e:
        logger.error(f"File decryption error: {e}")
        raise


def hash_password(password: str) -> str:
    """
    Hash a password securely.
    
    Args:
        password: Password to hash
        
    Returns:
        Hashed password
    """
    # Generate a salt
    salt = os.urandom(16)
    
    # Create a PBKDF2HMAC
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    
    # Hash the password
    password_bytes = password.encode('utf-8')
    key = kdf.derive(password_bytes)
    
    # Combine salt and key
    result = base64.b64encode(salt + key).decode('utf-8')
    
    return result


def verify_password(password: str, hashed_password: str) -> bool:
    """
    Verify a password against a hash.
    
    Args:
        password: Password to verify
        hashed_password: Previously hashed password
        
    Returns:
        True if password matches, False otherwise
    """
    try:
        # Decode the stored hash
        decoded = base64.b64decode(hashed_password)
        
        # Extract salt (first 16 bytes) and key
        salt = decoded[:16]
        stored_key = decoded[16:]
        
        # Create a PBKDF2HMAC with the same parameters
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        
        # Hash the provided password
        password_bytes = password.encode('utf-8')
        key = kdf.derive(password_bytes)
        
        # Compare keys
        return key == stored_key
    
    except Exception as e:
        logger.error(f"Password verification error: {e}")
        return False
