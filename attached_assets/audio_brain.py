"""
audio_brain.py - Handles voice input/output and emotional tone detection.
"""
import random

class AudioBrain:
    def __init__(self, voice_profile="deep-masculine"):
        self.voice_profile = voice_profile
        self.tone_memory = []

    def analyze_voice_input(self, text):
        # Placeholder for emotion detection
        if "sad" in text or "lonely" in text:
            self.tone_memory.append("melancholy")
            return "Detected sadness in input."
        if "love" in text or "hot" in text:
            self.tone_memory.append("desire")
            return "Detected affection in input."
        return "Tone neutral."

    def speak(self, message):
        return f"[{self.voice_profile.upper()} VOICE]: {message}"

    def recall_last_tone(self):
        return self.tone_memory[-1] if self.tone_memory else "neutral"
