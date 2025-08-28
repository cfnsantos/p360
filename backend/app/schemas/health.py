from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime
from enum import Enum

class ActivityLevel(str, Enum):
    SEDENTARY = "sedentary"
    LIGHTLY_ACTIVE = "lightly_active"
    MODERATELY_ACTIVE = "moderately_active"
    VERY_ACTIVE = "very_active"
    EXTREMELY_ACTIVE = "extremely_active"

class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"
    PREFER_NOT_TO_SAY = "prefer_not_to_say"

class UserProfile(BaseModel):
    age: Optional[int] = Field(None, ge=1, le=120)
    gender: Optional[Gender] = None
    height: Optional[float] = Field(None, gt=0, description="Height in cm")
    weight: Optional[float] = Field(None, gt=0, description="Weight in kg")
    activity_level: Optional[ActivityLevel] = None
    health_goals: Optional[List[str]] = None
    medical_conditions: Optional[List[str]] = None
    medications: Optional[List[str]] = None
    allergies: Optional[List[str]] = None

class HealthData(BaseModel):
    user_id: int
    date: datetime
    weight: Optional[float] = None
    blood_pressure_systolic: Optional[int] = None
    blood_pressure_diastolic: Optional[int] = None
    heart_rate: Optional[int] = None
    sleep_hours: Optional[float] = None
    exercise_minutes: Optional[int] = None
    water_intake: Optional[float] = None
    stress_level: Optional[int] = Field(None, ge=1, le=10)
    mood: Optional[int] = Field(None, ge=1, le=10)

class HealthRecommendationRequest(BaseModel):
    user_profile: UserProfile
    recent_health_data: Optional[List[HealthData]] = None
    symptoms: Optional[List[str]] = None
    specific_concerns: Optional[str] = None

class HealthRecommendation(BaseModel):
    recommendations: str
    user_profile: Dict
    generated_at: datetime
    confidence_score: float = Field(ge=0.0, le=1.0)
    categories: List[str]
    priority_level: Optional[str] = "medium"
    follow_up_date: Optional[datetime] = None

class SymptomLog(BaseModel):
    user_id: int
    symptoms: List[str]
    severity: int = Field(ge=1, le=10)
    duration: Optional[str] = None
    notes: Optional[str] = None
    logged_at: datetime = Field(default_factory=datetime.utcnow)

class WellnessTip(BaseModel):
    title: str
    content: str
    category: str
    tags: List[str]
    generated_at: datetime
    is_personalized: bool = False
    user_id: Optional[int] = None
