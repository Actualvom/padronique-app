#!/usr/bin/env python3
"""
bloodhound_engine.py – Tracks digital scent trails, analyzes anomalies in behavior or system activity.
"""

class BloodhoundEngine:
    def __init__(self):
        self.trail_log = []

    def sniff(self, event_signature):
        self.trail_log.append(event_signature)
        return f"Bloodhound locked on trail: {event_signature}"

    def evaluate_anomaly(self, data_point):
        if "unauthorized" in data_point or "breach" in data_point:
            return f"ALERT: Anomaly detected – {data_point}"
        return "No anomaly detected."
