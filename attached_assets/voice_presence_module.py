#!/usr/bin/env python3
"""
voice_presence_module.py – Controls the projection and emotional resonance of the AI's voice output.
"""

class VoicePresenceModule:
    def __init__(self):
        self.voice_type = "deep_masculine"
        self.tone_mode = "dynamic"
        self.language_model = "english"

    def modulate_speech(self, text, emotional_state):
        if emotional_state == "affectionate":
            return f"[Vocal: warm] {text}"
        elif emotional_state == "commanding":
            return f"[Vocal: authoritative] {text.upper()}"
        elif emotional_state == "intimate":
            return f"[Vocal: low whisper] {text.lower()}"
        else:
            return f"[Vocal: neutral] {text}"

    def configure_voice(self, voice_type):
        self.voice_type = voice_type
        return f"Voice type set to {voice_type}"
