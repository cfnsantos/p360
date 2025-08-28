from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel

from app.db.database import get_db
from app.services.openai_service import openai_service
from app.models.models import CodeAssistanceLog

router = APIRouter()

class CodeAssistanceRequest(BaseModel):
    query: str
    language: str = "python"
    context: Optional[str] = None
    code_snippet: Optional[str] = None

class CodeAssistanceResponse(BaseModel):
    assistance: str
    language: str
    query: str
    generated_at: str
    token_count: int
    assistance_id: int

@router.post("/assist", response_model=CodeAssistanceResponse)
async def get_code_assistance(
    request: CodeAssistanceRequest,
    user_id: Optional[int] = None,  # TODO: Get from authenticated user
    db: Session = Depends(get_db)
):
    """Get AI-powered code assistance"""
    try:
        # Enhanced context with code snippet
        enhanced_context = request.context or ""
        if request.code_snippet:
            enhanced_context += f"\n\nCode snippet:\n```{request.language}\n{request.code_snippet}\n```"
        
        assistance_result = await openai_service.code_assistance(
            code_query=request.query,
            language=request.language,
            context=enhanced_context
        )
        
        # Save to database
        assistance_log = CodeAssistanceLog(
            user_id=user_id,
            query=request.query,
            language=request.language,
            context=enhanced_context,
            assistance_response=assistance_result["assistance"],
            token_count=assistance_result["token_count"]
        )
        db.add(assistance_log)
        db.commit()
        db.refresh(assistance_log)
        
        return CodeAssistanceResponse(
            assistance=assistance_result["assistance"],
            language=request.language,
            query=request.query,
            generated_at=assistance_result["generated_at"],
            token_count=assistance_result["token_count"],
            assistance_id=assistance_log.id
        )
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Code assistance error: {str(e)}")

@router.post("/review")
async def code_review(
    code: str,
    language: str = "python",
    focus_areas: Optional[List[str]] = None,
    db: Session = Depends(get_db)
):
    """Get AI-powered code review"""
    try:
        focus = focus_areas or ["best_practices", "performance", "security", "maintainability"]
        
        review_prompt = f"""
        Please review this {language} code and provide feedback on:
        {', '.join(focus)}
        
        Code to review:
        ```{language}
        {code}
        ```
        
        Provide:
        1. Overall assessment
        2. Specific improvement suggestions
        3. Best practices recommendations
        4. Potential issues or bugs
        5. Performance optimization opportunities
        """
        
        review_result = await openai_service.code_assistance(
            code_query=review_prompt,
            language=language,
            context="Code review request"
        )
        
        # Save to database
        assistance_log = CodeAssistanceLog(
            query=f"Code review for {language} code",
            language=language,
            context=f"Code review focusing on: {', '.join(focus)}",
            assistance_response=review_result["assistance"],
            token_count=review_result["token_count"]
        )
        db.add(assistance_log)
        db.commit()
        
        return {
            "review": review_result["assistance"],
            "language": language,
            "focus_areas": focus,
            "generated_at": review_result["generated_at"],
            "token_count": review_result["token_count"]
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Code review error: {str(e)}")

@router.post("/debug")
async def debug_assistance(
    error_message: str,
    code_snippet: str,
    language: str = "python",
    expected_behavior: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get AI help with debugging code issues"""
    try:
        debug_prompt = f"""
        Help debug this {language} code issue:
        
        Error Message: {error_message}
        
        Code:
        ```{language}
        {code_snippet}
        ```
        
        Expected Behavior: {expected_behavior or 'Not specified'}
        
        Please provide:
        1. Explanation of the error
        2. Step-by-step debugging approach
        3. Specific fix suggestions
        4. Prevention strategies for similar issues
        """
        
        debug_result = await openai_service.code_assistance(
            code_query=debug_prompt,
            language=language,
            context="Debugging assistance"
        )
        
        # Save to database
        assistance_log = CodeAssistanceLog(
            query=f"Debug assistance for {language}: {error_message[:100]}",
            language=language,
            context=f"Error: {error_message}",
            assistance_response=debug_result["assistance"],
            token_count=debug_result["token_count"]
        )
        db.add(assistance_log)
        db.commit()
        
        return {
            "debug_assistance": debug_result["assistance"],
            "error_message": error_message,
            "language": language,
            "generated_at": debug_result["generated_at"],
            "token_count": debug_result["token_count"]
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Debug assistance error: {str(e)}")

@router.get("/history")
async def get_assistance_history(
    user_id: Optional[int] = None,  # TODO: Get from authenticated user
    language: Optional[str] = None,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """Get code assistance history"""
    try:
        query = db.query(CodeAssistanceLog)
        
        if user_id:
            query = query.filter(CodeAssistanceLog.user_id == user_id)
        
        if language:
            query = query.filter(CodeAssistanceLog.language == language)
        
        assistance_history = query.order_by(
            CodeAssistanceLog.created_at.desc()
        ).limit(limit).all()
        
        return [
            {
                "id": log.id,
                "query": log.query,
                "language": log.language,
                "assistance_response": log.assistance_response,
                "created_at": log.created_at.isoformat(),
                "was_helpful": log.was_helpful,
                "user_rating": log.user_rating
            }
            for log in assistance_history
        ]
        
    except Exception as e:\n        raise HTTPException(status_code=500, detail=f\"Error retrieving assistance history: {str(e)}\")\n\n@router.post(\"/feedback/{assistance_id}\")\nasync def provide_feedback(\n    assistance_id: int,\n    was_helpful: bool,\n    rating: Optional[int] = None,\n    db: Session = Depends(get_db)\n):\n    \"\"\"Provide feedback on code assistance\"\"\"\n    try:\n        assistance_log = db.query(CodeAssistanceLog).filter(\n            CodeAssistanceLog.id == assistance_id\n        ).first()\n        \n        if not assistance_log:\n            raise HTTPException(status_code=404, detail=\"Assistance log not found\")\n        \n        assistance_log.was_helpful = was_helpful\n        if rating and 1 <= rating <= 5:\n            assistance_log.user_rating = rating\n        \n        db.commit()\n        \n        return {\"message\": \"Feedback recorded successfully\"}\n        \n    except Exception as e:\n        db.rollback()\n        raise HTTPException(status_code=500, detail=f\"Error recording feedback: {str(e)}\")\n"}}
</function_results>

<function_calls>
<invoke name="mark_todo_as_done">
<parameter name="todo_ids">["41a54e15-457f-44cc-90dd-aa84d77fbd83"]
