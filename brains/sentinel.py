#!/usr/bin/env python3
"""
sentinel.py: Monitors system health and security.
"""

import time
import os
import logging
import platform
import threading
import psutil
from brains.base_brain import BaseBrain

class Sentinel(BaseBrain):
    """
    Sentinel brain responsible for monitoring system health and security.
    Detects threats, monitors resources, and ensures system integrity.
    """
    
    def __init__(self):
        """Initialize the Sentinel brain."""
        super().__init__("Sentinel")
        self.digital_soul = None  # Will be set by orchestrator
        self.threat_level = 0  # 0-10 scale
        self.threats = []
        self.system_health = {
            "cpu_usage": 0,
            "memory_usage": 0,
            "disk_space": 0,
            "uptime": 0
        }
        self.last_scan = 0
        self.scan_interval = 60  # seconds between scans
        self._monitor_thread = None
        self._running = False
        self._start_monitoring()
    
    def _start_monitoring(self):
        """Start the background monitoring thread."""
        self._running = True
        self._monitor_thread = threading.Thread(
            target=self._monitoring_loop,
            daemon=True
        )
        self._monitor_thread.start()
        self.logger.info("System monitoring started")
    
    def _monitoring_loop(self):
        """Main loop for system monitoring."""
        while self._running:
            try:
                self.scan_system()
                time.sleep(10)  # Check every 10 seconds
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                time.sleep(30)  # Back off on errors
    
    def scan_system(self):
        """
        Scan the system for health and security issues.
        
        Returns:
            dict: System health and security information
        """
        current_time = time.time()
        
        # Only perform full scan periodically
        if current_time - self.last_scan < self.scan_interval:
            return {
                "system_health": self.system_health,
                "threat_level": self.threat_level,
                "threats": self.threats
            }
        
        self.last_scan = current_time
        self.logger.debug("Performing system scan")
        
        # Update system health metrics
        try:
            self.system_health["cpu_usage"] = psutil.cpu_percent(interval=1)
            self.system_health["memory_usage"] = psutil.virtual_memory().percent
            self.system_health["disk_space"] = psutil.disk_usage('/').percent
            self.system_health["uptime"] = time.time() - psutil.boot_time()
            
            # Log significant changes
            if self.system_health["cpu_usage"] > 90:
                self.logger.warning(f"High CPU usage: {self.system_health['cpu_usage']}%")
            
            if self.system_health["memory_usage"] > 90:
                self.logger.warning(f"High memory usage: {self.system_health['memory_usage']}%")
            
            if self.system_health["disk_space"] > 90:
                self.logger.warning(f"Low disk space: {100 - self.system_health['disk_space']}% free")
            
        except Exception as e:
            self.logger.error(f"Error updating system health: {e}")
        
        # Check for security issues
        self.check_security()
        
        # Store scan results in memory
        if hasattr(self, 'digital_soul') and self.digital_soul:
            self.digital_soul.add_memory(
                "core", 
                {
                    "system_health": self.system_health,
                    "threat_level": self.threat_level,
                    "threats": self.threats
                },
                tags=["system_scan", "security", "health"]
            )
        
        return {
            "system_health": self.system_health,
            "threat_level": self.threat_level,
            "threats": self.threats
        }
    
    def check_security(self):
        """
        Check for security threats and vulnerabilities.
        Updates threat_level and threats properties.
        """
        self.threats = []
        
        # Check for unusual process activity
        try:
            processes = psutil.process_iter(['pid', 'name', 'username'])
            suspicious_processes = []
            
            # Check for known suspicious process names (example)
            suspicious_names = ["notaspy", "keylogger", "screencapture"]
            for proc in processes:
                if any(suspicious in proc.info['name'].lower() for suspicious in suspicious_names):
                    suspicious_processes.append(proc.info)
            
            if suspicious_processes:
                self.threats.append({
                    "type": "suspicious_process",
                    "details": suspicious_processes
                })
        except Exception as e:
            self.logger.error(f"Error checking processes: {e}")
        
        # Check for file integrity
        try:
            # In a real implementation, this would check critical files
            # against known checksums
            pass
        except Exception as e:
            self.logger.error(f"Error checking file integrity: {e}")
        
        # Check network connections
        try:
            # In a real implementation, this would analyze network
            # connections for suspicious activity
            pass
        except Exception as e:
            self.logger.error(f"Error checking network: {e}")
        
        # Update threat level based on findings
        self.threat_level = min(10, len(self.threats) * 2)
        
        if self.threat_level > 0:
            self.logger.warning(f"Security threats detected. Threat level: {self.threat_level}/10")
    
    def process_input(self, input_data):
        """
        Process input data for security analysis.
        
        Args:
            input_data: Input data to process
            
        Returns:
            str: Response or None
        """
        super().process_input(input_data)
        
        # Skip cycle updates
        if input_data == "Cycle update":
            return None
        
        # Check for security-related commands
        if any(keyword in input_data.lower() for keyword in ["security", "threat", "protect", "scan", "monitor"]):
            # Perform a scan and return results
            scan_results = self.scan_system()
            
            if scan_results["threat_level"] > 0:
                return f"Security scan complete. Threat level: {scan_results['threat_level']}/10. Detected {len(scan_results['threats'])} potential issues."
            else:
                return f"Security scan complete. No threats detected. System health: CPU {scan_results['system_health']['cpu_usage']}%, Memory {scan_results['system_health']['memory_usage']}%."
        
        return None
    
    def get_status(self):
        """
        Get the current security and health status.
        
        Returns:
            dict: Current status
        """
        status = super().get_status()
        status.update({
            "system_health": self.system_health,
            "threat_level": self.threat_level,
            "threats_count": len(self.threats)
        })
        return status
    
    def shutdown(self):
        """Shutdown the monitoring thread."""
        self._running = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=5.0)
        self.logger.info("System monitoring stopped")
