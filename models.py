from datetime import datetime
from flask_login import UserMixin
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float, Boolean
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash

# Import this after other imports to prevent circular imports
from app import db


class User(UserMixin, db.Model):
    """User model for authentication and personalization"""
    id = Column(Integer, primary_key=True)
    username = Column(String(64), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(256))
    created_at = Column(DateTime, default=datetime.utcnow)
    settings = relationship("UserSettings", back_populates="user", uselist=False, cascade="all, delete-orphan")
    memories = relationship("Memory", back_populates="user", cascade="all, delete-orphan")
    interactions = relationship("Interaction", back_populates="user", cascade="all, delete-orphan")
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        """
        Check if the provided password matches the stored hash.
        """
        try:
            # Handle case where password_hash is None or empty
            if not self.password_hash:
                return False
                
            # Get as string (for SQLAlchemy compatibility)
            password_hash_str = str(self.password_hash)
            
            # Safety check
            if not password_hash_str or len(password_hash_str) < 10:
                return False
                
            # Check the password
            return check_password_hash(password_hash_str, password)
        except Exception as e:
            # Log error and fail safe
            print(f"Error checking password: {e}")
            return False


class UserSettings(db.Model):
    """User preferences and settings"""
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    theme = Column(String(32), default="dark")
    language = Column(String(10), default="en")
    voice_enabled = Column(Boolean, default=False)
    notification_enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user = relationship("User", back_populates="settings")
    brain_settings = relationship("BrainSettings", back_populates="user_settings", cascade="all, delete-orphan")


class BrainSettings(db.Model):
    """Settings for individual AI brain modules"""
    id = Column(Integer, primary_key=True)
    user_settings_id = Column(Integer, ForeignKey('user_settings.id'), nullable=False)
    brain_type = Column(String(50), nullable=False)  # e.g., "health", "finance", "intimacy", etc.
    is_active = Column(Boolean, default=True)
    priority = Column(Integer, default=5)  # 1-10, with 10 being highest priority
    custom_settings = Column(Text)  # JSON string for brain-specific settings
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_settings = relationship("UserSettings", back_populates="brain_settings")


class Memory(db.Model):
    """Long-term memory storage for AI"""
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    memory_type = Column(String(50), nullable=False)  # e.g., "conversation", "fact", "preference"
    content = Column(Text, nullable=False)
    importance = Column(Float, default=0.5)  # 0.0 to 1.0
    embedding = Column(Text)  # Vector embedding as serialized string
    created_at = Column(DateTime, default=datetime.utcnow)
    last_accessed = Column(DateTime, default=datetime.utcnow)
    access_count = Column(Integer, default=0)
    user = relationship("User", back_populates="memories")


class Interaction(db.Model):
    """Record of user-AI interactions"""
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    input_text = Column(Text)
    response_text = Column(Text)
    sentiment_score = Column(Float)  # -1.0 to 1.0
    active_brains = Column(Text)  # JSON array of brain modules activated for this interaction
    context_data = Column(Text)  # JSON object with additional context
    interaction_duration = Column(Float)  # in seconds
    user = relationship("User", back_populates="interactions")