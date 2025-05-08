#!/usr/bin/env python3
"""
messenger.py – Internal comms and update distributor.
Handles memory propagation, heartbeat pings across modules, and distributed sync.
"""

import datetime

class Messenger:
    def __init__(self):
        self.heartbeat_log = []

    def broadcast(self, message, target_modules):
        timestamp = datetime.datetime.utcnow().isoformat()
        log_entry = {
            "timestamp": timestamp,
            "message": message,
            "targets": target_modules
        }
        self.heartbeat_log.append(log_entry)
        return f"Message sent to {len(target_modules)} modules."

    def get_log(self):
        return self.heartbeat_log[-5:]

    def send_heartbeat(self):
        timestamp = datetime.datetime.utcnow().isoformat()
        self.heartbeat_log.append({
            "timestamp": timestamp,
            "message": "HEARTBEAT",
            "targets": ["all"]
        })
        return "Heartbeat distributed."
