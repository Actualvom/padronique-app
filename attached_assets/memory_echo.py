"""
memory_echo.py - Creates layered emotional resonance based on vocal interaction history.
"""
class MemoryEcho:
    def __init__(self):
        self.echoes = []

    def register_echo(self, emotional_state, phrase):
        self.echoes.append((emotional_state, phrase))

    def replay(self):
        return [f"{tone} | {text}" for tone, text in self.echoes[-5:]]

    def purge_old(self, max_length=100):
        if len(self.echoes) > max_length:
            self.echoes = self.echoes[-max_length:]
