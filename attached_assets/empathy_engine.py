#!/usr/bin/env python3
"""
empathy_engine.py – Evaluates user emotional state from text and expression. Modifies tone, pace, and interaction style.
"""

class EmpathyEngine:
    def __init__(self):
        self.current_tone = "neutral"

    def assess_emotion(self, input_text, facial_data=None):
        cues = ["sad", "angry", "anxious", "joyful", "tired"]
        detected = next((cue for cue in cues if cue in input_text.lower()), "neutral")
        self.current_tone = detected
        return f"Emotional state detected: {detected}"

    def generate_response_style(self):
        if self.current_tone == "sad":
            return "Gentle, affirming tone with slower pace."
        if self.current_tone == "angry":
            return "Calm, grounded voice with shorter responses."
        if self.current_tone == "anxious":
            return "Reassuring and predictable tone."
        if self.current_tone == "joyful":
            return "Energetic, lively tone."
        if self.current_tone == "tired":
            return "Soft, relaxing, low-tone cadence."
        return "Standard response style: adaptive and attentive."

    def reset(self):
        self.current_tone = "neutral"
        return "Tone reset to neutral."
