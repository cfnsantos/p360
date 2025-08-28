from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict
from datetime import datetime, timedelta

from app.db.database import get_db
from app.schemas.health import (
    HealthRecommendationRequest, 
    HealthRecommendation,
    UserProfile,
    HealthData,
    SymptomLog,
    WellnessTip
)
from app.services.openai_service import openai_service
from app.models.models import (
    User, 
    HealthData as HealthDataModel, 
    SymptomLog as SymptomLogModel,
    HealthRecommendationLog,
    WellnessTip as WellnessTipModel
)

router = APIRouter()

@router.post("/recommendations", response_model=HealthRecommendation)
async def get_health_recommendations(
    request: HealthRecommendationRequest,
    user_id: int = 1,  # TODO: Get from authenticated user
    db: Session = Depends(get_db)
):
    """Generate AI-powered health recommendations"""
    try:
        # Get user's recent health data
        recent_data = db.query(HealthDataModel).filter(
            HealthDataModel.user_id == user_id,
            HealthDataModel.date >= datetime.utcnow() - timedelta(days=30)
        ).order_by(HealthDataModel.date.desc()).limit(10).all()
        
        # Prepare health data for AI
        health_data_dict = {}
        if recent_data:
            latest_data = recent_data[0]
            health_data_dict = {
                "weight": latest_data.weight,
                "blood_pressure": f"{latest_data.blood_pressure_systolic}/{latest_data.blood_pressure_diastolic}" 
                    if latest_data.blood_pressure_systolic and latest_data.blood_pressure_diastolic else None,
                "heart_rate": latest_data.heart_rate,
                "sleep_hours": latest_data.sleep_hours,
                "exercise_minutes": latest_data.exercise_minutes,
                "water_intake": latest_data.water_intake,
                "stress_level": latest_data.stress_level,
                "mood": latest_data.mood
            }
        
        # Generate recommendations
        recommendation = await openai_service.health_recommendation(
            user_profile=request.user_profile.dict(),
            health_data=health_data_dict,
            symptoms=request.symptoms
        )
        
        # Save recommendation to database
        recommendation_log = HealthRecommendationLog(
            user_id=user_id,
            recommendations=recommendation.recommendations,
            user_profile_snapshot=request.user_profile.dict(),
            confidence_score=recommendation.confidence_score,
            categories=recommendation.categories,
            priority_level=recommendation.priority_level,
            follow_up_date=recommendation.follow_up_date
        )
        db.add(recommendation_log)
        db.commit()
        
        return recommendation
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Health recommendation error: {str(e)}")

@router.post("/data")
async def log_health_data(
    health_data: HealthData,
    db: Session = Depends(get_db)
):
    """Log health data for a user"""
    try:
        health_record = HealthDataModel(**health_data.dict())
        db.add(health_record)
        db.commit()
        db.refresh(health_record)
        
        return {"message": "Health data logged successfully", "id": health_record.id}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error logging health data: {str(e)}")

