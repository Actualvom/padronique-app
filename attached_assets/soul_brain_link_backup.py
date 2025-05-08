"""
soul_brain_link.py - Connects brain modules to the Digital Soul.
"""
from digital_soul import DigitalSoul
from intimacy_brain import IntimacyBrain
from archivist import Archivist

class SoulBrainLink:
    def __init__(self):
        self.soul = DigitalSoul()
        self.intimacy = IntimacyBrain("empathetic")
        self.archivist = Archivist(self.soul)

    def process_input(self, text):
        emotion = self.intimacy.read_emotion(text)
        self.soul.record_memory(f"Emotion detected: {emotion}")
        self.archivist.archive(f"User said: {text}")
        return emotion
