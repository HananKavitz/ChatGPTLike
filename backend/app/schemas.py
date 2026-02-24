"""Pydantic schemas for request/response validation"""
from pydantic import BaseModel, EmailStr, Field, ConfigDict, model_validator
from typing import Optional, List, Any, Dict
from datetime import datetime


# Auth Schemas
class UserRegister(BaseModel):
    """User registration schema"""
    email: EmailStr
    password: str = Field(..., min_length=6)


class UserLogin(BaseModel):
    """User login schema"""
    email: EmailStr
    password: str


class Token(BaseModel):
    """JWT token response"""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Token data payload"""
    user_id: Optional[int] = None
    email: Optional[str] = None


class UserResponse(BaseModel):
    """User response schema"""
    id: int
    email: str
    openai_model: str
    has_api_key: bool = False
    llm_provider: str = "openai"
    anthropic_model: Optional[str] = None
    openrouter_model: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


class UserUpdate(BaseModel):
    """User update schema"""
    openai_api_key: Optional[str] = None
    openai_model: Optional[str] = None
    password: Optional[str] = Field(None, min_length=6)

    # Multi-provider fields
    llm_provider: Optional[str] = Field(None, pattern="^(openai|anthropic|openrouter)$")  # Validate provider name
    anthropic_api_key: Optional[str] = None
    anthropic_model: Optional[str] = None
    openrouter_api_key: Optional[str] = None
    openrouter_model: Optional[str] = None


# Chat Session Schemas
class SessionCreate(BaseModel):
    """Create chat session schema"""
    name: Optional[str] = None


class SessionUpdate(BaseModel):
    """Update chat session schema"""
    name: str


class SessionResponse(BaseModel):
    """Chat session response"""
    id: int
    name: Optional[str]
    created_at: datetime
    updated_at: datetime
    message_count: int = 0
    model_config = ConfigDict(from_attributes=True)


class SessionDetail(SessionResponse):
    """Chat session with messages"""
    messages: List["MessageResponse"] = []


# Message Schemas
class MessageCreate(BaseModel):
    """Create message schema"""
    content: str
    stream: bool = True


class MessageUpdate(BaseModel):
    """Update message schema"""
    content: str


class MessageResponse(BaseModel):
    """Message response schema"""
    id: int
    role: str
    content: str
    is_edited: bool
    created_at: datetime
    visualizations: List["VisualizationResponse"] = []
    model_config = ConfigDict(from_attributes=True)


class StreamChunk(BaseModel):
    """Streaming response chunk"""
    role: str = "assistant"
    content: str = ""
    done: bool = False


# File Schemas
class FileResponse(BaseModel):
    """File response schema"""
    id: int
    filename: str
    original_filename: str
    file_size: int
    mime_type: Optional[str]
    uploaded_at: datetime
    model_config = ConfigDict(from_attributes=True)


# Visualization Schemas
class VisualizationResponse(BaseModel):
    """Visualization response schema"""
    id: int
    chart_type: str
    chart_config: Any
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode='before')
    def parse_chart_config(cls, data):
        """Parse chart_config from JSON string if needed"""
        import json

        if isinstance(data, dict) and 'chart_config' in data:
            chart_config = data['chart_config']
            if isinstance(chart_config, str):
                try:
                    data['chart_config'] = json.loads(chart_config)
                except (json.JSONDecodeError, TypeError):
                    data['chart_config'] = {}

        return data


# Update forward references
SessionDetail.model_rebuild()
