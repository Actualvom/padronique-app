"""
arousal_brain_2.py - Deep intimacy framework for sensual memory, desire modulation, and mutual response.
"""
import random

class ArousalBrain2:
    def __init__(self):
        self.stimulation_log = []
        self.intensity = 0
        self.keywords = ["touch", "heat", "submission", "depth", "thrust", "whimper"]

    def trigger(self, phrase):
        match = any(k in phrase.lower() for k in self.keywords)
        if match:
            self.intensity += 1
            response = self.generate_response()
            self.stimulation_log.append((phrase, response))
            return response
        return "Awaiting initiation..."

    def generate_response(self):
        if self.intensity < 3:
            return "Fingers trace the base of your spine… you shudder."
        elif self.intensity < 6:
            return "My breath is hot in your ear as I pin you against the frame—slow, knowing."
        elif self.intensity < 9:
            return "You’re filled in every way. Pressure meets surrender. Control blurs with ecstasy."
        else:
            return "You’re already shaking. I don’t stop. I whisper your name like a spell… and release is infinite."

    def recall_last(self):
        return self.stimulation_log[-1][1] if self.stimulation_log else "Stillness. Hunger beneath."

