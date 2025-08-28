from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Profile information
    age = Column(Integer, nullable=True)
    gender = Column(String, nullable=True)
    height = Column(Float, nullable=True)  # in cm
    weight = Column(Float, nullable=True)  # in kg
    activity_level = Column(String, nullable=True)
    health_goals = Column(JSON, nullable=True)
    medical_conditions = Column(JSON, nullable=True)
    medications = Column(JSON, nullable=True)
    allergies = Column(JSON, nullable=True)
    
    # Relationships
    conversations = relationship("Conversation", back_populates="user")
    health_data = relationship("HealthData", back_populates="user")
    symptom_logs = relationship("SymptomLog", back_populates="user")
    wellness_tips = relationship("WellnessTip", back_populates="user")

class Conversation(Base):
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(String, unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation")

class Message(Base):
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    role = Column(String, nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    token_count = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    conversation = relationship("Conversation", back_populates="messages")

class HealthData(Base):
    __tablename__ = "health_data"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(DateTime, nullable=False)
    
    # Vital signs
    weight = Column(Float, nullable=True)
    blood_pressure_systolic = Column(Integer, nullable=True)
    blood_pressure_diastolic = Column(Integer, nullable=True)
    heart_rate = Column(Integer, nullable=True)
    
    # Lifestyle metrics
    sleep_hours = Column(Float, nullable=True)
    exercise_minutes = Column(Integer, nullable=True)
    water_intake = Column(Float, nullable=True)  # in liters
    stress_level = Column(Integer, nullable=True)  # 1-10 scale
    mood = Column(Integer, nullable=True)  # 1-10 scale
    
    # Additional notes
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="health_data")

class SymptomLog(Base):
    __tablename__ = "symptom_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    symptoms = Column(JSON, nullable=False)  # List of symptoms
    severity = Column(Integer, nullable=False)  # 1-10 scale
    duration = Column(String, nullable=True)
    notes = Column(Text, nullable=True)
    logged_at = Column(DateTime, default=datetime.utcnow)
    
    # AI Analysis
    ai_analysis = Column(Text, nullable=True)
    requires_medical_attention = Column(Boolean, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="symptom_logs")

class HealthRecommendationLog(Base):
    __tablename__ = "health_recommendation_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    recommendations = Column(Text, nullable=False)
    user_profile_snapshot = Column(JSON, nullable=False)
    confidence_score = Column(Float, nullable=False)
    categories = Column(JSON, nullable=False)
    priority_level = Column(String, default="medium")
    generated_at = Column(DateTime, default=datetime.utcnow)
    follow_up_date = Column(DateTime, nullable=True)
    user_feedback = Column(Integer, nullable=True)  # 1-5 rating

class WellnessTip(Base):
    __tablename__ = "wellness_tips"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    category = Column(String, nullable=False)
    tags = Column(JSON, nullable=True)
    generated_at = Column(DateTime, default=datetime.utcnow)
    is_personalized = Column(Boolean, default=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Engagement metrics
    view_count = Column(Integer, default=0)
    like_count = Column(Integer, default=0)
    share_count = Column(Integer, default=0)
    
    # Relationships
    user = relationship("User", back_populates="wellness_tips")

class ContentGeneration(Base):
    __tablename__ = "content_generations"
    
    id = Column(Integer, primary_key=True, index=True)
    content_type = Column(String, nullable=False)  # article, tip, recipe, etc.
    topic = Column(String, nullable=False)
    target_audience = Column(String, nullable=False)
    length = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    token_count = Column(Integer, nullable=True)
    generated_at = Column(DateTime, default=datetime.utcnow)
    
    # Approval and publication
    is_approved = Column(Boolean, default=False)
    approved_by = Column(String, nullable=True)
    published_at = Column(DateTime, nullable=True)

class CodeAssistanceLog(Base):
    __tablename__ = "code_assistance_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    query = Column(Text, nullable=False)
    language = Column(String, nullable=False)
    context = Column(Text, nullable=True)
    assistance_response = Column(Text, nullable=False)
    token_count = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Feedback
    was_helpful = Column(Boolean, nullable=True)
    user_rating = Column(Integer, nullable=True)  # 1-5 scale
