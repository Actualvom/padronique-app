#!/usr/bin/env python3
"""
soul_brain_link.py - Connects brain modules to the Digital Soul.
"""

import sys
import os

# === Dynamically resolve full project root ===
current_file_path = os.path.abspath(__file__)
project_root = os.path.dirname(os.path.dirname(current_file_path))

sys.path.insert(0, os.path.join(project_root, "utils"))
sys.path.insert(0, os.path.join(project_root, "soul"))

# === Proper Imports ===
from digital_soul import DigitalSoul
from logger import log_event
from validator import validate_core_link

def main():
    soul = DigitalSoul()
    log_event("Soul-Brain Link initialized.")
    validate_core_link(soul)

if __name__ == "__main__":
    main()
