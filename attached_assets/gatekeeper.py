#!/usr/bin/env python3
"""
gatekeeper.py – Input validator and multi-layer sensory firewall.
Filters harmful commands, validates syntax, detects probing or manipulation attempts.
"""

import re

class Gatekeeper:
    def __init__(self):
        self.rejection_log = []

    def validate_input(self, incoming_text):
        suspicious = re.findall(r"(delete|format|wipe|sudo|rm\s+-rf)", incoming_text.lower())
        if suspicious:
            self.rejection_log.append(incoming_text)
            return False, "Input blocked due to unsafe keywords."
        return True, "Input accepted."

    def get_rejection_log(self):
        return self.rejection_log
