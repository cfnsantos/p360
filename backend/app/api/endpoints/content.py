from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Optional
from pydantic import BaseModel

from app.db.database import get_db
from app.services.openai_service import openai_service
from app.models.models import ContentGeneration

router = APIRouter()

class ContentRequest(BaseModel):
    content_type: str  # article, blog_post, social_media, newsletter, etc.
    topic: str
    target_audience: str = "general"
    length: str = "medium"  # short, medium, long
    tone: Optional[str] = "professional"
    keywords: Optional[List[str]] = None

class ContentResponse(BaseModel):
    content: str
    content_type: str
    topic: str
    target_audience: str
    length: str
    token_count: int
    generated_at: str
    content_id: int

@router.post("/generate", response_model=ContentResponse)
async def generate_content(
    request: ContentRequest,
    db: Session = Depends(get_db)
):
    """Generate health and wellness content using AI"""
    try:
        # Enhanced content generation with more context
        enhanced_topic = request.topic
        if request.keywords:
            enhanced_topic += f" (focusing on: {', '.join(request.keywords)})"
        
        content_result = await openai_service.generate_content(
            content_type=request.content_type,
            topic=enhanced_topic,
            target_audience=request.target_audience,
            length=request.length
        )
        
        # Save to database
        content_record = ContentGeneration(
            content_type=request.content_type,
            topic=request.topic,
            target_audience=request.target_audience,
            length=request.length,
            content=content_result["content"],
            token_count=content_result["token_count"]
        )
        db.add(content_record)
        db.commit()
        db.refresh(content_record)
        
        return ContentResponse(
            content=content_result["content"],
            content_type=request.content_type,
            topic=request.topic,
            target_audience=request.target_audience,
            length=request.length,
            token_count=content_result["token_count"],
            generated_at=content_result["generated_at"],
            content_id=content_record.id
        )
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Content generation error: {str(e)}")

@router.get("/library")
async def get_content_library(
    content_type: Optional[str] = None,
    topic: Optional[str] = None,
    approved_only: bool = True,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """Get generated content from the library"""
    try:
        query = db.query(ContentGeneration)
        
        if approved_only:
            query = query.filter(ContentGeneration.is_approved == True)
        
        if content_type:
            query = query.filter(ContentGeneration.content_type == content_type)
        
        if topic:
            query = query.filter(ContentGeneration.topic.ilike(f"%{topic}%"))
        
        content_items = query.order_by(
            ContentGeneration.generated_at.desc()
        ).limit(limit).all()
        
        return [
            {
                "id": item.id,
                "content_type": item.content_type,
                "topic": item.topic,
                "target_audience": item.target_audience,
                "length": item.length,
                "content": item.content,
                "generated_at": item.generated_at.isoformat(),
                "is_approved": item.is_approved,
                "published_at": item.published_at.isoformat() if item.published_at else None
            }
            for item in content_items
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving content: {str(e)}")

@router.post("/templates")
async def generate_content_templates(
    category: str = "wellness",
    count: int = 5,
    db: Session = Depends(get_db)
):
    """Generate content templates for different health topics"""
    try:
        topics = {
            "wellness": [
                "10 Daily Habits for Better Health",
                "Stress Management Techniques",
                "Nutrition Tips for Busy Professionals", 
                "Sleep Hygiene Best Practices",
                "Mental Health Self-Care Strategies"
            ],
            "fitness": [
                "Beginner's Guide to Home Workouts",
                "Building Muscle Without a Gym",
                "Cardio Exercises for Heart Health",
                "Flexibility and Stretching Routines",
                "Recovery and Rest Day Activities"
            ],
            "nutrition": [
                "Meal Planning for Healthy Eating",
                "Understanding Macronutrients",
                "Healthy Snack Ideas",
                "Hydration and Water Intake Guide",
                "Plant-Based Nutrition Basics"
            ]
        }
        
        selected_topics = topics.get(category, topics["wellness"])[:count]
        generated_content = []
        
        for topic in selected_topics:
            content_result = await openai_service.generate_content(
                content_type="article",
                topic=topic,
                target_audience="general",
                length="medium"
            )
            
            content_record = ContentGeneration(
                content_type="article",
                topic=topic,
                target_audience="general",
                length="medium",
                content=content_result["content"],
                token_count=content_result["token_count"]
            )
            db.add(content_record)
            generated_content.append({
                "topic": topic,
                "content": content_result["content"],
                "token_count": content_result["token_count"]
            })
        
        db.commit()
        
        return {
            "message": f"Generated {len(generated_content)} content templates for {category}",
            "category": category,
            "content": generated_content
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error generating templates: {str(e)}")

@router.put("/approve/{content_id}")
async def approve_content(
    content_id: int,
    approved_by: str,
    db: Session = Depends(get_db)
):
    """Approve generated content for publication"""
    try:
        content = db.query(ContentGeneration).filter(
            ContentGeneration.id == content_id
        ).first()
        
        if not content:
            raise HTTPException(status_code=404, detail="Content not found")
        
        content.is_approved = True
        content.approved_by = approved_by
        content.published_at = datetime.utcnow()
        
        db.commit()
        
        return {"message": "Content approved successfully", "content_id": content_id}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error approving content: {str(e)}")
