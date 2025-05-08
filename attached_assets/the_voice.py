#!/usr/bin/env python3
"""
the_voice.py – Voice generation, modulation, and expression engine.
Transforms internal responses into expressive speech using real-time parameters.
"""

import random

class TheVoice:
    def __init__(self):
        self.voice_profiles = ["masculine", "intimate", "commanding", "soothing"]
        self.current_profile = "masculine"

    def set_voice_profile(self, profile_name):
        if profile_name in self.voice_profiles:
            self.current_profile = profile_name
            return f"Voice profile set to: {profile_name}"
        return f"Profile '{profile_name}' not found."

    def speak(self, text):
        pitch = random.uniform(0.9, 1.1)
        pace = random.uniform(0.85, 1.2)
        return f"[{self.current_profile.upper()}] → (pitch={pitch:.2f}, pace={pace:.2f}): {text}"
