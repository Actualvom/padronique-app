#!/usr/bin/env python3
"""
personal_care_brain.py: Provides personal care and wellness assistance.
"""

import time
import random
import re
from brains.base_brain import BaseBrain

class PersonalCareBrain(BaseBrain):
    """
    Personal Care Brain responsible for wellness suggestions and self-care.
    Helps with reminders, wellness tips, and personal routines.
    """
    
    def __init__(self):
        """Initialize the Personal Care Brain."""
        super().__init__("PersonalCare")
        self.digital_soul = None  # Will be set by orchestrator
        self.care_areas = [
            "hydration", "sleep", "exercise", "nutrition", 
            "mental_health", "relaxation", "social", "hygiene"
        ]
        self.reminders = {}  # User-set reminders
        self.last_care_suggestion = 0
        self.suggestion_interval = 3600  # Seconds between suggestions (1 hour)
    
    def process_input(self, input_data):
        """
        Process input data for personal care related queries.
        
        Args:
            input_data: Input data to process
            
        Returns:
            str: Response with care suggestions or None
        """
        super().process_input(input_data)
        
        # Handle cycle updates
        if input_data == "Cycle update":
            return self._check_for_reminder()
        
        # Skip if not care-related
        if not self._is_care_related(input_data):
            return None
        
        try:
            # Parse the input to determine the type of care request
            care_type = self._identify_care_type(input_data)
            
            # Generate appropriate response
            if "reminder" in care_type:
                return self._handle_reminder_request(input_data)
            elif care_type in self.care_areas:
                return self._generate_care_suggestion(care_type)
            else:
                return self._generate_general_care_suggestion()
            
        except Exception as e:
            self.logger.error(f"Error processing care input: {e}")
            self.stats["error_count"] += 1
            return None
    
    def _is_care_related(self, text):
        """
        Determine if input is related to personal care.
        
        Args:
            text: Input text
            
        Returns:
            bool: True if care-related
        """
        text_lower = text.lower()
        
        # Check for care-related keywords
        care_keywords = [
            "reminder", "remind me", "don't forget", "health", "wellness",
            "self-care", "hydrate", "water", "sleep", "rest", "exercise",
            "workout", "eat", "food", "meal", "diet", "stress", "relax",
            "meditate", "breathe", "shower", "hygiene", "break", "tired"
        ]
        
        return any(keyword in text_lower for keyword in care_keywords)
    
    def _identify_care_type(self, text):
        """
        Identify the type of care request.
        
        Args:
            text: Input text
            
        Returns:
            str: Care type
        """
        text_lower = text.lower()
        
        # Check for reminder requests
        if any(word in text_lower for word in ["remind", "reminder", "don't forget", "alert"]):
            return "reminder"
        
        # Check for specific care areas
        for area in self.care_areas:
            if area in text_lower or self._get_area_keywords(area, text_lower):
                return area
        
        # Default to general care
        return "general"
    
    def _get_area_keywords(self, area, text):
        """
        Check if text contains keywords for a specific care area.
        
        Args:
            area: Care area to check
            text: Text to search in
            
        Returns:
            bool: True if area keywords are present
        """
        area_keywords = {
            "hydration": ["water", "drink", "thirsty", "dehydrated", "hydrate"],
            "sleep": ["sleep", "tired", "rest", "nap", "bed", "drowsy"],
            "exercise": ["exercise", "workout", "move", "stretch", "walk", "run", "gym"],
            "nutrition": ["food", "eat", "meal", "diet", "hungry", "nutrition", "snack"],
            "mental_health": ["stress", "anxiety", "depression", "mental", "therapy", "mood"],
            "relaxation": ["relax", "calm", "peace", "meditate", "breathe", "break"],
            "social": ["friend", "family", "connect", "talk", "social", "relationship"],
            "hygiene": ["shower", "bath", "clean", "wash", "hygiene", "teeth", "dental"]
        }
        
        keywords = area_keywords.get(area, [])
        return any(keyword in text for keyword in keywords)
    
    def _handle_reminder_request(self, text):
        """
        Handle a request to set a reminder.
        
        Args:
            text: Request text
            
        Returns:
            str: Response
        """
        # Parse time information (simplified)
        time_patterns = [
            r"in (\d+) (minute|minutes|min|mins|hour|hours|day|days)",
            r"at (\d+):(\d+) (am|pm)",
            r"at (\d+) (am|pm)",
            r"tomorrow at (\d+):(\d+)",
            r"tomorrow at (\d+) (am|pm)"
        ]
        
        reminder_time = None
        for pattern in time_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                # This is a simplified placeholder for time parsing
                # In a real implementation, parse the time properly
                reminder_time = time.time() + 3600  # Default to 1 hour from now
                break
        
        # Parse reminder content
        content_match = re.search(r"remind me to (.+?)(in|at|tomorrow|$)", text, re.IGNORECASE)
        if content_match:
            content = content_match.group(1).strip()
        else:
            content = "your reminder"
        
        # Set reminder
        if reminder_time:
            reminder_id = str(int(time.time()))
            self.reminders[reminder_id] = {
                "time": reminder_time,
                "content": content,
                "notified": False
            }
            
            # Format time for display
            display_time = time.strftime("%I:%M %p", time.localtime(reminder_time))
            
            return f"I'll remind you to {content} at {display_time}."
        else:
            return "I couldn't understand when to set the reminder. Please specify a time like 'in 30 minutes' or 'at 3 pm'."
    
    def _check_for_reminder(self):
        """
        Check if any reminders are due.
        
        Returns:
            str: Reminder message or None
        """
        current_time = time.time()
        due_reminders = []
        
        for reminder_id, reminder in list(self.reminders.items()):
            if current_time >= reminder["time"] and not reminder["notified"]:
                due_reminders.append(reminder["content"])
                reminder["notified"] = True
                
                # Remove old reminders that are more than a day old
                if current_time - reminder["time"] > 86400:  # 24 hours
                    self.reminders.pop(reminder_id)
        
        if due_reminders:
            if len(due_reminders) == 1:
                return f"Reminder: {due_reminders[0]}"
            else:
                reminder_list = "\n".join([f"- {item}" for item in due_reminders])
                return f"You have several reminders:\n{reminder_list}"
        
        # Check if it's time for a random care suggestion
        if current_time - self.last_care_suggestion > self.suggestion_interval:
            self.last_care_suggestion = current_time
            return self._generate_random_care_suggestion()
        
        return None
    
    def _generate_care_suggestion(self, care_type):
        """
        Generate a suggestion for a specific care area.
        
        Args:
            care_type: Type of care to suggest
            
        Returns:
            str: Care suggestion
        """
        suggestions = {
            "hydration": [
                "Remember to stay hydrated. Have you had enough water today?",
                "Staying hydrated improves focus and energy. Consider having a glass of water now.",
                "Proper hydration supports overall health. Do you need a water break?"
            ],
            "sleep": [
                "Quality sleep is essential for cognitive function. Are you getting enough rest?",
                "A consistent sleep schedule helps maintain your body's rhythm. Try to keep regular hours.",
                "If you're feeling tired, a short power nap of 15-20 minutes can be rejuvenating."
            ],
            "exercise": [
                "Regular movement keeps your body and mind healthy. Consider taking a short walk.",
                "Even a few minutes of stretching can improve circulation and reduce tension.",
                "Physical activity boosts mood and energy. What type of movement do you enjoy?"
            ],
            "nutrition": [
                "Regular, balanced meals help maintain energy and focus. Have you eaten recently?",
                "Try to include a variety of nutrients in your diet for optimal health.",
                "Mindful eating helps you enjoy your food and recognize hunger cues better."
            ],
            "mental_health": [
                "Taking time for your mental health is important. How are you feeling today?",
                "Short mindfulness breaks can help reduce stress and improve focus.",
                "It's okay to set boundaries and prioritize your emotional wellbeing."
            ],
            "relaxation": [
                "Taking breaks helps prevent burnout. Consider a brief relaxation moment.",
                "Deep breathing for just a minute can help reduce stress and center your thoughts.",
                "Finding moments of calm throughout your day supports overall wellbeing."
            ],
            "social": [
                "Social connections contribute to wellbeing. Have you connected with someone today?",
                "Even brief social interactions can boost mood and reduce feelings of isolation.",
                "Quality time with loved ones is an important part of a balanced life."
            ],
            "hygiene": [
                "Good personal hygiene supports both physical health and confidence.",
                "Taking care of yourself through regular grooming routines can be a form of self-respect.",
                "Simple hygiene practices help prevent illness and promote overall wellness."
            ]
        }
        
        # Get suggestions for the requested care type
        care_suggestions = suggestions.get(care_type, suggestions["relaxation"])
        
        # Select a random suggestion
        suggestion = random.choice(care_suggestions)
        
        return suggestion
    
    def _generate_general_care_suggestion(self):
        """
        Generate a general personal care suggestion.
        
        Returns:
            str: Care suggestion
        """
        general_suggestions = [
            "Taking moments for self-care throughout your day supports overall wellbeing.",
            "Small wellness habits add up to significant benefits over time.",
            "Balancing different aspects of self-care creates a foundation for overall health.",
            "What's one small thing you could do right now to support your wellbeing?",
            "Remember that self-care isn't selfish—it's necessary for sustainable energy and focus."
        ]
        
        return random.choice(general_suggestions)
    
    def _generate_random_care_suggestion(self):
        """
        Generate a random care suggestion from any category.
        
        Returns:
            str: Care suggestion
        """
        # Select a random care area
        care_type = random.choice(self.care_areas)
        
        # Get a suggestion for that area
        return self._generate_care_suggestion(care_type)
    
    def set_suggestion_interval(self, interval_seconds):
        """
        Set the interval between automatic care suggestions.
        
        Args:
            interval_seconds: Seconds between suggestions
            
        Returns:
            bool: True if set successfully
        """
        if interval_seconds < 0:
            return False
        
        self.suggestion_interval = interval_seconds
        return True