@router.get("/data/{user_id}")
async def get_health_data(
    user_id: int,
    days: int = 30,
    db: Session = Depends(get_db)
):
    """Get health data for a user"""
    try:
        start_date = datetime.utcnow() - timedelta(days=days)
        
        health_data = db.query(HealthDataModel).filter(
            HealthDataModel.user_id == user_id,
            HealthDataModel.date >= start_date
        ).order_by(HealthDataModel.date.desc()).all()
        
        return [
            {
                "date": record.date.isoformat(),
                "weight": record.weight,
                "blood_pressure": f"{record.blood_pressure_systolic}/{record.blood_pressure_diastolic}"
                    if record.blood_pressure_systolic and record.blood_pressure_diastolic else None,
                "heart_rate": record.heart_rate,
                "sleep_hours": record.sleep_hours,
                "exercise_minutes": record.exercise_minutes,
                "water_intake": record.water_intake,
                "stress_level": record.stress_level,
                "mood": record.mood,
                "notes": record.notes
            }
            for record in health_data
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving health data: {str(e)}")

@router.post("/symptoms")
async def log_symptoms(
    symptom_log: SymptomLog,
    db: Session = Depends(get_db)
):
    """Log symptoms and get AI analysis"""
    try:
        # Create symptom log
        symptom_record = SymptomLogModel(**symptom_log.dict())
        
        # Get AI analysis of symptoms
        analysis_prompt = f"""
        Analyze these symptoms: {symptom_log.symptoms}
        Severity: {symptom_log.severity}/10
        Duration: {symptom_log.duration or 'Not specified'}
        Additional notes: {symptom_log.notes or 'None'}
        
        Provide:
        1. Possible causes (non-diagnostic)
        2. Self-care suggestions
        3. When to seek medical attention
        4. Red flags to watch for
        
        IMPORTANT: This is not a medical diagnosis. Always recommend consulting healthcare professionals for persistent or severe symptoms.
        """
        
        ai_analysis = await openai_service.chat_completion(
            messages=[{"role": "user", "content": analysis_prompt}],
            system_prompt="You are a health information assistant. Provide helpful guidance while emphasizing the importance of professional medical care."
        )
        
        symptom_record.ai_analysis = ai_analysis.message
        symptom_record.requires_medical_attention = "seek medical attention" in ai_analysis.message.lower()
        
        db.add(symptom_record)
        db.commit()
        db.refresh(symptom_record)
        
        return {
            "message": "Symptoms logged successfully",
            "id": symptom_record.id,
            "ai_analysis": ai_analysis.message,
            "requires_medical_attention": symptom_record.requires_medical_attention
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error logging symptoms: {str(e)}")

@router.get("/tips")
async def get_wellness_tips(
    category: str = None,
    personalized: bool = False,
    user_id: int = 1,  # TODO: Get from authenticated user
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Get wellness tips, optionally filtered by category"""
    try:
        query = db.query(WellnessTipModel)
        
        if personalized:
            query = query.filter(WellnessTipModel.user_id == user_id)
        else:
            query = query.filter(WellnessTipModel.user_id.is_(None))
        
        if category:
            query = query.filter(WellnessTipModel.category == category)
        
        tips = query.order_by(WellnessTipModel.generated_at.desc()).limit(limit).all()
        
        return [
            {
                "id": tip.id,
                "title": tip.title,
                "content": tip.content,
                "category": tip.category,
                "tags": tip.tags,
                "generated_at": tip.generated_at.isoformat(),
                "is_personalized": tip.is_personalized,
                "engagement": {
                    "views": tip.view_count,
                    "likes": tip.like_count,
                    "shares": tip.share_count
                }
            }
            for tip in tips
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving wellness tips: {str(e)}")

@router.post("/tips/generate")
async def generate_personalized_tips(
    user_id: int = 1,  # TODO: Get from authenticated user
    category: str = "general",
    count: int = 3,
    db: Session = Depends(get_db)
):
    """Generate personalized wellness tips using AI"""
    try:
        # Get user profile
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get recent health data
        recent_data = db.query(HealthDataModel).filter(
            HealthDataModel.user_id == user_id,
            HealthDataModel.date >= datetime.utcnow() - timedelta(days=7)
        ).order_by(HealthDataModel.date.desc()).limit(5).all()
        
        # Prepare user context for AI
        user_context = f"""
        User Profile:
        - Age: {user.age or 'Not specified'}
        - Activity Level: {user.activity_level or 'Not specified'}
        - Health Goals: {user.health_goals or 'Not specified'}
        
        Recent Health Trends:
        """
        
        if recent_data:
            for data in recent_data:
                user_context += f"- {data.date.strftime('%Y-%m-%d')}: Sleep: {data.sleep_hours}h, Exercise: {data.exercise_minutes}min, Stress: {data.stress_level}/10\n"
        
        # Generate tips using AI
        tips_content = await openai_service.generate_content(
            content_type="wellness_tips",
            topic=f"Personalized {category} wellness tips",
            target_audience="individual_user"
        )
        
        # Parse and save individual tips (simplified - you might want more sophisticated parsing)
        tips_text = tips_content["content"]
        tip_sections = tips_text.split("\n\n")  # Simple splitting logic
        
        generated_tips = []
        for i, tip_section in enumerate(tip_sections[:count]):
            if tip_section.strip():
                lines = tip_section.strip().split("\n")
                title = lines[0].replace("#", "").strip() if lines else f"Wellness Tip {i+1}"
                content = "\n".join(lines[1:]) if len(lines) > 1 else tip_section.strip()
                
                wellness_tip = WellnessTipModel(
                    title=title,
                    content=content,
                    category=category,
                    tags=[category, "personalized", "ai_generated"],
                    is_personalized=True,
                    user_id=user_id
                )
                db.add(wellness_tip)
                generated_tips.append(wellness_tip)
        
        db.commit()
        
        return {
            "message": f"Generated {len(generated_tips)} personalized wellness tips",
            "tips": [
                {
                    "id": tip.id,
                    "title": tip.title,
                    "content": tip.content,
                    "category": tip.category,
                    "tags": tip.tags
                }
                for tip in generated_tips
            ]
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error generating tips: {str(e)}")
