"""
Schema definitions for Message in the Todo AI Chatbot
Provides Pydantic models for request/response validation and serialization.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from uuid import UUID


class MessageBase(BaseModel):
    """Base schema for Message with shared attributes."""
    conversation_id: UUID = Field(..., description="ID of the conversation this message belongs to")
    user_id: str = Field(..., description="ID of the user who sent this message")
    role: str = Field(..., pattern=r'^(user|assistant)$', description="Role of the sender ('user' or 'assistant')")
    content: str = Field(..., max_length=10000, description="Content of the message")
    tool_calls: Optional[Dict[str, Any]] = Field(None, description="Optional tool calls made during this message")
    tool_responses: Optional[Dict[str, Any]] = Field(None, description="Optional responses from tools")


class MessageCreate(MessageBase):
    """Schema for creating a new message."""
    pass


class MessageUpdate(BaseModel):
    """Schema for updating an existing message."""
    content: Optional[str] = Field(None, max_length=10000)


class MessageRead(MessageBase):
    """Schema for reading message data."""
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


class MessageList(BaseModel):
    """Schema for listing messages."""
    messages: List[MessageRead]
    total_count: int