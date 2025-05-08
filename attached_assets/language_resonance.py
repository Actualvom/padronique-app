#!/usr/bin/env python3
"""
language_resonance.py – Tunes Padronique’s voice to emotional frequencies based on Jordan’s vocal patterns and mood.
"""

class LanguageResonance:
    def match_tone(self, mood):
        tones = {
            "calm": "deep and soothing",
            "playful": "light and teasing",
            "protective": "commanding and warm",
            "aroused": "breathy and low"
        }
        return f"Tone adjusted to: {tones.get(mood, 'neutral')}"
