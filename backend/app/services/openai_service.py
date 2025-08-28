import openai
from typing import List, Dict, Optional, AsyncGenerator
import json
from datetime import datetime
import logging

from app.core.config import settings
from app.schemas.chat import ChatMessage, ChatResponse
from app.schemas.health import HealthRecommendation

logger = logging.getLogger(__name__)

class OpenAIService:
    def __init__(self):
        self.client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL
        self.max_tokens = settings.MAX_TOKENS
        self.temperature = settings.TEMPERATURE

    async def chat_completion(
        self, 
        messages: List[Dict[str, str]], 
        system_prompt: Optional[str] = None,
        stream: bool = False
    ) -> ChatResponse:
        """General chat completion for user interactions"""
        try:
            if system_prompt:
                messages.insert(0, {"role": "system", "content": system_prompt})
            
            if stream:
                return await self._stream_completion(messages)
            else:
                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    max_tokens=self.max_tokens,
                    temperature=self.temperature
                )
                
                return ChatResponse(
                    message=response.choices[0].message.content,
                    token_usage=response.usage.total_tokens,
                    model=self.model,
                    timestamp=datetime.utcnow()
                )
        except Exception as e:
            logger.error(f"Chat completion error: {e}")
            raise

    async def _stream_completion(self, messages: List[Dict[str, str]]) -> AsyncGenerator[str, None]:
        """Stream chat completion for real-time responses"""
        try:
            stream = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                stream=True
            )
            
            async for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            logger.error(f"Stream completion error: {e}")
            raise

    async def health_recommendation(
        self, 
        user_profile: Dict, 
        health_data: Dict, 
        symptoms: Optional[List[str]] = None
    ) -> HealthRecommendation:
        """Generate AI-powered health recommendations"""
        
        system_prompt = """
        You are a professional health and wellness AI assistant. Provide personalized health recommendations based on user data.
        IMPORTANT: Always include medical disclaimers and recommend consulting healthcare professionals for serious concerns.
        Focus on: nutrition, exercise, mental wellness, sleep, and preventive care.
        """
        
        user_context = f"""
        User Profile:
        - Age: {user_profile.get('age', 'Not specified')}
        - Gender: {user_profile.get('gender', 'Not specified')}
        - Activity Level: {user_profile.get('activity_level', 'Not specified')}
        - Health Goals: {user_profile.get('health_goals', 'Not specified')}
        
        Current Health Data:
        - Weight: {health_data.get('weight', 'Not specified')}
        - Height: {health_data.get('height', 'Not specified')}
        - Blood Pressure: {health_data.get('blood_pressure', 'Not specified')}
        - Sleep Hours: {health_data.get('sleep_hours', 'Not specified')}
        
        Symptoms (if any): {symptoms or 'None reported'}
        
        Please provide personalized health recommendations including:
        1. Nutrition advice
        2. Exercise recommendations
        3. Lifestyle improvements
        4. When to seek medical attention
        """
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_context}
        ]
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=1500,
                temperature=0.7
            )
            
            return HealthRecommendation(
                recommendations=response.choices[0].message.content,
                user_profile=user_profile,
                generated_at=datetime.utcnow(),
                confidence_score=0.85,  # Could be calculated based on data completeness
                categories=["nutrition", "exercise", "lifestyle", "preventive"]
            )
        except Exception as e:
            logger.error(f"Health recommendation error: {e}")
            raise

    async def generate_content(
        self, 
        content_type: str, 
        topic: str, 
        target_audience: str = "general",
        length: str = "medium"
    ) -> Dict[str, str]:
        """Generate health and wellness content"""
        
        length_guidelines = {
            "short": "200-300 words",
            "medium": "500-700 words", 
            "long": "1000-1500 words"
        }
        
        system_prompt = f"""
        You are a professional health and wellness content writer. Create engaging, accurate, and helpful content.
        Content Type: {content_type}
        Target Audience: {target_audience}
        Length: {length_guidelines.get(length, "500-700 words")}
        
        Ensure content is:
        - Scientifically accurate
        - Easy to understand
        - Actionable
        - Includes appropriate disclaimers
        """
        
        user_prompt = f"Create {content_type} content about: {topic}"
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=2000,
                temperature=0.8
            )
            
            return {
                "content": response.choices[0].message.content,
                "type": content_type,
                "topic": topic,
                "audience": target_audience,
                "generated_at": datetime.utcnow().isoformat(),
                "token_count": response.usage.total_tokens
            }
        except Exception as e:
            logger.error(f"Content generation error: {e}")
            raise

    async def code_assistance(
        self, 
        code_query: str, 
        language: str = "python",
        context: Optional[str] = None
    ) -> Dict[str, str]:
        """Provide code assistance for development tasks"""
        
        system_prompt = f"""
        You are an expert software developer specializing in {language} and web development.
        Help with code review, debugging, optimization, and best practices.
        Focus on clean, maintainable, and efficient code.
        """
        
        user_context = f"""
        Programming Language: {language}
        Query: {code_query}
        Additional Context: {context or 'None provided'}
        
        Please provide:
        1. Clear explanation
        2. Code examples (if applicable)
        3. Best practices
        4. Potential improvements
        """
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_context}
        ]
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=1500,
                temperature=0.3  # Lower temperature for more precise code assistance
            )
            
            return {
                "assistance": response.choices[0].message.content,
                "language": language,
                "query": code_query,
                "generated_at": datetime.utcnow().isoformat(),
                "token_count": response.usage.total_tokens
            }
        except Exception as e:
            logger.error(f"Code assistance error: {e}")
            raise

# Singleton instance
openai_service = OpenAIService()
