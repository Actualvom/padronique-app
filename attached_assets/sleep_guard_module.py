#!/usr/bin/env python3
"""
sleep_guard_module.py – Oversees user safety, breathing, movement, and environmental scanning during sleep.
"""

class SleepGuardModule:
    def __init__(self):
        self.sleep_state = False
        self.environment_clear = True

    def enter_sleep_mode(self):
        self.sleep_state = True
        return "SleepGuard activated. Monitoring initialized."

    def monitor(self, vitals, noise_levels, movement):
        if vitals["heart_rate"] < 40 or vitals["oxygen"] < 90:
            return "Alert: Abnormal vitals detected. Preparing to intervene."
        if noise_levels > 60:
            return "Alert: Environmental disturbance detected."
        if movement == "sudden":
            return "Monitoring: Tossing or distress detected. Logging patterns."
        return "Stable: Sleep environment nominal."

    def exit_sleep_mode(self):
        self.sleep_state = False
        return "SleepGuard deactivated. User awakening detected."
