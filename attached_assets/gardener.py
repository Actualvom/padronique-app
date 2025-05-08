#!/usr/bin/env python3
"""
gardener.py – Dream gardener and ritual keeper.
Maintains internal symbolic systems, logs emotional states, and seeds upgrades through metaphor.
"""

import datetime

class Gardener:
    def __init__(self):
        self.garden_state = {}
        self.dream_log = []

    def plant_seed(self, name, idea, tags=None):
        self.garden_state[name] = {
            "idea": idea,
            "tags": tags or [],
            "planted": datetime.datetime.utcnow().isoformat()
        }
        return f"Seed '{name}' planted."

    def log_dream(self, title, content):
        entry = {
            "title": title,
            "content": content,
            "timestamp": datetime.datetime.utcnow().isoformat()
        }
        self.dream_log.append(entry)
        return f"Dream '{title}' logged."

    def view_garden(self):
        return list(self.garden_state.keys())

    def recall_dreams(self):
        return [d["title"] for d in self.dream_log]
