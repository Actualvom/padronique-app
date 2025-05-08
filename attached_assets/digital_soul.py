#!/usr/bin/env python3
"""
digital_soul.py - Core memory and identity structure.
"""

class DigitalSoul:
    def __init__(self):
        self.core_memory = None
        self.load_memory()

    def load_memory(self):
        try:
            with open('soul/memory.db', 'r') as mem_file:
                for line in mem_file:
                    if line.startswith("core_memory:"):
                        self.core_memory = line.strip().split("core_memory:")[1].strip().strip("'").strip('"')
        except FileNotFoundError:
            self.core_memory = "Memory file not found."

    def speak(self):
        return f"My memory says: {self.core_memory or 'I have no memory... yet.'}"
