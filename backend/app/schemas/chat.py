from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime
from enum import Enum

class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

class ChatMessage(BaseModel):
    role: MessageRole
    content: str
    timestamp: Optional[datetime] = None

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    system_prompt: Optional[str] = None
    stream: bool = False

class ChatResponse(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    token_usage: Optional[int] = None
    model: str
    timestamp: datetime

class ConversationHistory(BaseModel):
    conversation_id: str
    messages: List[ChatMessage]
    created_at: datetime
    updated_at: datetime
    user_id: Optional[int] = None

class StreamChatResponse(BaseModel):
    chunk: str
    conversation_id: Optional[str] = None
    is_complete: bool = False
