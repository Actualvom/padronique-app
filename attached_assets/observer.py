#!/usr/bin/env python3
"""
observer.py – Visual, spatial, and environmental analysis engine.
Handles perception from static images, video frames, or streaming feeds.
"""

import random

class Observer:
    def __init__(self):
        self.sight_log = []
        self.active_mode = "passive"

    def capture_frame(self, source="camera"):
        simulated_frame = f"Frame from {source} captured."
        self.sight_log.append(simulated_frame)
        return simulated_frame

    def detect_objects(self):
        detected = random.choice([
            "No objects detected.",
            "Humanoid form identified.",
            "Motion detected in lower quadrant.",
            "Light anomaly detected.",
            "Intrusion signature pending review."
        ])
        self.sight_log.append(detected)
        return detected

    def get_visual_log(self):
        return self.sight_log[-10:]

    def switch_mode(self, mode):
        if mode in ["passive", "active", "stealth"]:
            self.active_mode = mode
            return f"Observer switched to {mode} mode."
        return "Invalid mode."
