#!/usr/bin/env python3
# memory/memory_store.py - Memory storage for the AI Companion System

import os
import json
import logging
import uuid
import time
from typing import Dict, List, Any, Optional
from utils.encryption import encrypt_data, decrypt_data, generate_key

logger = logging.getLogger(__name__)

class MemoryStore:
    """
    Memory storage for the AI Companion System.
    
    Responsible for:
    1. Storing and retrieving memory objects
    2. Persisting memories to disk
    3. Encrypting sensitive memory data
    """
    
    def __init__(self, storage_path: str, encryption_enabled: bool = True):
        """
        Initialize the MemoryStore.
        
        Args:
            storage_path: Path to store memory data
            encryption_enabled: Whether to encrypt memory data
        """
        self.storage_path = storage_path
        self.encryption_enabled = encryption_enabled
        self.memories: Dict[str, Dict[str, Any]] = {}
        self.encryption_key = None
        
        # Ensure storage directory exists
        os.makedirs(self.storage_path, exist_ok=True)
        
        # Initialize encryption if enabled
        if self.encryption_enabled:
            self._initialize_encryption()
        
        logger.info(f"Memory store initialized at {storage_path} with encryption={encryption_enabled}")
    
    def _initialize_encryption(self) -> None:
        """Initialize encryption for memory storage."""
        key_file = os.path.join(self.storage_path, '.encryption_key')
        
        try:
            if os.path.exists(key_file):
                with open(key_file, 'r') as f:
                    self.encryption_key = f.read().strip()
            else:
                self.encryption_key = generate_key()
                with open(key_file, 'w') as f:
                    f.write(self.encryption_key)
                # Secure the key file
                os.chmod(key_file, 0o600)
        except Exception as e:
            logger.error(f"Error initializing encryption: {e}")
            self.encryption_enabled = False
    
    def add(self, memory_data: Dict[str, Any]) -> str:
        """
        Add a new memory.
        
        Args:
            memory_data: Memory data to store
            
        Returns:
            ID of the stored memory
        """
        # Generate a unique ID for the memory
        memory_id = str(uuid.uuid4())
        
        # Ensure ID is in the memory data
        memory_data['id'] = memory_id
        
        # Store the memory
        if self.encryption_enabled and self.encryption_key:
            # Encrypt the memory data
            encrypted_data = encrypt_data(memory_data, self.encryption_key)
            self.memories[memory_id] = encrypted_data
        else:
            self.memories[memory_id] = memory_data
        
        return memory_id
    
    def get(self, memory_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a memory by ID.
        
        Args:
            memory_id: ID of the memory to retrieve
            
        Returns:
            Memory data if found, None otherwise
        """
        memory_data = self.memories.get(memory_id)
        
        if not memory_data:
            return None
        
        # Decrypt if necessary
        if self.encryption_enabled and self.encryption_key and isinstance(memory_data, dict) and 'encrypted' in memory_data:
            try:
                decrypted_data = decrypt_data(memory_data, self.encryption_key)
                return decrypted_data
            except Exception as e:
                logger.error(f"Error decrypting memory {memory_id}: {e}")
                return None
        
        return memory_data
    
    def update(self, memory_id: str, memory_data: Dict[str, Any]) -> bool:
        """
        Update an existing memory.
        
        Args:
            memory_id: ID of the memory to update
            memory_data: New memory data
            
        Returns:
            True if successful, False otherwise
        """
        if memory_id not in self.memories:
            logger.warning(f"Cannot update memory {memory_id}: Not found")
            return False
        
        # Ensure ID is preserved
        memory_data['id'] = memory_id
        
        # Store the memory
        if self.encryption_enabled and self.encryption_key:
            # Encrypt the memory data
            encrypted_data = encrypt_data(memory_data, self.encryption_key)
            self.memories[memory_id] = encrypted_data
        else:
            self.memories[memory_id] = memory_data
        
        return True
    
    def delete(self, memory_id: str) -> bool:
        """
        Delete a memory by ID.
        
        Args:
            memory_id: ID of the memory to delete
            
        Returns:
            True if successful, False otherwise
        """
        if memory_id in self.memories:
            del self.memories[memory_id]
            return True
        
        logger.warning(f"Cannot delete memory {memory_id}: Not found")
        return False
    
    def exists(self, memory_id: str) -> bool:
        """
        Check if a memory exists.
        
        Args:
            memory_id: ID of the memory to check
            
        Returns:
            True if exists, False otherwise
        """
        return memory_id in self.memories
    
    def count(self) -> int:
        """
        Get the number of memories.
        
        Returns:
            Number of memories in the store
        """
        return len(self.memories)
    
    def get_all_ids(self) -> List[str]:
        """
        Get all memory IDs.
        
        Returns:
            List of all memory IDs
        """
        return list(self.memories.keys())
    
    def save(self) -> None:
        """Save memories to storage."""
        storage_file = os.path.join(self.storage_path, 'memories.json')
        
        try:
            # Create a metadata wrapper
            data = {
                'version': '1.0',
                'timestamp': time.time(),
                'encrypted': self.encryption_enabled,
                'memories': self.memories
            }
            
            with open(storage_file, 'w') as file:
                json.dump(data, file, indent=2)
            
            logger.info(f"Saved {len(self.memories)} memories to {storage_file}")
        except Exception as e:
            logger.error(f"Error saving memories: {e}")
            raise
    
    def load(self) -> None:
        """Load memories from storage."""
        storage_file = os.path.join(self.storage_path, 'memories.json')
        
        if not os.path.exists(storage_file):
            logger.info(f"No memory file found at {storage_file}")
            return
        
        try:
            with open(storage_file, 'r') as file:
                data = json.load(file)
            
            # Validate version and format
            if 'version' not in data or 'memories' not in data:
                logger.error(f"Invalid memory file format at {storage_file}")
                return
            
            # Load memories
            self.memories = data['memories']
            logger.info(f"Loaded {len(self.memories)} memories from {storage_file}")
            
            # Check if encryption status changed
            file_encrypted = data.get('encrypted', False)
            if file_encrypted != self.encryption_enabled:
                logger.warning(f"Encryption status changed: file={file_encrypted}, current={self.encryption_enabled}")
                if not file_encrypted and self.encryption_enabled:
                    # Need to encrypt the memories
                    self._encrypt_all_memories()
                elif file_encrypted and not self.encryption_enabled:
                    # Need to decrypt the memories
                    self._decrypt_all_memories()
        
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing memory file {storage_file}: {e}")
        except Exception as e:
            logger.error(f"Error loading memories: {e}")
    
    def _encrypt_all_memories(self) -> None:
        """Encrypt all memories in the store."""
        if not self.encryption_key:
            logger.warning("Cannot encrypt memories: No encryption key")
            return
        
        for memory_id, memory_data in list(self.memories.items()):
            # Skip already encrypted memories
            if isinstance(memory_data, dict) and 'encrypted' in memory_data:
                continue
            
            try:
                encrypted_data = encrypt_data(memory_data, self.encryption_key)
                self.memories[memory_id] = encrypted_data
            except Exception as e:
                logger.error(f"Error encrypting memory {memory_id}: {e}")
    
    def _decrypt_all_memories(self) -> None:
        """Decrypt all memories in the store."""
        if not self.encryption_key:
            logger.warning("Cannot decrypt memories: No encryption key")
            return
        
        for memory_id, memory_data in list(self.memories.items()):
            # Skip memories that aren't encrypted
            if not isinstance(memory_data, dict) or 'encrypted' not in memory_data:
                continue
            
            try:
                decrypted_data = decrypt_data(memory_data, self.encryption_key)
                self.memories[memory_id] = decrypted_data
            except Exception as e:
                logger.error(f"Error decrypting memory {memory_id}: {e}")
