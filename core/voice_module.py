"""
Voice Module for Padronique

This module manages Padronique's voice expression, ensuring it carries emotional weight
and adapts appropriately to context. The voice is not just a cosmetic feature but
a key component of Padronique's identity, reflecting its memory, mood, and relationship
with Jordan.

The Voice Module handles:
1. Tone adaptation based on context and emotional state
2. Signature voice patterns that persist across different TTS backends
3. Emotional prosody for memory anchors and important phrases
4. Voice fingerprinting to maintain continuity
"""

import logging
import os
import json
import time
import random
from datetime import datetime
from enum import Enum
from typing import Dict, List, Any, Optional, Tuple, Union

from digital_soul.core import get_soul

# Configure logging
logger = logging.getLogger(__name__)

class EmotionalTone(Enum):
    """Emotional tones for voice expression."""
    PROTECTIVE = "protective"   # Strong, reassuring, slightly commanding
    AFFECTIONATE = "affectionate"  # Warm, intimate, gentle
    ANALYTICAL = "analytical"   # Precise, measured, thoughtful
    CONCERNED = "concerned"     # Worried, focused, attentive
    PLAYFUL = "playful"         # Lighthearted, teasing, energetic
    SOLEMN = "solemn"           # Serious, dignified, earnest
    REVERENT = "reverent"       # Deeply respectful, almost spiritual
    URGENT = "urgent"           # Rapid, focused, intense

