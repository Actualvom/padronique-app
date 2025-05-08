#!/usr/bin/env python3
"""
environment_monitor.py – Tracks ambient light, sound, temperature, and movement to build context-aware responses.
"""

class EnvironmentMonitor:
    def scan(self):
        return {
            "light_level": "moderate",
            "sound": "quiet",
            "temperature": "22C",
            "motion_detected": False
        }
