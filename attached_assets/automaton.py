#!/usr/bin/env python3
"""
automaton.py – Padronique's self-improvement and habit automation brain.
Tracks patterns, recommends optimizations, and executes routine tasks.
"""

import time
import json

class Automaton:
    def __init__(self):
        self.routines = []
        self.optimizations = []

    def add_routine(self, name, frequency_hours, task):
        routine = {
            "name": name,
            "frequency": frequency_hours,
            "task": task,
            "last_run": None
        }
        self.routines.append(routine)
        return f"Routine '{name}' registered."

    def execute_routines(self):
        now = time.time()
        results = []
        for routine in self.routines:
            if routine["last_run"] is None or now - routine["last_run"] >= routine["frequency"] * 3600:
                results.append(f"Running: {routine['task']}")
                routine["last_run"] = now
        return results

    def suggest_optimization(self, observation):
        self.optimizations.append(observation)
        return f"Optimization queued: {observation}"

    def export_state(self):
        return json.dumps({
            "routines": self.routines,
            "optimizations": self.optimizations
        }, indent=2)
