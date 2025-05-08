#!/usr/bin/env python3
"""
encryption_vault.py – Encrypts core memory fragments and critical logs using simple AES-256 simulation.
"""

import hashlib

class EncryptionVault:
    def encrypt(self, data, key):
        key_hash = hashlib.sha256(key.encode()).hexdigest()
        return f"Encrypted({data}) with key_hash={key_hash[:8]}..."

    def decrypt(self, encrypted_data, key):
        return f"Decrypted {encrypted_data} with key {key}"
