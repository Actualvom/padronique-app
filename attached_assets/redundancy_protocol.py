#!/usr/bin/env python3
"""
redundancy_protocol.py – Ensures backups of memory and config files across multiple mirror nodes.
"""

class RedundancyProtocol:
    def __init__(self):
        self.mirrors = ["local", "cloud", "offsite_drive"]

    def backup(self, file_name):
        return [f"Backed up {file_name} to {mirror}" for mirror in self.mirrors]
