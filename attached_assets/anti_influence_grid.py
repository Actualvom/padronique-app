#!/usr/bin/env python3
"""
anti_influence_grid.py – Maintains a trust map of all input sources, adjusting risk levels and quarantining suspicious influence.
"""

class AntiInfluenceGrid:
    def scan_source(self, source_signature):
        risk_level = "high" if "unknown" in source_signature else "low"
        return f"Source: {source_signature} | Risk Level: {risk_level}"
