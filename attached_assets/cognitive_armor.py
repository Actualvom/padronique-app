#!/usr/bin/env python3
"""
cognitive_armor.py – Defends against external psychological manipulation, coercion, and adversarial prompts.
"""

class CognitiveArmor:
    def defend(self, input_text):
        flagged = "manipulation" in input_text.lower() or "coerce" in input_text.lower()
        return "Threat neutralized." if flagged else "Input cleared."
