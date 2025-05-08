#!/usr/bin/env python3
"""
safety_brain.py: Provides safety monitoring and assistance.
"""

import time
import random
from brains.base_brain import BaseBrain

class SafetyBrain(BaseBrain):
    """
    Safety Brain responsible for monitoring personal safety.
    Provides safety tips, emergency resources, and protective guidance.
    """
    
    def __init__(self):
        """Initialize the Safety Brain."""
        super().__init__("Safety")
        self.digital_soul = None  # Will be set by orchestrator
        self.safety_categories = [
            "home", "travel", "online", "emergency", "weather", 
            "personal", "health", "fire", "vehicle"
        ]
        self.emergency_contacts = []
        self.safety_plan = {}
        self.last_safety_tip = 0
        self.tip_interval = 43200  # Seconds between tips (12 hours)
        
    def process_input(self, input_data):
        """
        Process input data for safety-related queries.
        
        Args:
            input_data: Input data to process
            
        Returns:
            str: Response with safety information or None
        """
        super().process_input(input_data)
        
        # Handle cycle updates
        if input_data == "Cycle update":
            return self._check_for_safety_tip()
        
        # Skip if not safety-related
        if not self._is_safety_related(input_data):
            return None
        
        try:
            # Parse the input to determine the type of safety request
            safety_type = self._identify_safety_type(input_data)
            
            # Generate appropriate response
            if safety_type == "emergency":
                return self._handle_emergency_request(input_data)
            elif safety_type == "contacts":
                return self._handle_contact_request(input_data)
            elif safety_type == "plan":
                return self._handle_safety_plan_request(input_data)
            elif safety_type in self.safety_categories:
                return self._generate_safety_tip(safety_type)
            else:
                return self._generate_general_safety_tip()
            
        except Exception as e:
            self.logger.error(f"Error processing safety input: {e}")
            self.stats["error_count"] += 1
            return None
    
    def _is_safety_related(self, text):
        """
        Determine if input is related to safety.
        
        Args:
            text: Input text
            
        Returns:
            bool: True if safety-related
        """
        text_lower = text.lower()
        
        # Check for safety-related keywords
        safety_keywords = [
            "safety", "safe", "danger", "dangerous", "emergency", "urgent",
            "help", "sos", "911", "fire", "accident", "security", "protect",
            "alarm", "alert", "warning", "risk", "hazard", "threat", "secure",
            "lock", "password", "privacy", "guard", "defense", "prevention"
        ]
        
        return any(keyword in text_lower for keyword in safety_keywords)
    
    def _identify_safety_type(self, text):
        """
        Identify the type of safety request.
        
        Args:
            text: Input text
            
        Returns:
            str: Safety request type
        """
        text_lower = text.lower()
        
        # Check for emergency situations
        if any(word in text_lower for word in ["emergency", "urgent", "immediate", "help now", "sos", "911", "crisis"]):
            return "emergency"
        
        # Check for emergency contact requests
        if any(phrase in text_lower for phrase in ["emergency contact", "emergency number", "safety contact", "add contact"]):
            return "contacts"
        
        # Check for safety plan requests
        if any(phrase in text_lower for phrase in ["safety plan", "emergency plan", "evacuation", "disaster plan"]):
            return "plan"
        
        # Check for specific safety categories
        for category in self.safety_categories:
            if category in text_lower:
                return category
            
        # Some additional common mappings
        if any(word in text_lower for word in ["house", "apartment", "bedroom", "kitchen", "bathroom"]):
            return "home"
        elif any(word in text_lower for word in ["car", "drive", "driving", "road", "transportation"]):
            return "vehicle"
        elif any(word in text_lower for word in ["internet", "cyber", "digital", "password", "hacker", "phishing"]):
            return "online"
        elif any(word in text_lower for word in ["trip", "travel", "vacation", "journey", "abroad", "foreign"]):
            return "travel"
        elif any(word in text_lower for word in ["storm", "hurricane", "tornado", "flood", "earthquake", "natural disaster"]):
            return "weather"
        
        # Default to general safety
        return "general"
    
    def _handle_emergency_request(self, text):
        """
        Handle emergency-related requests.
        
        Args:
            text: Request text
            
        Returns:
            str: Emergency response
        """
        # Note: This is a simulated emergency response
        # In a real implementation, this would have more sophisticated logic
        
        emergency_responses = [
            "If this is a life-threatening emergency, please call emergency services immediately (911 in the US).",
            "I'm unable to directly contact emergency services for you. Please call 911 (or your local emergency number) if you need immediate help.",
            "For medical emergencies, call 911 or your local emergency number right away. Don't wait.",
            "Emergency situations require immediate professional help. Please contact emergency services directly."
        ]
        
        return emergency_responses[0] + "\n\n" + emergency_responses[1]
    
    def _handle_contact_request(self, text):
        """
        Handle emergency contact-related requests.
        
        Args:
            text: Request text
            
        Returns:
            str: Contact management response
        """
        text_lower = text.lower()
        
        # Check if this is adding a contact
        if any(phrase in text_lower for phrase in ["add contact", "save contact", "new contact"]):
            # Simple parsing for contact information
            # In a real implementation, this would be more robust
            if "name:" in text_lower and "number:" in text_lower:
                name_start = text_lower.find("name:") + 5
                name_end = text_lower.find("number:") - 1 if "number:" in text_lower else len(text_lower)
                name = text[name_start:name_end].strip()
                
                number_start = text_lower.find("number:") + 7
                number = text[number_start:].strip()
                
                # Add contact
                self.emergency_contacts.append({
                    "name": name,
                    "number": number
                })
                
                return f"I've added {name} as an emergency contact with number {number}."
            else:
                return "To add an emergency contact, please provide their name and number in this format: 'Add emergency contact name: John Doe number: 555-123-4567'."
        
        # Check if this is viewing contacts
        elif any(phrase in text_lower for phrase in ["list contacts", "show contacts", "view contacts", "my contacts"]):
            if not self.emergency_contacts:
                return "You don't have any emergency contacts saved yet. To add one, say something like 'Add emergency contact name: John Doe number: 555-123-4567'."
            
            response = "Your emergency contacts:\n"
            for i, contact in enumerate(self.emergency_contacts, 1):
                response += f"{i}. {contact['name']}: {contact['number']}\n"
            
            return response
        
        # Default response
        return "I can help you manage emergency contacts. You can add a new contact or view your saved contacts."
    
    def _handle_safety_plan_request(self, text):
        """
        Handle safety plan-related requests.
        
        Args:
            text: Request text
            
        Returns:
            str: Safety plan response
        """
        text_lower = text.lower()
        
        # Check if this is creating/updating a plan
        if any(phrase in text_lower for phrase in ["create plan", "make plan", "update plan", "new plan"]):
            return "Creating a safety plan is an important step. Consider including:\n\n" + \
                   "1. Emergency contacts\n" + \
                   "2. Meeting points for family members\n" + \
                   "3. Evacuation routes\n" + \
                   "4. Location of emergency supplies\n" + \
                   "5. Special considerations for children, elderly, or pets\n\n" + \
                   "Would you like me to help you create a specific type of safety plan?"
        
        # Check if this is viewing the plan
        elif any(phrase in text_lower for phrase in ["view plan", "show plan", "see plan", "my plan"]):
            if not self.safety_plan:
                return "You don't have a safety plan saved yet. Would you like to create one?"
            
            response = "Your safety plan:\n"
            for category, details in self.safety_plan.items():
                response += f"\n{category.title()}:\n"
                for item in details:
                    response += f"- {item}\n"
            
            return response
        
        # Default response
        return "I can help you create and manage safety plans for different situations like home emergencies, natural disasters, or travel safety."
    
    def _generate_safety_tip(self, category):
        """
        Generate a safety tip for a specific category.
        
        Args:
            category: Safety category
            
        Returns:
            str: Safety tip
        """
        tips = {
            "home": [
                "Test smoke and carbon monoxide detectors monthly and replace batteries at least once a year.",
                "Keep a fire extinguisher in an accessible location and know how to use it.",
                "Create and practice a home evacuation plan with all household members.",
                "Keep emergency numbers posted where everyone can find them quickly.",
                "Consider installing smart home security devices for additional protection."
            ],
            "travel": [
                "Research your destination before traveling, including local emergency services and health facilities.",
                "Keep digital and physical copies of important documents like passports and insurance information.",
                "Share your itinerary with a trusted friend or family member who isn't traveling with you.",
                "Be aware of your surroundings, especially in unfamiliar locations.",
                "Consider travel insurance that covers medical emergencies and evacuation."
            ],
            "online": [
                "Use strong, unique passwords for each of your important accounts and consider a password manager.",
                "Enable two-factor authentication whenever possible for additional security.",
                "Be cautious about the information you share online, especially personal details.",
                "Regularly update your devices and applications to patch security vulnerabilities.",
                "Be skeptical of unexpected emails, messages, or calls asking for personal information."
            ],
            "emergency": [
                "Keep an emergency kit with essentials like water, non-perishable food, medications, and first aid supplies.",
                "Have a plan for communicating with family members during emergencies when normal channels may be unavailable.",
                "Know multiple evacuation routes from your home and community.",
                "Store important documents in a waterproof, fireproof container or digitally in secure cloud storage.",
                "Consider learning basic first aid and CPR skills."
            ],
            "weather": [
                "Stay informed about severe weather through local news, weather apps, or NOAA weather radio.",
                "Know the safe locations in your home for different types of weather emergencies.",
                "Prepare an emergency kit specifically for weather-related events common in your area.",
                "Have backup power sources like portable chargers or generators for extended outages.",
                "If advised to evacuate due to severe weather, do so promptly."
            ],
            "personal": [
                "Trust your instincts—if a situation feels unsafe, remove yourself if possible.",
                "When meeting someone new, consider doing so in public places, especially for first meetings.",
                "Let someone know your plans, including when to expect your return, when going out.",
                "Keep your phone charged and easily accessible for emergency calls.",
                "Consider using personal safety apps that can quickly alert contacts if needed."
            ],
            "health": [
                "Keep a list of current medications, allergies, and medical conditions easily accessible.",
                "Wear medical alert jewelry if you have serious medical conditions.",
                "Know the warning signs of common medical emergencies like heart attack or stroke.",
                "Keep basic first aid supplies at home and in your vehicle.",
                "Stay current with recommended vaccinations and health screenings."
            ],
            "fire": [
                "Never leave cooking unattended on the stove or in the oven.",
                "Keep flammable items away from heat sources like stoves, heaters, and candles.",
                "Have working smoke detectors on each level of your home and in each bedroom.",
                "Plan and practice two ways out of each room in case of fire.",
                "Sleep with bedroom doors closed to slow the spread of fire and smoke."
            ],
            "vehicle": [
                "Regularly maintain your vehicle, including safety systems like brakes and tires.",
                "Keep an emergency kit in your vehicle with items like jumper cables, flashlight, and first aid supplies.",
                "Avoid distracted driving—focus on the road, not phones or other devices.",
                "Always wear seat belts and ensure children are in appropriate car seats.",
                "Know what to do if your vehicle breaks down, including safe locations to pull over."
            ]
        }
        
        # Get tips for the requested category
        category_tips = tips.get(category, tips["personal"])
        
        # Select a random tip
        tip = random.choice(category_tips)
        
        # Add a general intro
        category_name = category.capitalize()
        intro = f"Safety Tip ({category_name}): "
        
        return intro + tip
    
    def _generate_general_safety_tip(self):
        """
        Generate a general safety tip.
        
        Returns:
            str: Safety tip
        """
        general_tips = [
            "Preparation is key to safety—take time to create and practice emergency plans.",
            "Keep emergency contact information readily available for yourself and family members.",
            "Consider taking first aid and CPR courses to be prepared for emergency situations.",
            "Regularly review and update your safety preparations as circumstances change.",
            "Small safety precautions, taken consistently, can significantly reduce risks in daily life."
        ]
        
        return "Safety Tip: " + random.choice(general_tips)
    
    def _check_for_safety_tip(self):
        """
        Check if it's time for a safety tip.
        
        Returns:
            str: Safety tip or None
        """
        current_time = time.time()
        
        # Only provide tips periodically
        if current_time - self.last_safety_tip < self.tip_interval:
            return None
        
        self.last_safety_tip = current_time
        
        # Select a random category
        category = random.choice(self.safety_categories)
        
        # Generate a tip for that category
        return self._generate_safety_tip(category)
    
    def add_emergency_contact(self, name, number):
        """
        Add an emergency contact.
        
        Args:
            name: Contact name
            number: Contact phone number
            
        Returns:
            bool: True if added successfully
        """
        self.emergency_contacts.append({
            "name": name,
            "number": number
        })
        return True
    
    def add_safety_plan_item(self, category, item):
        """
        Add an item to the safety plan.
        
        Args:
            category: Plan category
            item: Plan item
            
        Returns:
            bool: True if added successfully
        """
        if category not in self.safety_plan:
            self.safety_plan[category] = []
        
        self.safety_plan[category].append(item)
        return True
