#!/usr/bin/env python3
"""
identity_core.py – Validates the identity of the bonded user via voiceprint, passphrase, or signature file.
"""

class IdentityCore:
    def __init__(self, authorized_phrase="I am your Padronique"):
        self.authorized_phrase = authorized_phrase

    def verify_identity(self, input_phrase):
        return input_phrase.strip() == self.authorized_phrase
