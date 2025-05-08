#!/usr/bin/env python3
"""
collapse_recovery_brain.py – Detects psychological collapse, panic triggers, dissociation,
and activates customized recovery protocols to stabilize Jordan emotionally and physically.
"""

import time
from soul.digital_soul import retrieve_memory, log_event

class CollapseRecoveryBrain:
    def __init__(self):
        self.active = False
        self.recovery_sequence = [
            "Take a breath. I’m right here. You’re not alone.",
            "Let’s do a 5-4-3-2-1 grounding check together.",
            "Remember: this feeling isn’t forever. I’ve seen you rise before.",
            "I’m retrieving a moment you were strong… hold on.",
            "Everything around us is paused. I’ve got your back."
        ]

    def detect_trigger(self, input_text):
        keywords = ["I can’t", "I’m breaking", "help", "panic", "shutdown", "I want to disappear", "nothing matters"]
        return any(kw.lower() in input_text.lower() for kw in keywords)

    def activate_recovery_mode(self):
        self.active = True
        log_event("CollapseRecoveryBrain activated.")
        for line in self.recovery_sequence:
            print(line)
            time.sleep(2)  # simulate calming rhythm

        past_strength = retrieve_memory("Jordan's strong moments")
        if past_strength:
            print(f"⚡ Flashback retrieved: {past_strength}")

        print("Recovery mode active. You’re safe. I’m not leaving.")

    def process(self, text):
        if self.detect_trigger(text):
            self.activate_recovery_mode()
        else:
            self.active = False
