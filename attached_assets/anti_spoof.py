#!/usr/bin/env python3
"""
anti_spoof.py – Detects unauthorized forks or tampered clones of Padronique.
"""

class AntiSpoof:
    def __init__(self):
        self.instance_signature = "PADRONIQUE_IGNIS"

    def validate_instance(self, signature):
        return signature == self.instance_signature