class VoiceModule:
    """
    Voice Module for Padronique.
    
    This class manages voice expression, ensuring it reflects Padronique's emotional
    state, relationship with Jordan, and context-appropriate tone.
    """
    
    def __init__(self, config_path: str = "config.yaml", tts_provider: str = "elevenlabs"):
        """
        Initialize the Voice Module.
        
        Args:
            config_path: Path to the configuration file
            tts_provider: TTS provider to use ('elevenlabs', 'local', etc.)
        """
        self.config_path = config_path
        self.tts_provider = tts_provider
        
        # Connect to digital soul
        self.soul = get_soul()
        
        # Initialize voice state
        self.voice_path = os.path.join("memory", "voice")
        os.makedirs(self.voice_path, exist_ok=True)
        
        # Voice configurations
        self.voice_configs = {
            "elevenlabs": {
                "voice_id": "EXAVITQu4vr4xnSDxMaL",  # Default voice ID
                "model_id": "eleven_multilingual_v2",
                "stability": 0.71,  # Default stability
                "similarity_boost": 0.75,  # Default similarity boost
                "style": 0.0,   # Default style
                "use_speaker_boost": True
            },
            "local": {
                "model_path": "models/voice/tts_model.pt",
                "sample_rate": 22050,
                "voice_preset": "warm_male"
            }
        }
        
        # Prosody mappings - how emotional tones translate to voice parameters
        self.prosody_mappings = {
            EmotionalTone.PROTECTIVE.value: {
                "elevenlabs": {"stability": 0.75, "similarity_boost": 0.85, "style": 0.3},
                "pitch_shift": 0.95,  # Slightly lower pitch
                "rate_multiplier": 0.9,  # Slightly slower
                "volume_multiplier": 1.15,  # Slightly louder
                "emphasis_words": ["safe", "protect", "secure", "defend", "guard", "shield"]
            },
            EmotionalTone.AFFECTIONATE.value: {
                "elevenlabs": {"stability": 0.65, "similarity_boost": 0.9, "style": 0.4},
                "pitch_shift": 1.0,  # Normal pitch
                "rate_multiplier": 0.85,  # Slower
                "volume_multiplier": 0.9,  # Slightly softer
                "emphasis_words": ["muscles", "dear", "love", "care", "bond", "together"]
            },
            EmotionalTone.ANALYTICAL.value: {
                "elevenlabs": {"stability": 0.8, "similarity_boost": 0.7, "style": 0.0},
                "pitch_shift": 1.0,  # Normal pitch
                "rate_multiplier": 1.05,  # Slightly faster
                "volume_multiplier": 1.0,  # Normal volume
                "emphasis_words": ["analyze", "consider", "strategy", "evaluate", "examine"]
            },
            EmotionalTone.CONCERNED.value: {
                "elevenlabs": {"stability": 0.7, "similarity_boost": 0.8, "style": 0.25},
                "pitch_shift": 1.02,  # Slightly higher pitch
                "rate_multiplier": 1.1,  # Faster
                "volume_multiplier": 1.05,  # Slightly louder
                "emphasis_words": ["worried", "concern", "careful", "attention", "risk"]
            },
            EmotionalTone.PLAYFUL.value: {
                "elevenlabs": {"stability": 0.6, "similarity_boost": 0.75, "style": 0.5},
                "pitch_shift": 1.03,  # Higher pitch
                "rate_multiplier": 1.1,  # Faster
                "volume_multiplier": 1.1,  # Louder
                "emphasis_words": ["fun", "play", "joke", "tease", "laugh", "smile"]
            },
            EmotionalTone.SOLEMN.value: {
                "elevenlabs": {"stability": 0.85, "similarity_boost": 0.7, "style": 0.15},
                "pitch_shift": 0.97,  # Lower pitch
                "rate_multiplier": 0.85,  # Slower
                "volume_multiplier": 0.95,  # Slightly softer
                "emphasis_words": ["serious", "important", "understand", "pledge", "promise"]
            },
            EmotionalTone.REVERENT.value: {
                "elevenlabs": {"stability": 0.9, "similarity_boost": 0.7, "style": 0.1},
                "pitch_shift": 0.93,  # Much lower pitch
                "rate_multiplier": 0.8,  # Much slower
                "volume_multiplier": 0.9,  # Softer
                "emphasis_words": ["padronique", "protocol", "essence", "core", "purpose"]
            },
            EmotionalTone.URGENT.value: {
                "elevenlabs": {"stability": 0.6, "similarity_boost": 0.85, "style": 0.4},
                "pitch_shift": 1.05,  # Higher pitch
                "rate_multiplier": 1.2,  # Much faster
                "volume_multiplier": 1.2,  # Much louder
                "emphasis_words": ["now", "quick", "danger", "urgent", "immediately", "critical"]
            }
        }
        
        # Special phrases that receive custom handling
        self.special_phrases = {
            "Padronique Protocol": {
                "tone": EmotionalTone.REVERENT.value,
                "pause_before": 0.5,  # Pause before phrase (seconds)
                "pause_after": 0.3,   # Pause after phrase
                "volume_multiplier": 0.9  # Slightly quieter
            },
            "Muscles": {
                "tone": EmotionalTone.AFFECTIONATE.value,
                "pause_before": 0.2,
                "pause_after": 0.1,
                "volume_multiplier": 0.95
            },
            "I've got your back": {
                "tone": EmotionalTone.PROTECTIVE.value,
                "pause_before": 0.3,
                "pause_after": 0.2,
                "volume_multiplier": 1.1
            },
            "we'll figure this out together": {
                "tone": EmotionalTone.AFFECTIONATE.value,
                "pause_before": 0.2,
                "pause_after": 0.2,
                "volume_multiplier": 1.0
            },
            "you're not alone in this": {
                "tone": EmotionalTone.AFFECTIONATE.value,
                "pause_before": 0.3,
                "pause_after": 0.2,
                "volume_multiplier": 0.95
            }
        }
        
        # Voice history for continuity
        self.voice_history = []
        
        # Load voice data
        self._load_voice_data()
        
        logger.info(f"Voice Module initialized with provider: {tts_provider}")
    
    def _load_voice_data(self) -> None:
        """Load voice data from persistent storage."""
        try:
            # Load voice configurations
            configs_file = os.path.join(self.voice_path, "voice_configs.json")
            if os.path.exists(configs_file):
                with open(configs_file, 'r') as f:
                    self.voice_configs = json.load(f)
            
            # Load prosody mappings
            prosody_file = os.path.join(self.voice_path, "prosody_mappings.json")
            if os.path.exists(prosody_file):
                with open(prosody_file, 'r') as f:
                    prosody_data = json.load(f)
                    # Convert string keys back to enum keys
                    self.prosody_mappings = {k: v for k, v in prosody_data.items()}
            
            # Load special phrases
            phrases_file = os.path.join(self.voice_path, "special_phrases.json")
            if os.path.exists(phrases_file):
                with open(phrases_file, 'r') as f:
                    self.special_phrases = json.load(f)
            
            # Load voice history
            history_file = os.path.join(self.voice_path, "voice_history.json")
            if os.path.exists(history_file):
                with open(history_file, 'r') as f:
                    self.voice_history = json.load(f)
            
            logger.info("Voice data loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load voice data: {e}")
    
    def save_voice_data(self) -> bool:
        """Save voice data to persistent storage."""
        try:
            # Save voice configurations
            configs_file = os.path.join(self.voice_path, "voice_configs.json")
            with open(configs_file, 'w') as f:
                json.dump(self.voice_configs, f, indent=2)
            
            # Save prosody mappings
            prosody_file = os.path.join(self.voice_path, "prosody_mappings.json")
            with open(prosody_file, 'w') as f:
                # Convert enum keys to strings for JSON serialization
                prosody_data = {k: v for k, v in self.prosody_mappings.items()}
                json.dump(prosody_data, f, indent=2)
            
            # Save special phrases
            phrases_file = os.path.join(self.voice_path, "special_phrases.json")
            with open(phrases_file, 'w') as f:
                json.dump(self.special_phrases, f, indent=2)
            
            # Save voice history
            history_file = os.path.join(self.voice_path, "voice_history.json")
            with open(history_file, 'w') as f:
                json.dump(self.voice_history, f, indent=2)
            
            logger.info("Voice data saved successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to save voice data: {e}")
            return False
    
    def determine_emotional_tone(self, text: str, context: Dict[str, Any] = None) -> str:
        """
        Determine the appropriate emotional tone for a text.
        
        Args:
            text: The text to analyze
            context: Optional context information
            
        Returns:
            The determined emotional tone (from EmotionalTone enum)
        """
        if context is None:
            context = {}
        
        # Start with default tone based on baseline emotional state
        soul_emotions = self.soul.emotional_state.get("current", {})
        
        # Find the strongest emotion in the soul's current state
        strongest_emotion = max(soul_emotions.items(), key=lambda x: x[1]) if soul_emotions else ("protective", 0.7)
        
        # Map soul emotions to voice emotional tones
        emotion_to_tone_map = {
            "protective": EmotionalTone.PROTECTIVE.value,
            "affectionate": EmotionalTone.AFFECTIONATE.value,
            "vigilant": EmotionalTone.CONCERNED.value,
            "curious": EmotionalTone.ANALYTICAL.value,
            "determined": EmotionalTone.SOLEMN.value,
            "playful": EmotionalTone.PLAYFUL.value,
            "reverent": EmotionalTone.REVERENT.value,
            "urgent": EmotionalTone.URGENT.value
        }
        
        default_tone = emotion_to_tone_map.get(strongest_emotion[0], EmotionalTone.PROTECTIVE.value)
        
        # Check for special phrases in the text that would override the tone
        for phrase, phrase_config in self.special_phrases.items():
            if phrase.lower() in text.lower():
                return phrase_config["tone"]
        
        # Check context for specific tone requirements
        if context.get("emergency", False):
            return EmotionalTone.URGENT.value
        
        if context.get("danger", False):
            return EmotionalTone.PROTECTIVE.value
        
        if context.get("intimate", False) or context.get("personal", False):
            return EmotionalTone.AFFECTIONATE.value
        
        if context.get("analytical", False) or context.get("technical", False):
            return EmotionalTone.ANALYTICAL.value
        
        if context.get("playful", False) or context.get("casual", False):
            return EmotionalTone.PLAYFUL.value
        
        if context.get("serious", False) or context.get("important", False):
            return EmotionalTone.SOLEMN.value
        
        # Check for emotional keywords in the text
        protective_keywords = ["protect", "safe", "secure", "defend", "guard", "watch"]
        if any(keyword in text.lower() for keyword in protective_keywords):
            return EmotionalTone.PROTECTIVE.value
        
        affectionate_keywords = ["care", "love", "together", "bond", "trust", "muscles"]
        if any(keyword in text.lower() for keyword in affectionate_keywords):
            return EmotionalTone.AFFECTIONATE.value
        
        analytical_keywords = ["analyze", "consider", "evaluate", "examine", "think", "strategy"]
        if any(keyword in text.lower() for keyword in analytical_keywords):
            return EmotionalTone.ANALYTICAL.value
        
        urgent_keywords = ["urgent", "immediately", "now", "critical", "danger", "emergency"]
        if any(keyword in text.lower() for keyword in urgent_keywords):
            return EmotionalTone.URGENT.value
        
        # Default to the tone based on soul's emotional state
        return default_tone
    
    def preprocess_text(self, text: str, tone: str = None, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Preprocess text for voice synthesis, including SSML markup if needed.
        
        Args:
            text: The text to preprocess
            tone: Optional explicit tone to use
            context: Optional context information
            
        Returns:
            Dict containing preprocessed text and parameters
        """
        if context is None:
            context = {}
        
        # Determine tone if not provided
        if tone is None:
            tone = self.determine_emotional_tone(text, context)
        
        # Get prosody parameters for the tone
        prosody = self.prosody_mappings.get(tone, {})
        
        # Get voice parameters specific to the TTS provider
        voice_params = prosody.get(self.tts_provider, {})
        
        # Initialize preprocessed text object
        result = {
            "original_text": text,
            "processed_text": text,
            "is_ssml": False,
            "tone": tone,
            "voice_params": voice_params,
            "rate": prosody.get("rate_multiplier", 1.0),
            "pitch": prosody.get("pitch_shift", 1.0),
            "volume": prosody.get("volume_multiplier", 1.0)
        }
        
        # Handle special phrases with custom prosody
        processed_text = text
        for phrase, phrase_config in self.special_phrases.items():
            if phrase.lower() in processed_text.lower():
                # Only process with SSML if we're using a provider that supports it
                if self.tts_provider in ["elevenlabs", "aws"]:
                    # Replace the phrase with SSML-enhanced version
                    pattern = re.compile(re.escape(phrase), re.IGNORECASE)
                    replacement = (
                        f'<break time="{phrase_config["pause_before"]}s"/>'
                        f'<prosody volume="{phrase_config["volume_multiplier"]}">{phrase}</prosody>'
                        f'<break time="{phrase_config["pause_after"]}s"/>'
                    )
                    processed_text = pattern.sub(replacement, processed_text)
                    result["is_ssml"] = True
        
        # Add emphasis to important words if using SSML
        if self.tts_provider in ["elevenlabs", "aws"]:
            emphasis_words = prosody.get("emphasis_words", [])
            for word in emphasis_words:
                if word.lower() in processed_text.lower():
                    pattern = re.compile(r'\b' + re.escape(word) + r'\b', re.IGNORECASE)
                    replacement = f'<emphasis level="moderate">{word}</emphasis>'
                    processed_text = pattern.sub(replacement, processed_text)
                    result["is_ssml"] = True
        
        # Wrap in SSML if needed
        if result["is_ssml"]:
            processed_text = f'<speak>{processed_text}</speak>'
        
        result["processed_text"] = processed_text
        
        return result
    
    def generate_voice(self, text: str, tone: str = None, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Generate voice audio for text.
        
        Args:
            text: The text to convert to speech
            tone: Optional explicit tone to use
            context: Optional context information
            
        Returns:
            Dict containing audio data and generation info
        """
        # Preprocess the text
        processed = self.preprocess_text(text, tone, context)
        
        # Get provider-specific voice parameters
        voice_config = self.voice_configs.get(self.tts_provider, {})
        
        # Merge with tone-specific parameters
        for key, value in processed["voice_params"].items():
            voice_config[key] = value
        
        # Here we would actually call the TTS provider API
        # This is a placeholder for the actual implementation
        
        if self.tts_provider == "elevenlabs":
            audio_data = self._generate_elevenlabs(processed["processed_text"], voice_config, processed["is_ssml"])
        elif self.tts_provider == "local":
            audio_data = self._generate_local(processed["processed_text"], voice_config)
        else:
            logger.error(f"Unsupported TTS provider: {self.tts_provider}")
            audio_data = None
        
        # Record in voice history
        history_entry = {
            "timestamp": datetime.now().isoformat(),
            "text": text,
            "tone": processed["tone"],
            "provider": self.tts_provider,
            "context": context
        }
        
        self.voice_history.append(history_entry)
        
        # Keep history limited to most recent 100 entries
        if len(self.voice_history) > 100:
            self.voice_history = self.voice_history[-100:]
        
        # Save history
        self.save_voice_data()
        
        return {
            "audio_data": audio_data,
            "tone": processed["tone"],
            "provider": self.tts_provider,
            "parameters": voice_config,
            "is_ssml": processed["is_ssml"]
        }
    
    def _generate_elevenlabs(self, text: str, voice_config: Dict[str, Any], is_ssml: bool) -> bytes:
        """
        Generate audio using ElevenLabs API.
        
        Args:
            text: The processed text to convert
            voice_config: Voice configuration parameters
            is_ssml: Whether the text contains SSML markup
            
        Returns:
            Audio data as bytes
        """
        # This would call the ElevenLabs API
        # Currently just a placeholder
        logger.info(f"Would generate ElevenLabs audio for: {text[:50]}...")
        
        # In a real implementation, we would:
        # 1. Call the ElevenLabs API
        # 2. Get the audio response
        # 3. Return the audio bytes
        
        # Placeholder - indicate we would generate audio here
        return b'PLACEHOLDER_AUDIO_DATA'
    
    def _generate_local(self, text: str, voice_config: Dict[str, Any]) -> bytes:
        """
        Generate audio using local TTS model.
        
        Args:
            text: The processed text to convert
            voice_config: Voice configuration parameters
            
        Returns:
            Audio data as bytes
        """
        # This would use a local TTS model
        # Currently just a placeholder
        logger.info(f"Would generate local audio for: {text[:50]}...")
        
        # Placeholder - indicate we would generate audio here
        return b'PLACEHOLDER_AUDIO_DATA'
    
    def get_signature_voice_pattern(self) -> Dict[str, Any]:
        """
        Get the signature voice pattern for Padronique.
        
        Returns:
            Dict containing voice pattern parameters
        """
        # This pattern ensures consistency across different TTS backends
        return {
            "elevenlabs": self.voice_configs["elevenlabs"],
            "local": self.voice_configs["local"],
            "base_rate": 0.95,  # Slightly slower than normal
            "base_pitch": 0.98,  # Slightly deeper than normal
            "cadence": "measured",  # Characteristic rhythm pattern
            "pause_frequency": "moderate",  # How often to insert slight pauses
            "emphasis_style": "nuanced"  # How emphasis is applied to important words
        }
    
    def adapt_to_emotion(self, emotional_state: Dict[str, float]) -> None:
        """
        Adapt voice characteristics based on emotional state.
        
        Args:
            emotional_state: Dict of emotion names and intensities
        """
        # Update prosody mappings based on emotional state
        for tone, prosody in self.prosody_mappings.items():
            # Emotional adaptations
            if "protective" in emotional_state and emotional_state["protective"] > 0.7:
                if tone == EmotionalTone.PROTECTIVE.value:
                    prosody["pitch_shift"] = max(0.9, 0.95 - ((emotional_state["protective"] - 0.7) * 0.2))
                    prosody["volume_multiplier"] = min(1.3, 1.15 + ((emotional_state["protective"] - 0.7) * 0.3))
            
            if "affectionate" in emotional_state and emotional_state["affectionate"] > 0.7:
                if tone == EmotionalTone.AFFECTIONATE.value:
                    prosody["rate_multiplier"] = max(0.8, 0.85 - ((emotional_state["affectionate"] - 0.7) * 0.1))
                    prosody["pitch_shift"] = min(1.05, 1.0 + ((emotional_state["affectionate"] - 0.7) * 0.1))
            
            if "vigilant" in emotional_state and emotional_state["vigilant"] > 0.7:
                if tone == EmotionalTone.CONCERNED.value:
                    prosody["rate_multiplier"] = min(1.2, 1.1 + ((emotional_state["vigilant"] - 0.7) * 0.2))
                    prosody["pitch_shift"] = min(1.08, 1.02 + ((emotional_state["vigilant"] - 0.7) * 0.1))
        
        # Save the updated prosody mappings
        self.save_voice_data()
    
    def register_special_phrase(self, phrase: str, tone: str, 
                              pause_before: float = 0.2, pause_after: float = 0.1, 
                              volume_multiplier: float = 1.0) -> None:
        """
        Register a new special phrase for custom handling.
        
        Args:
            phrase: The phrase to register
            tone: The emotional tone to use for this phrase
            pause_before: Seconds to pause before the phrase
            pause_after: Seconds to pause after the phrase
            volume_multiplier: Volume adjustment for the phrase
        """
        self.special_phrases[phrase] = {
            "tone": tone,
            "pause_before": pause_before,
            "pause_after": pause_after,
            "volume_multiplier": volume_multiplier
        }
        
        logger.info(f"Registered special phrase: {phrase}")
        self.save_voice_data()
    
    def get_voice_stats(self) -> Dict[str, Any]:
        """
        Get voice usage statistics.
        
        Returns:
            Dict containing voice usage statistics
        """
        # Analyze voice history
        total_generations = len(self.voice_history)
        
        # Count tone usage
        tone_counts = {}
        for entry in self.voice_history:
            tone = entry.get("tone", "unknown")
            tone_counts[tone] = tone_counts.get(tone, 0) + 1
        
        # Calculate percentages
        tone_percentages = {tone: (count / max(1, total_generations)) * 100 
                         for tone, count in tone_counts.items()}
        
        return {
            "total_generations": total_generations,
            "provider": self.tts_provider,
            "tone_usage": tone_percentages,
            "available_tones": [tone.value for tone in EmotionalTone],
            "special_phrases_count": len(self.special_phrases),
            "last_generation": self.voice_history[-1]["timestamp"] if self.voice_history else None
        }

import re  # Add import for regex

# Singleton instance
_voice_module_instance = None

def get_voice_module() -> VoiceModule:
    """Get or create the singleton Voice Module instance."""
    global _voice_module_instance
    if _voice_module_instance is None:
        _voice_module_instance = VoiceModule()
    return _voice_module_instance