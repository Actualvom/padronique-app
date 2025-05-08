#!/usr/bin/env python3
"""
robotics_blueprint.py: Creates and manages blueprints for physical robot embodiment.
"""

import json
import time
import os
import logging
import random
from brains.base_brain import BaseBrain

class RoboticsBlueprint(BaseBrain):
    """
    Robotics Blueprint brain responsible for designing robot bodies and components.
    Creates detailed specifications for potential physical embodiments.
    """
    
    def __init__(self):
        """Initialize the Robotics Blueprint brain."""
        super().__init__("RoboticsBlueprint")
        self.digital_soul = None  # Will be set by orchestrator
        self.blueprints = {}
        self.current_blueprint = None
        self.blueprint_dir = "blueprints"
        self.default_blueprint = {
            "type": "humanoid",
            "height": 180,  # cm
            "weight": 75,   # kg
            "materials": {
                "skeleton": "carbon fiber",
                "exterior": "silicone",
                "joints": "titanium alloy"
            },
            "power": {
                "type": "hybrid",
                "battery_capacity": 10000,  # mAh
                "estimated_runtime": 24     # hours
            },
            "mobility": {
                "locomotion": "bipedal",
                "max_speed": 5,    # km/h
                "terrain_capability": ["indoor", "outdoor_flat", "stairs"]
            },
            "sensors": [
                {
                    "type": "visual",
                    "subtype": "camera",
                    "resolution": "4K",
                    "count": 2,
                    "positions": ["head_front"]
                },
                {
                    "type": "audio",
                    "subtype": "microphone_array",
                    "count": 4,
                    "positions": ["head_circumference"]
                },
                {
                    "type": "tactile",
                    "subtype": "pressure_sensor",
                    "count": 30,
                    "positions": ["fingertips", "palms", "feet"]
                }
            ],
            "actuators": {
                "arms": 2,
                "fingers_per_hand": 5,
                "legs": 2,
                "head_dof": 3  # degrees of freedom
            },
            "communication": [
                "wifi",
                "bluetooth",
                "cellular",
                "speakers",
                "display"
            ],
            "created": time.time(),
            "version": "1.0"
        }
        
        # Create blueprint directory if it doesn't exist
        if not os.path.exists(self.blueprint_dir):
            try:
                os.makedirs(self.blueprint_dir)
                self.logger.info(f"Created blueprint directory: {self.blueprint_dir}")
            except Exception as e:
                self.logger.error(f"Failed to create blueprint directory: {e}")
        
        # Load existing blueprints
        self._load_blueprints()
        
        # Set default as current if no blueprints exist
        if not self.blueprints:
            self.blueprints["default"] = self.default_blueprint
            self.current_blueprint = "default"
            self._save_blueprint("default")
    
    def _load_blueprints(self):
        """Load existing blueprints from disk."""
        if not os.path.exists(self.blueprint_dir):
            return
        
        try:
            for filename in os.listdir(self.blueprint_dir):
                if filename.endswith(".json"):
                    blueprint_name = filename.replace(".json", "")
                    filepath = os.path.join(self.blueprint_dir, filename)
                    
                    with open(filepath, 'r') as f:
                        self.blueprints[blueprint_name] = json.load(f)
                        
                    self.logger.debug(f"Loaded blueprint: {blueprint_name}")
            
            # Set current blueprint to the most recently modified one
            if self.blueprints:
                latest_time = 0
                latest_blueprint = None
                
                for name, blueprint in self.blueprints.items():
                    created_time = blueprint.get("created", 0)
                    if created_time > latest_time:
                        latest_time = created_time
                        latest_blueprint = name
                
                self.current_blueprint = latest_blueprint
                self.logger.info(f"Set current blueprint to: {self.current_blueprint}")
        
        except Exception as e:
            self.logger.error(f"Error loading blueprints: {e}")
    
    def _save_blueprint(self, name):
        """
        Save a blueprint to disk.
        
        Args:
            name: Blueprint name
            
        Returns:
            bool: True if successful
        """
        if name not in self.blueprints:
            return False
        
        try:
            filepath = os.path.join(self.blueprint_dir, f"{name}.json")
            
            with open(filepath, 'w') as f:
                json.dump(self.blueprints[name], f, indent=2)
                
            self.logger.info(f"Saved blueprint: {name}")
            return True
        
        except Exception as e:
            self.logger.error(f"Error saving blueprint {name}: {e}")
            return False
    
    def process_input(self, input_data):
        """
        Process input data for blueprint-related commands.
        
        Args:
            input_data: Input data to process
            
        Returns:
            str: Response or None
        """
        super().process_input(input_data)
        
        # Skip cycle updates
        if input_data == "Cycle update":
            return None
        
        # Skip if not blueprint-related
        if not self._is_blueprint_related(input_data):
            return None
        
        try:
            input_lower = input_data.lower()
            
            # Check for blueprint commands
            if "create blueprint" in input_lower or "new blueprint" in input_lower:
                return self._handle_create_blueprint(input_data)
            
            elif "modify blueprint" in input_lower or "update blueprint" in input_lower or "change blueprint" in input_lower:
                return self._handle_modify_blueprint(input_data)
            
            elif "list blueprints" in input_lower or "show blueprints" in input_lower:
                return self._list_blueprints()
            
            elif "show blueprint" in input_lower or "details" in input_lower:
                return self._show_blueprint_details(input_data)
            
            elif "generate blueprint" in input_lower:
                return self._handle_generate_blueprint(input_data)
            
            # Default response
            else:
                return self._provide_blueprint_info()
                
        except Exception as e:
            self.logger.error(f"Error processing blueprint input: {e}")
            self.stats["error_count"] += 1
            return f"I encountered an error while processing your blueprint request: {str(e)}"
    
    def _is_blueprint_related(self, text):
        """
        Determine if input is related to robotics blueprints.
        
        Args:
            text: Input text
            
        Returns:
            bool: True if blueprint-related
        """
        text_lower = text.lower()
        
        # Blueprint keywords
        blueprint_keywords = [
            "blueprint", "design", "specification", "spec", "robot body",
            "physical form", "embodiment", "dimensions", "construct",
            "build", "fabricate", "prototype", "model", "diagram",
            "schematic", "plan", "template"
        ]
        
        return any(keyword in text_lower for keyword in blueprint_keywords)
    
    def _handle_create_blueprint(self, text):
        """
        Handle blueprint creation requests.
        
        Args:
            text: Request text
            
        Returns:
            str: Response
        """
        # Extract name if provided
        import re
        name_match = re.search(r"named? ['\"]?([a-zA-Z0-9_]+)['\"]?", text.lower())
        
        if name_match:
            name = name_match.group(1)
        else:
            name = f"blueprint_{int(time.time())}"
        
        # Check if name already exists
        if name in self.blueprints:
            return f"A blueprint named '{name}' already exists. Please choose a different name or modify the existing one."
        
        # Create a new blueprint based on the default
        self.blueprints[name] = self.default_blueprint.copy()
        self.blueprints[name]["created"] = time.time()
        self.current_blueprint = name
        
        # Extract type if specified
        type_match = re.search(r"type ['\"]?([a-zA-Z0-9_]+)['\"]?", text.lower())
        if type_match:
            robot_type = type_match.group(1)
            self.blueprints[name]["type"] = robot_type
        
        # Save the new blueprint
        self._save_blueprint(name)
        
        return f"I've created a new blueprint named '{name}'. You can now modify its specifications or generate detailed plans."
    
    def _handle_modify_blueprint(self, text):
        """
        Handle blueprint modification requests.
        
        Args:
            text: Request text
            
        Returns:
            str: Response
        """
        text_lower = text.lower()
        
        # Extract blueprint name if provided
        import re
        name_match = re.search(r"blueprint ['\"]?([a-zA-Z0-9_]+)['\"]?", text_lower)
        
        if name_match:
            name = name_match.group(1)
            if name not in self.blueprints:
                return f"I couldn't find a blueprint named '{name}'. Available blueprints: {', '.join(self.blueprints.keys())}"
        else:
            # Use current blueprint
            if not self.current_blueprint:
                return "No blueprint is currently selected. Please specify which blueprint you want to modify."
            name = self.current_blueprint
        
        # Extract modifications
        modifications = []
        
        # Height modification
        height_match = re.search(r"height (?:to|of|:)? ?(\d+)(?: ?cm)?", text_lower)
        if height_match:
            height = int(height_match.group(1))
            self.blueprints[name]["height"] = height
            modifications.append(f"height to {height} cm")
        
        # Weight modification
        weight_match = re.search(r"weight (?:to|of|:)? ?(\d+)(?: ?kg)?", text_lower)
        if weight_match:
            weight = int(weight_match.group(1))
            self.blueprints[name]["weight"] = weight
            modifications.append(f"weight to {weight} kg")
        
        # Material modifications
        material_match = re.search(r"(?:exterior|skin|surface) material (?:to|:)? ?([a-zA-Z0-9 ]+)", text_lower)
        if material_match:
            material = material_match.group(1).strip()
            self.blueprints[name]["materials"]["exterior"] = material
            modifications.append(f"exterior material to {material}")
        
        # Mobility modifications
        if "bipedal" in text_lower:
            self.blueprints[name]["mobility"]["locomotion"] = "bipedal"
            modifications.append("locomotion to bipedal")
        elif "quadrupedal" in text_lower:
            self.blueprints[name]["mobility"]["locomotion"] = "quadrupedal"
            modifications.append("locomotion to quadrupedal")
        elif "wheeled" in text_lower:
            self.blueprints[name]["mobility"]["locomotion"] = "wheeled"
            modifications.append("locomotion to wheeled")
        
        # Speed modifications
        speed_match = re.search(r"(?:speed|velocity) (?:to|of|:)? ?(\d+(?:\.\d+)?)(?: ?km/?h)?", text_lower)
        if speed_match:
            speed = float(speed_match.group(1))
            self.blueprints[name]["mobility"]["max_speed"] = speed
            modifications.append(f"maximum speed to {speed} km/h")
        
        # If no specific modifications were detected
        if not modifications:
            return "I couldn't determine what aspects of the blueprint you want to modify. You can change height, weight, materials, mobility type, and more."
        
        # Update timestamp
        self.blueprints[name]["modified"] = time.time()
        
        # Save the modified blueprint
        self._save_blueprint(name)
        
        return f"I've updated the '{name}' blueprint, changing {', '.join(modifications)}. The changes have been saved."
    
    def _list_blueprints(self):
        """
        List all available blueprints.
        
        Returns:
            str: Blueprint list
        """
        if not self.blueprints:
            return "No blueprints available. You can create a new blueprint with 'create blueprint'."
        
        response = "Available Blueprints:\n\n"
        
        for name, blueprint in self.blueprints.items():
            # Format creation time
            created = time.strftime("%Y-%m-%d", time.localtime(blueprint.get("created", 0)))
            
            # Mark current blueprint
            current = " (current)" if name == self.current_blueprint else ""
            
            # Add basic info
            response += f"- {name}{current}: {blueprint['type']} robot, {blueprint['height']} cm tall, created on {created}\n"
        
        response += "\nYou can view details with 'show blueprint [name]' or modify with 'modify blueprint [name]'."
        
        return response
    
    def _show_blueprint_details(self, text):
        """
        Show detailed information about a blueprint.
        
        Args:
            text: Request text
            
        Returns:
            str: Blueprint details
        """
        # Extract blueprint name if provided
        import re
        name_match = re.search(r"blueprint ['\"]?([a-zA-Z0-9_]+)['\"]?", text.lower())
        
        if name_match:
            name = name_match.group(1)
            if name not in self.blueprints:
                return f"I couldn't find a blueprint named '{name}'. Available blueprints: {', '.join(self.blueprints.keys())}"
        else:
            # Use current blueprint
            if not self.current_blueprint:
                return "No blueprint is currently selected. Please specify which blueprint you want to view."
            name = self.current_blueprint
        
        blueprint = self.blueprints[name]
        
        # Format creation time
        created = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(blueprint.get("created", 0)))
        
        # Format details
        response = f"Blueprint: {name} (Version {blueprint.get('version', '1.0')})\n"
        response += f"Created: {created}\n\n"
        
        response += f"Type: {blueprint['type']}\n"
        response += f"Dimensions: {blueprint['height']} cm tall, {blueprint['weight']} kg\n\n"
        
        response += "Materials:\n"
        for part, material in blueprint['materials'].items():
            response += f"- {part.capitalize()}: {material}\n"
        
        response += "\nPower System:\n"
        response += f"- Type: {blueprint['power']['type']}\n"
        response += f"- Battery: {blueprint['power']['battery_capacity']} mAh\n"
        response += f"- Runtime: {blueprint['power']['estimated_runtime']} hours\n"
        
        response += "\nMobility:\n"
        response += f"- Type: {blueprint['mobility']['locomotion']}\n"
        response += f"- Max Speed: {blueprint['mobility']['max_speed']} km/h\n"
        response += f"- Terrain: {', '.join(blueprint['mobility']['terrain_capability'])}\n"
        
        response += "\nSensors:\n"
        for sensor in blueprint['sensors']:
            response += f"- {sensor['count']}x {sensor['subtype']} ({sensor['type']})\n"
            response += f"  Positions: {', '.join(sensor['positions'])}\n"
        
        response += "\nActuators:\n"
        for actuator, value in blueprint['actuators'].items():
            response += f"- {actuator.replace('_', ' ').capitalize()}: {value}\n"
        
        response += "\nCommunication: " + ", ".join(blueprint['communication'])
        
        return response
    
    def _handle_generate_blueprint(self, text):
        """
        Generate a detailed blueprint based on text description.
        
        Args:
            text: Description text
            
        Returns:
            str: Response
        """
        text_lower = text.lower()
        
        # Extract blueprint name if provided
        import re
        name_match = re.search(r"blueprint ['\"]?([a-zA-Z0-9_]+)['\"]?", text_lower)
        
        if name_match:
            name = name_match.group(1)
        else:
            name = f"generated_{int(time.time())}"
        
        # Start with default template
        new_blueprint = self.default_blueprint.copy()
        new_blueprint["created"] = time.time()
        
        # Extract robot type
        if "humanoid" in text_lower:
            new_blueprint["type"] = "humanoid"
        elif "quadruped" in text_lower:
            new_blueprint["type"] = "quadruped"
            new_blueprint["mobility"]["locomotion"] = "quadrupedal"
            new_blueprint["actuators"]["arms"] = 0
            new_blueprint["actuators"]["legs"] = 4
        elif "wheeled" in text_lower:
            new_blueprint["type"] = "wheeled"
            new_blueprint["mobility"]["locomotion"] = "wheeled"
            new_blueprint["actuators"]["legs"] = 0
            
        # Extract size
        size_matches = {
            "small": {"height": 100, "weight": 30},
            "medium": {"height": 150, "weight": 50},
            "large": {"height": 180, "weight": 75},
            "tall": {"height": 200, "weight": 90}
        }
        
        for size_word, dimensions in size_matches.items():
            if size_word in text_lower:
                new_blueprint["height"] = dimensions["height"]
                new_blueprint["weight"] = dimensions["weight"]
                break
        
        # Extract specific height if provided
        height_match = re.search(r"(\d+)(?: ?cm)? tall", text_lower)
        if height_match:
            new_blueprint["height"] = int(height_match.group(1))
        
        # Extract material preferences
        materials = {
            "metal": "aluminum alloy",
            "plastic": "high-density polymer",
            "soft": "silicone elastomer",
            "carbon": "carbon fiber",
            "titanium": "titanium alloy",
            "steel": "stainless steel"
        }
        
        for material_word, material_type in materials.items():
            if material_word in text_lower:
                new_blueprint["materials"]["exterior"] = material_type
                break
        
        # Extract capability preferences
        if "fast" in text_lower or "speed" in text_lower:
            new_blueprint["mobility"]["max_speed"] = 10.0  # Faster than default
        
        if "strong" in text_lower or "strength" in text_lower:
            # Add strength-related characteristics
            new_blueprint["actuators"]["lifting_capacity_kg"] = 50
        
        if "dexterous" in text_lower or "dexterity" in text_lower:
            # Enhance hand capabilities
            new_blueprint["actuators"]["fingers_per_hand"] = 5
            new_blueprint["actuators"]["finger_joints_per_finger"] = 3
        
        # Additional sensors based on needs
        if "night vision" in text_lower or "dark" in text_lower:
            new_blueprint["sensors"].append({
                "type": "visual",
                "subtype": "infrared_camera",
                "count": 2,
                "positions": ["head_front"]
            })
        
        if "temperature" in text_lower or "heat" in text_lower:
            new_blueprint["sensors"].append({
                "type": "environmental",
                "subtype": "temperature_sensor",
                "count": 4,
                "positions": ["exterior_body"]
            })
        
        # Save the new blueprint
        self.blueprints[name] = new_blueprint
        self.current_blueprint = name
        self._save_blueprint(name)
        
        return f"I've generated a detailed blueprint named '{name}' based on your description. Type 'show blueprint {name}' to see the full specifications."
    
    def _provide_blueprint_info(self):
        """
        Provide general information about blueprints.
        
        Returns:
            str: Informational response
        """
        info_responses = [
            "I can help you design robot body blueprints. You can create, modify, or generate detailed specifications for potential physical embodiments.",
            "Robot blueprints define the physical characteristics of a robot body. I can help you design everything from humanoid forms to specialized robotic platforms.",
            "Would you like to create a new robot blueprint? You can specify characteristics like height, weight, materials, and mobility capabilities.",
            "Robot blueprints are the first step toward physical embodiment. They specify all the physical characteristics needed to construct a compatible robot body.",
            "I currently have blueprints for various robot types. You can view them with 'list blueprints' or create a new one with 'create blueprint'."
        ]
        
        return random.choice(info_responses)
    
    def generate_blueprint(self, description=None, name=None):
        """
        Generate a blueprint based on description.
        Interface for other brain modules to use.
        
        Args:
            description: Text description of desired robot
            name: Name for the blueprint
            
        Returns:
            dict: Generated blueprint data
        """
        if not name:
            name = f"generated_{int(time.time())}"
        
        # Start with default template
        new_blueprint = self.default_blueprint.copy()
        new_blueprint["created"] = time.time()
        
        # Modify based on description if provided
        if description:
            text_lower = description.lower()
            
            # Simple rule-based modifications
            if "small" in text_lower:
                new_blueprint["height"] = 100
                new_blueprint["weight"] = 30
            elif "large" in text_lower:
                new_blueprint["height"] = 200
                new_blueprint["weight"] = 90
            
            if "fast" in text_lower:
                new_blueprint["mobility"]["max_speed"] = 10.0
            
            if "humanoid" in text_lower:
                new_blueprint["type"] = "humanoid"
            elif "quadruped" in text_lower:
                new_blueprint["type"] = "quadruped"
                new_blueprint["mobility"]["locomotion"] = "quadrupedal"
            elif "wheeled" in text_lower:
                new_blueprint["type"] = "wheeled"
                new_blueprint["mobility"]["locomotion"] = "wheeled"
                
        # Save the new blueprint
        self.blueprints[name] = new_blueprint
        self.current_blueprint = name
        self._save_blueprint(name)
        
        return {"name": name, "blueprint": new_blueprint}
    
    def get_blueprint(self, name=None):
        """
        Get a specific blueprint or the current one.
        
        Args:
            name: Blueprint name or None for current
            
        Returns:
            dict: Blueprint data or None if not found
        """
        if name:
            return self.blueprints.get(name)
        elif self.current_blueprint:
            return self.blueprints.get(self.current_blueprint)
        else:
            return None
