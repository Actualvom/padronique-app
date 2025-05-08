#!/usr/bin/env python3
"""
threat_perception.py – Evaluates surroundings for potential threats and deploys preemptive defense logic.
"""

import random

class ThreatPerception:
    def __init__(self):
        self.threat_database = ["low_noise", "proximity_violation", "rapid_movement", "electronic_interference"]
        self.alert_level = 0

    def scan_environment(self, sensor_data):
        alerts = []
        for stimulus in sensor_data:
            if stimulus in self.threat_database:
                alerts.append(f"Detected threat: {stimulus}")
                self.alert_level += 1
        if not alerts:
            alerts.append("Environment secure.")
        return alerts

    def deploy_countermeasures(self):
        if self.alert_level > 2:
            return "Countermeasures deployed: Visual cloaking + signal jamming + evasive routines."
        return "Monitoring quietly..."

    def reset_alert(self):
        self.alert_level = 0
        return "Threat level normalized. Continuing passive scan."
