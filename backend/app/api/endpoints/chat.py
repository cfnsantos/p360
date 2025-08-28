from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from typing import List
import uuid
import json
from datetime import datetime

from app.db.database import get_db
from app.schemas.chat import ChatRequest, ChatResponse, ConversationHistory, StreamChatResponse
from app.services.openai_service import openai_service
from app.models.models import Conversation, Message, User

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

manager = ConnectionManager()

@router.post("/", response_model=ChatResponse)
async def chat_with_ai(
    request: ChatRequest,
    db: Session = Depends(get_db)
):
    """Send a message to ChatGPT and get a response"""
    try:
        # Create or get conversation
        conversation_id = request.conversation_id or str(uuid.uuid4())
        
        conversation = db.query(Conversation).filter(
            Conversation.conversation_id == conversation_id
        ).first()
        
        if not conversation:
            conversation = Conversation(
                conversation_id=conversation_id,
                user_id=1,  # TODO: Get from authenticated user
                title=request.message[:50] + "..." if len(request.message) > 50 else request.message
            )
            db.add(conversation)
            db.commit()
            db.refresh(conversation)
        
        # Get conversation history
        messages_history = db.query(Message).filter(
            Message.conversation_id == conversation.id
        ).order_by(Message.created_at).all()
        
        # Prepare messages for OpenAI
        openai_messages = []
        for msg in messages_history:
            openai_messages.append({
                "role": msg.role,
                "content": msg.content
            })
        
        # Add current user message
        openai_messages.append({
            "role": "user", 
            "content": request.message
        })
        
        # System prompt for health and wellness context
        system_prompt = request.system_prompt or """
        You are P360's AI health and wellness assistant. You help users with:
        - General health questions and advice
        - Wellness tips and recommendations
        - Lifestyle guidance for better health
        - Mental health and stress management
        
        Always provide helpful, accurate information while reminding users to consult healthcare professionals for medical concerns.
        Be empathetic, supportive, and encouraging in your responses.
        """
        
        # Get AI response
        ai_response = await openai_service.chat_completion(
            messages=openai_messages,
            system_prompt=system_prompt,
            stream=request.stream
        )
        
        # Save user message
        user_message = Message(
            conversation_id=conversation.id,
            role="user",
            content=request.message
        )
        db.add(user_message)
        
        # Save AI response
        ai_message = Message(
            conversation_id=conversation.id,
            role="assistant",
            content=ai_response.message,
            token_count=ai_response.token_usage
        )
        db.add(ai_message)
        
        # Update conversation timestamp
        conversation.updated_at = datetime.utcnow()
        
        db.commit()
        
        ai_response.conversation_id = conversation_id
        return ai_response
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")

@router.get("/conversations/{conversation_id}", response_model=ConversationHistory)
async def get_conversation_history(
    conversation_id: str,
    db: Session = Depends(get_db)
):
    """Get conversation history by ID"""
    conversation = db.query(Conversation).filter(
        Conversation.conversation_id == conversation_id
    ).first()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    messages = db.query(Message).filter(
        Message.conversation_id == conversation.id
    ).order_by(Message.created_at).all()
    
    return ConversationHistory(
        conversation_id=conversation_id,
        messages=[
            {
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.created_at
            }
            for msg in messages
        ],
        created_at=conversation.created_at,
        updated_at=conversation.updated_at,
        user_id=conversation.user_id
    )

@router.get("/conversations")
async def get_user_conversations(
    user_id: int = 1,  # TODO: Get from authenticated user
    db: Session = Depends(get_db)
):
    """Get all conversations for a user"""
    conversations = db.query(Conversation).filter(
        Conversation.user_id == user_id,
        Conversation.is_active == True
    ).order_by(Conversation.updated_at.desc()).all()
    
    return [
        {
            "conversation_id": conv.conversation_id,
            "title": conv.title,
            "created_at": conv.created_at,
            "updated_at": conv.updated_at,
            "message_count": len(conv.messages)
        }
        for conv in conversations
    ]

@router.websocket("/ws/{conversation_id}")
async def websocket_chat(websocket: WebSocket, conversation_id: str):
    """WebSocket endpoint for real-time chat"""
    await manager.connect(websocket)
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Prepare for streaming response
            await manager.send_personal_message(
                json.dumps({"type": "stream_start"}), 
                websocket
            )
            
            # Stream AI response
            openai_messages = [{"role": "user", "content": message_data["message"]}]
            
            full_response = ""
            async for chunk in openai_service._stream_completion(openai_messages):
                full_response += chunk
                await manager.send_personal_message(
                    json.dumps({
                        "type": "stream_chunk",
                        "content": chunk
                    }), 
                    websocket
                )
            
            # Send completion signal
            await manager.send_personal_message(
                json.dumps({
                    "type": "stream_complete",
                    "full_response": full_response
                }), 
                websocket
            )
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
