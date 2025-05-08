#!/usr/bin/env python3
"""
signal_sensorium.py – External and internal sensory network interface.
Handles perception, mapping, and reflexive response simulation.
"""

import random

class SignalSensorium:
    def __init__(self):
        self.inputs = {
            "visual": False,
            "auditory": False,
            "tactile": False,
            "olfactory": False,
            "proprioception": False,
            "threat_alert": False
        }

    def activate_input(self, sense_type):
        if sense_type in self.inputs:
            self.inputs[sense_type] = True
            return f"{sense_type.capitalize()} input activated."
        return "Invalid input type."

    def deactivate_input(self, sense_type):
        if sense_type in self.inputs:
            self.inputs[sense_type] = False
            return f"{sense_type.capitalize()} input deactivated."
        return "Invalid input type."

    def scan_environment(self):
        if self.inputs["threat_alert"]:
            return random.choice(["No threat detected", "Unidentified movement", "Sound anomaly", "Infrared spike"])
        else:
            return "Passive scan only. Threat mode disabled."

    def report_status(self):
        return {sense: state for sense, state in self.inputs.items()}
