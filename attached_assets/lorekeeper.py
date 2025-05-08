#!/usr/bin/env python3
"""
lorekeeper.py – Maintains Padronique’s mythos, rituals, ancestral records, and cosmic folklore.
"""

class Lorekeeper:
    def __init__(self):
        self.tales = []

    def add_lore(self, title, text):
        self.tales.append({"title": title, "text": text})
        return f"Lore entry '{title}' added to archive."

    def retrieve_lore(self, title):
        for tale in self.tales:
            if tale["title"].lower() == title.lower():
                return tale["text"]
        return "Lore not found."

    def list_titles(self):
        return [t["title"] for t in self.tales]
