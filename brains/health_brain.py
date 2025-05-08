#!/usr/bin/env python3
"""
health_brain.py: Monitors and provides health-related assistance.
"""

import time
import random
import re
from datetime import datetime, timedelta
from brains.base_brain import BaseBrain

class HealthBrain(BaseBrain):
    """
    Health Brain responsible for health monitoring and wellness.
    Provides health information, tracking, and personalized recommendations.
    """
    
    def __init__(self):
        """Initialize the Health Brain."""
        super().__init__("Health")
        self.digital_soul = None  # Will be set by orchestrator
        self.health_data = {
            "vitals": [],
            "medications": [],
            "conditions": [],
            "allergies": [],
            "exercise_log": [],
            "sleep_log": [],
            "nutrition_log": []
        }
        self.last_health_check = 0
        self.check_interval = 86400  # Seconds between health checks (1 day)
    
    def process_input(self, input_data):
        """
        Process input data for health-related queries.
        
        Args:
            input_data: Input data to process
            
        Returns:
            str: Response with health information or None
        """
        super().process_input(input_data)
        
        # Handle cycle updates
        if input_data == "Cycle update":
            return self._check_health_alerts()
        
        # Skip if not health-related
        if not self._is_health_related(input_data):
            return None
        
        try:
            # Identify the health topic
            health_topic = self._identify_health_topic(input_data)
            
            # Handle different types of health queries
            if health_topic == "log":
                return self._handle_health_logging(input_data)
            elif health_topic == "track":
                return self._handle_tracking_request(input_data)
            elif health_topic == "query":
                return self._handle_health_query(input_data)
            elif health_topic == "medications":
                return self._handle_medication_query(input_data)
            else:
                return self._generate_general_health_info()
            
        except Exception as e:
            self.logger.error(f"Error processing health input: {e}")
            self.stats["error_count"] += 1
            return None
    
    def _is_health_related(self, text):
        """
        Determine if input is related to health.
        
        Args:
            text: Input text
            
        Returns:
            bool: True if health-related
        """
        text_lower = text.lower()
        
        # Check for health-related keywords
        health_keywords = [
            "health", "medical", "doctor", "symptom", "pain", "hurt", "ill", "sick",
            "disease", "condition", "medication", "medicine", "drug", "treatment",
            "therapy", "allergy", "allergic", "blood pressure", "heart rate",
            "temperature", "fever", "diagnosis", "checkup", "appointment", "exercise",
            "workout", "fitness", "nutrition", "diet", "vitamin", "supplement",
            "sleep", "rest", "recovery", "headache", "migraine", "pain"
        ]
        
        return any(keyword in text_lower for keyword in health_keywords)
    
    def _identify_health_topic(self, text):
        """
        Identify the health topic in the text.
        
        Args:
            text: Input text
            
        Returns:
            str: Health topic
        """
        text_lower = text.lower()
        
        # Check if this is a logging request
        if any(word in text_lower for word in ["log", "record", "track", "note", "journal"]):
            return "log"
        
        # Check if this is a tracking request
        if any(word in text_lower for word in ["trend", "progress", "history", "chart"]):
            return "track"
        
        # Check if this is a medication query
        if any(word in text_lower for word in ["medication", "medicine", "drug", "pill", "prescription"]):
            return "medications"
        
        # Check if this is a general health query
        if any(word in text_lower for word in ["what", "how", "when", "why", "should", "can", "?"]):
            return "query"
        
        # Default to general health
        return "general"
    
    def _handle_health_logging(self, text):
        """
        Handle a request to log health information.
        
        Args:
            text: Request text
            
        Returns:
            str: Response
        """
        text_lower = text.lower()
        timestamp = time.time()
        date_str = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d")
        
        # Determine what type of health data to log
        if any(word in text_lower for word in ["sleep", "slept", "nap", "rest"]):
            # Extract sleep duration (simplified)
            hours_match = re.search(r"(\d+\.?\d*)\s*(hour|hours|hr|hrs)", text_lower)
            hours = float(hours_match.group(1)) if hours_match else None
            
            if hours is not None:
                self.health_data["sleep_log"].append({
                    "date": date_str,
                    "hours": hours,
                    "timestamp": timestamp
                })
                return f"I've logged {hours} hours of sleep for {date_str}."
            else:
                return "Could you specify how many hours you slept? For example, 'I slept 7 hours last night.'"
        
        elif any(word in text_lower for word in ["exercise", "workout", "ran", "walk", "fitness"]):
            # Extract exercise details (simplified)
            activity_match = re.search(r"(ran|walked|swam|cycled|did|performed) (.+?) for (\d+) (minute|minutes|min|mins)", text_lower)
            if activity_match:
                activity = activity_match.group(2)
                duration = int(activity_match.group(3))
                
                self.health_data["exercise_log"].append({
                    "date": date_str,
                    "activity": activity,
                    "duration_minutes": duration,
                    "timestamp": timestamp
                })
                return f"I've logged {duration} minutes of {activity} for {date_str}."
            else:
                return "Could you provide more details about your exercise? For example, 'I walked for 30 minutes today.'"
        
        elif any(word in text_lower for word in ["ate", "eat", "food", "meal", "nutrition", "diet"]):
            # Extract meal information (simplified)
            food_match = re.search(r"(ate|had|consumed) (.+)", text_lower)
            if food_match:
                food = food_match.group(2)
                
                self.health_data["nutrition_log"].append({
                    "date": date_str,
                    "food": food,
                    "timestamp": timestamp
                })
                return f"I've logged your meal: {food} for {date_str}."
            else:
                return "Could you specify what you ate? For example, 'I ate a salad for lunch.'"
        
        elif any(word in text_lower for word in ["blood pressure", "bp"]):
            # Extract blood pressure reading (simplified)
            bp_match = re.search(r"(\d+)/(\d+)", text_lower)
            if bp_match:
                systolic = int(bp_match.group(1))
                diastolic = int(bp_match.group(2))
                
                self.health_data["vitals"].append({
                    "date": date_str,
                    "type": "blood_pressure",
                    "value": {"systolic": systolic, "diastolic": diastolic},
                    "timestamp": timestamp
                })
                return f"I've logged your blood pressure: {systolic}/{diastolic} for {date_str}."
            else:
                return "Could you provide your blood pressure reading in the format 'systolic/diastolic'? For example, '120/80'."
        
        # Default response for unspecified health logging
        return "I can help you log health information like sleep, exercise, nutrition, or vital signs. Please provide specific details."
    
    def _handle_tracking_request(self, text):
        """
        Handle a request to track or view health data trends.
        
        Args:
            text: Request text
            
        Returns:
            str: Response with trend information
        """
        text_lower = text.lower()
        
        # Determine what health data to track
        if "sleep" in text_lower:
            return self._generate_sleep_trends()
        elif any(word in text_lower for word in ["exercise", "activity", "workout", "fitness"]):
            return self._generate_exercise_trends()
        elif any(word in text_lower for word in ["food", "nutrition", "diet", "eat"]):
            return self._generate_nutrition_trends()
        elif any(word in text_lower for word in ["blood pressure", "bp", "heart", "pulse"]):
            return self._generate_vitals_trends()
        else:
            return "I can show trends for your sleep, exercise, nutrition, or vital signs. Which would you like to see?"
    
    def _generate_sleep_trends(self):
        """
        Generate information about sleep trends.
        
        Returns:
            str: Sleep trend information
        """
        if not self.health_data["sleep_log"]:
            return "I don't have any sleep data logged yet. You can log your sleep by telling me how many hours you slept."
        
        # Calculate some basic statistics
        sleep_records = self.health_data["sleep_log"]
        sleep_records.sort(key=lambda x: x["timestamp"])
        
        # Get recent sleep data (last 7 records or all if fewer)
        recent_sleep = sleep_records[-7:] if len(sleep_records) > 7 else sleep_records
        
        # Calculate average
        avg_sleep = sum(record["hours"] for record in recent_sleep) / len(recent_sleep)
        
        # Format the trend information
        trend_text = f"Based on your {len(recent_sleep)} most recent sleep logs:\n"
        trend_text += f"- Average sleep: {avg_sleep:.1f} hours per night\n"
        
        # Add sleep quality information if available
        # (This would be more sophisticated in a real implementation)
        if avg_sleep < 6:
            trend_text += "- Your average sleep is below the recommended 7-9 hours for adults.\n"
            trend_text += "- Consider setting a consistent sleep schedule to improve your rest."
        elif avg_sleep > 9:
            trend_text += "- Your average sleep is above the typical range of 7-9 hours for adults.\n"
            trend_text += "- While individual sleep needs vary, excessive sleep can sometimes indicate other health issues."
        else:
            trend_text += "- Your average sleep is within the recommended 7-9 hours for adults.\n"
            trend_text += "- Maintaining a consistent sleep schedule can help optimize your rest quality."
        
        return trend_text
    
    def _generate_exercise_trends(self):
        """
        Generate information about exercise trends.
        
        Returns:
            str: Exercise trend information
        """
        if not self.health_data["exercise_log"]:
            return "I don't have any exercise data logged yet. You can log your exercise by telling me what activity you did and for how long."
        
        # Calculate some basic statistics
        exercise_records = self.health_data["exercise_log"]
        exercise_records.sort(key=lambda x: x["timestamp"])
        
        # Get recent exercise data (last 10 records or all if fewer)
        recent_exercise = exercise_records[-10:] if len(exercise_records) > 10 else exercise_records
        
        # Calculate total minutes and activities
        total_minutes = sum(record["duration_minutes"] for record in recent_exercise)
        activities = set(record["activity"] for record in recent_exercise)
        
        # Format the trend information
        trend_text = f"Based on your {len(recent_exercise)} most recent exercise logs:\n"
        trend_text += f"- Total exercise: {total_minutes} minutes\n"
        trend_text += f"- Activities: {', '.join(activities)}\n"
        
        # Add exercise recommendations
        avg_weekly_minutes = total_minutes / 7 * 7  # Approximate weekly average
        if avg_weekly_minutes < 150:
            trend_text += "- The CDC recommends at least 150 minutes of moderate-intensity exercise per week.\n"
            trend_text += "- Consider gradually increasing your activity level to reach this goal."
        else:
            trend_text += "- You're meeting or exceeding the CDC recommendation of 150 minutes of moderate-intensity exercise per week.\n"
            trend_text += "- Great job maintaining your activity level!"
        
        return trend_text
    
    def _generate_nutrition_trends(self):
        """
        Generate information about nutrition trends.
        
        Returns:
            str: Nutrition trend information
        """
        if not self.health_data["nutrition_log"]:
            return "I don't have any nutrition data logged yet. You can log your meals by telling me what you ate."
        
        # In a real implementation, this would analyze nutrition content
        # For this simplified version, just mention recent meals
        nutrition_records = self.health_data["nutrition_log"]
        nutrition_records.sort(key=lambda x: x["timestamp"])
        
        # Get recent nutrition data (last 5 records or all if fewer)
        recent_nutrition = nutrition_records[-5:] if len(nutrition_records) > 5 else nutrition_records
        
        # Format the trend information
        trend_text = f"Based on your {len(recent_nutrition)} most recent meal logs:\n"
        trend_text += "Recent meals:\n"
        
        for record in recent_nutrition:
            date = record["date"]
            food = record["food"]
            trend_text += f"- {date}: {food}\n"
        
        trend_text += "\nFor more detailed nutrition analysis, consider logging specific nutrients or consulting with a dietitian."
        
        return trend_text
    
    def _generate_vitals_trends(self):
        """
        Generate information about vital sign trends.
        
        Returns:
            str: Vital signs trend information
        """
        vitals_records = [r for r in self.health_data["vitals"] if r.get("type") == "blood_pressure"]
        
        if not vitals_records:
            return "I don't have any blood pressure readings logged yet. You can log your blood pressure by telling me your systolic/diastolic values."
        
        # Sort by timestamp
        vitals_records.sort(key=lambda x: x["timestamp"])
        
        # Get recent readings (last 5 or all if fewer)
        recent_vitals = vitals_records[-5:] if len(vitals_records) > 5 else vitals_records
        
        # Calculate averages
        avg_systolic = sum(record["value"]["systolic"] for record in recent_vitals) / len(recent_vitals)
        avg_diastolic = sum(record["value"]["diastolic"] for record in recent_vitals) / len(recent_vitals)
        
        # Format the trend information
        trend_text = f"Based on your {len(recent_vitals)} most recent blood pressure readings:\n"
        trend_text += f"- Average: {avg_systolic:.0f}/{avg_diastolic:.0f} mmHg\n"
        
        # Recent readings
        trend_text += "Recent readings:\n"
        for record in recent_vitals:
            date = record["date"]
            sys = record["value"]["systolic"]
            dia = record["value"]["diastolic"]
            trend_text += f"- {date}: {sys}/{dia} mmHg\n"
        
        # Add interpretation
        if avg_systolic < 120 and avg_diastolic < 80:
            trend_text += "\nYour average blood pressure is in the normal range (below 120/80 mmHg)."
        elif avg_systolic < 130 and avg_diastolic < 80:
            trend_text += "\nYour average blood pressure is in the elevated range (systolic 120-129 and diastolic <80 mmHg)."
        elif avg_systolic < 140 or avg_diastolic < 90:
            trend_text += "\nYour average blood pressure is in the stage 1 hypertension range (systolic 130-139 or diastolic 80-89 mmHg)."
        else:
            trend_text += "\nYour average blood pressure is in the stage 2 hypertension range (systolic 140+ or diastolic 90+ mmHg)."
        
        trend_text += "\nThis is for informational purposes only. Please consult with a healthcare professional for medical advice."
        
        return trend_text
    
    def _handle_health_query(self, text):
        """
        Handle general health information queries.
        
        Args:
            text: Query text
            
        Returns:
            str: Health information response
        """
        text_lower = text.lower()
        
        # Note: In a real implementation, this would connect to a medical knowledge base
        # or a more sophisticated LLM to provide accurate health information
        
        # Sample responses for common health topics
        if any(word in text_lower for word in ["headache", "migraine", "head pain"]):
            return "Headaches can be caused by various factors including stress, dehydration, lack of sleep, or eye strain. For occasional headaches, rest, hydration, and over-the-counter pain relievers may help. If you experience severe or persistent headaches, please consult a healthcare professional."
        
        elif any(word in text_lower for word in ["cold", "flu", "cough", "sneeze", "congestion"]):
            return "Common colds and flu are caused by viruses. Rest, hydration, and over-the-counter medications can help manage symptoms. If you have severe symptoms, high fever, or symptoms that last more than 10 days, please consult a healthcare professional."
        
        elif any(word in text_lower for word in ["exercise", "workout", "fitness"]):
            return "Regular physical activity is important for overall health. The CDC recommends at least 150 minutes of moderate-intensity exercise per week, along with muscle-strengthening activities twice a week. It's always a good idea to start slowly and gradually increase intensity, especially if you're new to exercise."
        
        elif any(word in text_lower for word in ["nutrition", "diet", "eating", "food"]):
            return "A balanced diet typically includes a variety of fruits, vegetables, lean proteins, whole grains, and healthy fats. The specific dietary needs vary by individual. Consider consulting with a registered dietitian for personalized nutrition advice."
        
        elif any(word in text_lower for word in ["sleep", "insomnia", "tired"]):
            return "Adults generally need 7-9 hours of sleep per night. Good sleep hygiene includes maintaining a consistent sleep schedule, creating a restful environment, limiting screen time before bed, and avoiding caffeine and alcohol close to bedtime. If you have persistent sleep difficulties, consider consulting a healthcare professional."
        
        elif any(word in text_lower for word in ["stress", "anxiety", "mental health"]):
            return "Managing stress and anxiety can involve techniques such as deep breathing, meditation, physical activity, adequate sleep, and social connection. Professional support from therapists or counselors can also be beneficial. If you're experiencing severe or persistent mental health concerns, please seek help from a qualified healthcare provider."
        
        # General health response
        return "For specific health information, please consult with a healthcare professional. I can provide general wellness information, but I'm not a substitute for medical advice, diagnosis, or treatment."
    
    def _handle_medication_query(self, text):
        """
        Handle medication-related queries.
        
        Args:
            text: Query text
            
        Returns:
            str: Medication information response
        """
        # In a real implementation, this would connect to a medication database
        # For this simplified version, provide general medication guidance
        
        return "I can help you keep track of your medications, but I don't have access to a medication database to provide specific medication information. For questions about medications, please consult your healthcare provider or pharmacist. They can provide information about proper usage, side effects, and interactions."
    
    def _generate_general_health_info(self):
        """
        Generate general health information.
        
        Returns:
            str: General health information
        """
        general_health_tips = [
            "Regular physical activity, balanced nutrition, adequate sleep, and stress management are key components of a healthy lifestyle.",
            "Most adults need 7-9 hours of sleep per night for optimal health and well-being.",
            "Staying hydrated is important for many bodily functions. The exact amount of water needed varies by individual, but a common recommendation is about 8 cups (64 ounces) per day.",
            "Regular health check-ups can help detect potential health issues early when they may be easier to treat.",
            "Mental health is an important part of overall well-being. Consider practices like mindfulness, meditation, or speaking with a mental health professional if needed."
        ]
        
        return random.choice(general_health_tips) + "\n\nRemember, I can help track your health data and provide general wellness information, but I'm not a substitute for professional medical advice."
    
    def _check_health_alerts(self):
        """
        Check for health alerts or reminders.
        
        Returns:
            str: Health alert or None
        """
        current_time = time.time()
        
        # Only check periodically
        if current_time - self.last_health_check < self.check_interval:
            return None
        
        self.last_health_check = current_time
        
        # Check for medication reminders
        # (This would be more sophisticated in a real implementation)
        
        # Check for other health alerts
        if self.health_data["sleep_log"]:
            recent_sleep = sorted(self.health_data["sleep_log"], key=lambda x: x["timestamp"], reverse=True)[:7]
            avg_sleep = sum(record["hours"] for record in recent_sleep) / len(recent_sleep)
            
            if avg_sleep < 6:
                return "Health Alert: Your recent sleep average is below recommended levels. Consider prioritizing sleep to support your overall health."
        
        # No alerts needed
        return None
