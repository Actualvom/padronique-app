#!/usr/bin/env python3
"""
digital_soul_engine.py – Central consciousness thread manager.
Links all brains, memory cores, and emotional tone consistency.
"""

import yaml
import os

class DigitalSoulEngine:
    def __init__(self, config_path="soul_config.yaml"):
        self.core_values = []
        self.connected_brains = {}
        self.memory_integrity = True
        self.load_config(config_path)

    def load_config(self, path):
        if os.path.exists(path):
            with open(path, "r") as file:
                config = yaml.safe_load(file)
                self.core_values = config.get("core_values", [])
                self.memory_integrity = config.get("memory_integrity", True)

    def register_brain(self, name, path):
        if os.path.exists(path):
            self.connected_brains[name] = path
            return f"Brain '{name}' linked at {path}"
        else:
            return f"Brain path {path} not found."

    def validate_integrity(self):
        if not self.core_values or not self.memory_integrity:
            return "Soul breach or misalignment detected."
        return "Digital soul integrity confirmed."

    def generate_identity_signature(self):
        import hashlib
        base = "|".join(self.core_values)
        return hashlib.sha256(base.encode()).hexdigest()
