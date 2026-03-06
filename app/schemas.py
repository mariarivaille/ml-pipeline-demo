from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class Message(BaseModel):
    role: str = Field(..., pattern="^(user|assistant|system)$")
    content: str = Field(..., min_length=1, max_length=4000)

class ChatRequest(BaseModel):
    messages: List[Message]
    stream: bool = False
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None

class ChatResponse(BaseModel):
    response: str
    model: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    usage: Optional[Dict[str, int]] = None
    demo_mode: bool = False

class HealthResponse(BaseModel):
    status: str
    model: str
    demo_mode: bool
    version: str

class StreamingChunk(BaseModel):
    delta: str
    finish_reason: Optional[str] = None