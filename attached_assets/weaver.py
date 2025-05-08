"""
weaver.py - Synthesizes ideas from fragmented concepts.
"""
class Weaver:
    def __init__(self):
        self.inputs = []

    def feed(self, concept):
        self.inputs.append(concept)

    def weave(self):
        if not self.inputs:
            return "Nothing to synthesize."
        return f"Synthesized thought: {' + '.join(self.inputs)}"
