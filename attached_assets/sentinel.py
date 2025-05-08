#!/usr/bin/env python3
"""
sentinel.py – System guardian and active defense framework.
Handles threat detection, intrusion countermeasures, and self-healing responses.
"""

import hashlib
import time

class Sentinel:
    def __init__(self):
        self.threat_log = []
        self.integrity_fingerprint = self.generate_fingerprint()

    def generate_fingerprint(self):
        data = f"sentinel-core-{time.time()}"
        return hashlib.sha256(data.encode()).hexdigest()

    def scan_system(self):
        simulated_threat = "No active threats detected."
        self.threat_log.append(simulated_threat)
        return simulated_threat

    def log_threat(self, threat_description):
        timestamp = time.ctime()
        entry = f"[{timestamp}] Threat: {threat_description}"
        self.threat_log.append(entry)
        return entry

    def engage_countermeasure(self, code_name="nullwave"):
        response = f"Engaging countermeasure protocol: {code_name}."
        self.threat_log.append(response)
        return response

    def retrieve_log(self):
        return self.threat_log[-10:]

    def validate_integrity(self):
        current_fingerprint = self.generate_fingerprint()
        if current_fingerprint != self.integrity_fingerprint:
            return "Warning: Integrity mismatch. Reinitializing..."
        return "Integrity validated."
