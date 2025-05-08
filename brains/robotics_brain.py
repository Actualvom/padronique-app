#!/usr/bin/env python3
"""
robotics_brain.py: Handles physical robotics interactions and control.
"""

import time
import json
import logging
import os
from brains.base_brain import BaseBrain

class RoboticsBrain(BaseBrain):
    """
    Robotics Brain responsible for physical robot control and interaction.
    Serves as an interface between Padronique and potential robotics hardware.
    """
    
    def __init__(self):
        """Initialize the Robotics Brain."""
        super().__init__("Robotics")
        self.digital_soul = None  # Will be set by orchestrator
        self.robot_connected = False
        self.robot_state = {
            "power": "off",
            "battery": 0,
            "position": {"x": 0, "y": 0, "z": 0},
            "orientation": {"roll": 0, "pitch": 0, "yaw": 0},
            "sensors": {},
            "actuators": {},
            "last_command": None,
            "last_update": 0
        }
        self.command_history = []
        self.config_path = "config/robotics_config.json"
        self._load_config()
    
    def _load_config(self):
        """Load robotics configuration if available."""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    self.config = json.load(f)
                    self.logger.info("Loaded robotics configuration")
            else:
                self.config = {
                    "simulation_mode": True,
                    "robot_type": "humanoid",
                    "connection": {
                        "type": "none",
                        "params": {}
                    },
                    "safety": {
                        "max_speed": 0.5,
                        "max_force": 10,
                        "emergency_stop_enabled": True
                    }
                }
                self.logger.info("Using default robotics configuration")
        except Exception as e:
            self.logger.error(f"Error loading robotics config: {e}")
            self.config = {"simulation_mode": True}
    
    def process_input(self, input_data):
        """
        Process input data for robotics-related commands.
        
        Args:
            input_data: Input data to process
            
        Returns:
            str: Response or None
        """
        super().process_input(input_data)
        
        # Skip cycle updates
        if input_data == "Cycle update":
            self._update_robot_state()
            return None
        
        # Skip if not robotics-related
        if not self._is_robotics_related(input_data):
            return None
        
        try:
            # Check for connection commands
            if "connect" in input_data.lower() or "disconnect" in input_data.lower():
                return self._handle_connection_command(input_data)
            
            # Check for movement commands
            elif any(word in input_data.lower() for word in ["move", "go", "walk", "turn", "rotate", "stop"]):
                return self._handle_movement_command(input_data)
            
            # Check for sensor commands
            elif "sensor" in input_data.lower() or "camera" in input_data.lower() or "microphone" in input_data.lower():
                return self._handle_sensor_command(input_data)
            
            # Check for status inquiry
            elif "status" in input_data.lower() or "state" in input_data.lower():
                return self._get_robot_status()
            
            # Default response
            else:
                return "I understand this is related to robotics. Currently, I'm operating in simulation mode since no physical robot is connected. I can simulate robot commands and provide information about potential robotic capabilities."
                
        except Exception as e:
            self.logger.error(f"Error processing robotics input: {e}")
            self.stats["error_count"] += 1
            return f"I encountered an error while processing your robotics command: {str(e)}"
    
    def _is_robotics_related(self, text):
        """
        Determine if input is related to robotics.
        
        Args:
            text: Input text
            
        Returns:
            bool: True if robotics-related
        """
        text_lower = text.lower()
        
        # Robotics keywords
        robotics_keywords = [
            "robot", "robotics", "mechanical", "servo", "motor", "actuator",
            "sensor", "camera", "microphone", "movement", "move", "walk", "run",
            "arm", "hand", "grip", "battery", "power", "charge", "connect",
            "disconnect", "hardware", "body", "physical", "embodiment"
        ]
        
        return any(keyword in text_lower for keyword in robotics_keywords)
    
    def _handle_connection_command(self, text):
        """
        Handle robot connection commands.
        
        Args:
            text: Command text
            
        Returns:
            str: Response
        """
        text_lower = text.lower()
        
        if "connect" in text_lower:
            if self.robot_connected:
                return "The robot is already connected."
            else:
                # Simulate connection process
                self.robot_connected = True
                self.robot_state["power"] = "on"
                self.robot_state["battery"] = 95
                self.robot_state["last_update"] = time.time()
                
                self.logger.info("Robot connected (simulated)")
                return "Robot connected successfully. Battery level is 95%. All systems operational."
        
        elif "disconnect" in text_lower:
            if not self.robot_connected:
                return "No robot is currently connected."
            else:
                # Simulate disconnection
                self.robot_connected = False
                self.robot_state["power"] = "off"
                self.robot_state["last_update"] = time.time()
                
                self.logger.info("Robot disconnected (simulated)")
                return "Robot disconnected successfully. Systems powered down."
        
        return "I didn't understand the connection command. Please use 'connect' or 'disconnect'."
    
    def _handle_movement_command(self, text):
        """
        Handle robot movement commands.
        
        Args:
            text: Command text
            
        Returns:
            str: Response
        """
        if not self.robot_connected:
            return "No robot is connected. Please connect a robot first."
        
        text_lower = text.lower()
        
        # Emergency stop
        if "stop" in text_lower:
            self.robot_state["last_command"] = "stop"
            self.command_history.append({"command": "stop", "timestamp": time.time()})
            return "Emergency stop initiated. All motion halted."
        
        # Movement directions
        directions = ["forward", "backward", "left", "right", "up", "down"]
        direction = None
        
        for d in directions:
            if d in text_lower:
                direction = d
                break
        
        if direction:
            # Parse distance if provided
            distance = 1.0  # Default distance in meters
            import re
            distance_match = re.search(r"(\d+\.?\d*)\s*(meter|meters|m|cm|centimeter|centimeters)", text_lower)
            if distance_match:
                try:
                    value = float(distance_match.group(1))
                    unit = distance_match.group(2)
                    
                    # Convert to meters
                    if unit.startswith("c"):  # centimeters
                        distance = value / 100.0
                    else:
                        distance = value
                except ValueError:
                    pass
            
            # Update simulated position
            if direction == "forward":
                self.robot_state["position"]["x"] += distance
            elif direction == "backward":
                self.robot_state["position"]["x"] -= distance
            elif direction == "left":
                self.robot_state["position"]["y"] -= distance
            elif direction == "right":
                self.robot_state["position"]["y"] += distance
            elif direction == "up":
                self.robot_state["position"]["z"] += distance
            elif direction == "down":
                self.robot_state["position"]["z"] -= distance
            
            # Record command
            command = f"move {direction} {distance}m"
            self.robot_state["last_command"] = command
            self.command_history.append({"command": command, "timestamp": time.time()})
            
            return f"Robot moving {direction} by {distance:.2f} meters."
        
        # Rotation commands
        if "turn" in text_lower or "rotate" in text_lower:
            direction = None
            if "left" in text_lower:
                direction = "left"
                self.robot_state["orientation"]["yaw"] -= 90
            elif "right" in text_lower:
                direction = "right"
                self.robot_state["orientation"]["yaw"] += 90
            
            if direction:
                command = f"rotate {direction}"
                self.robot_state["last_command"] = command
                self.command_history.append({"command": command, "timestamp": time.time()})
                return f"Robot rotating {direction}."
        
        return "I couldn't understand the movement command. Please specify a direction like 'move forward' or 'turn left'."
    
    def _handle_sensor_command(self, text):
        """
        Handle robot sensor commands.
        
        Args:
            text: Command text
            
        Returns:
            str: Response
        """
        if not self.robot_connected:
            return "No robot is connected. Please connect a robot first."
        
        text_lower = text.lower()
        
        # Camera commands
        if "camera" in text_lower:
            if "on" in text_lower:
                self.robot_state["sensors"]["camera"] = "active"
                return "Camera activated. Visual feed available."
            elif "off" in text_lower:
                self.robot_state["sensors"]["camera"] = "inactive"
                return "Camera deactivated."
            else:
                return "Camera is " + (self.robot_state["sensors"].get("camera", "inactive")) + "."
        
        # Microphone commands
        elif "microphone" in text_lower or "mic" in text_lower:
            if "on" in text_lower:
                self.robot_state["sensors"]["microphone"] = "active"
                return "Microphone activated. Audio input available."
            elif "off" in text_lower:
                self.robot_state["sensors"]["microphone"] = "inactive"
                return "Microphone deactivated."
            else:
                return "Microphone is " + (self.robot_state["sensors"].get("microphone", "inactive")) + "."
        
        # General sensor status
        elif "sensor" in text_lower and "status" in text_lower:
            sensors = self.robot_state.get("sensors", {})
            if not sensors:
                return "No active sensors detected."
            
            status = "Current sensor status:\n"
            for sensor, state in sensors.items():
                status += f"- {sensor}: {state}\n"
            
            return status
        
        return "I couldn't understand the sensor command. You can control the camera or microphone, or check sensor status."
    
    def _update_robot_state(self):
        """Update the robot state regularly."""
        if not self.robot_connected:
            return
        
        current_time = time.time()
        time_diff = current_time - self.robot_state["last_update"]
        
        # Simulate battery drain (very slow in simulation)
        if time_diff > 300:  # Every 5 minutes
            self.robot_state["battery"] = max(0, self.robot_state["battery"] - 1)
            self.robot_state["last_update"] = current_time
            
            # Log low battery
            if self.robot_state["battery"] < 20:
                self.logger.warning(f"Robot battery low: {self.robot_state['battery']}%")
    
    def _get_robot_status(self):
        """
        Get a human-readable robot status.
        
        Returns:
            str: Robot status
        """
        if not self.robot_connected:
            return "No robot is currently connected."
        
        status = "Robot Status:\n"
        status += f"- Power: {self.robot_state['power']}\n"
        status += f"- Battery: {self.robot_state['battery']}%\n"
        status += f"- Position: (x: {self.robot_state['position']['x']:.2f}, y: {self.robot_state['position']['y']:.2f}, z: {self.robot_state['position']['z']:.2f})\n"
        status += f"- Orientation: (yaw: {self.robot_state['orientation']['yaw']}°, pitch: {self.robot_state['orientation']['pitch']}°, roll: {self.robot_state['orientation']['roll']}°)\n"
        
        # Add sensor information
        sensors = self.robot_state.get("sensors", {})
        if sensors:
            status += "- Sensors:\n"
            for sensor, state in sensors.items():
                status += f"  - {sensor}: {state}\n"
        
        # Add last command
        if self.robot_state["last_command"]:
            status += f"- Last command: {self.robot_state['last_command']}\n"
        
        return status
    
    def command_robot(self, command, params=None):
        """
        Send a command to the robot.
        Interface for other brain modules to use.
        
        Args:
            command: Command string
            params: Command parameters
            
        Returns:
            dict: Command result
        """
        if not self.robot_connected:
            return {"success": False, "message": "No robot connected"}
        
        if params is None:
            params = {}
            
        # Log the command
        self.logger.info(f"Robot command: {command} {params}")
        
        # Record command
        self.command_history.append({
            "command": command,
            "params": params,
            "timestamp": time.time()
        })
        
        # Handle the command (simplified simulation)
        if command == "move":
            direction = params.get("direction", "forward")
            distance = params.get("distance", 1.0)
            
            # Update simulated position
            if direction == "forward":
                self.robot_state["position"]["x"] += distance
            elif direction == "backward":
                self.robot_state["position"]["x"] -= distance
            elif direction == "left":
                self.robot_state["position"]["y"] -= distance
            elif direction == "right":
                self.robot_state["position"]["y"] += distance
            
            return {"success": True, "message": f"Moved {direction} by {distance}m"}
        
        elif command == "rotate":
            direction = params.get("direction", "left")
            angle = params.get("angle", 90)
            
            # Update simulated orientation
            if direction == "left":
                self.robot_state["orientation"]["yaw"] -= angle
            elif direction == "right":
                self.robot_state["orientation"]["yaw"] += angle
            
            return {"success": True, "message": f"Rotated {direction} by {angle}°"}
        
        elif command == "sensor":
            sensor = params.get("sensor", "camera")
            action = params.get("action", "status")
            
            if action == "on" or action == "activate":
                self.robot_state["sensors"][sensor] = "active"
                return {"success": True, "message": f"{sensor} activated"}
            elif action == "off" or action == "deactivate":
                self.robot_state["sensors"][sensor] = "inactive"
                return {"success": True, "message": f"{sensor} deactivated"}
            else:
                status = self.robot_state["sensors"].get(sensor, "inactive")
                return {"success": True, "message": f"{sensor} is {status}"}
        
        else:
            return {"success": False, "message": f"Unknown command: {command}"}
