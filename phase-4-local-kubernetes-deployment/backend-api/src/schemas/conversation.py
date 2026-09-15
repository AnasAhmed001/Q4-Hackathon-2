"""
Schema definitions for Conversation in the Todo AI Chatbot
Provides Pydantic models for request/response validation and serialization.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from uuid import UUID


class ConversationBase(BaseModel):
    """Base schema for Conversation with shared attributes."""
    title: Optional[str] = Field(None, max_length=255, description="Optional title for the conversation")
    user_id: str = Field(..., description="ID of the user who owns this conversation")


class ConversationCreate(ConversationBase):
    """Schema for creating a new conversation."""
    pass


class ConversationUpdate(BaseModel):
    """Schema for updating an existing conversation."""
    title: Optional[str] = Field(None, max_length=255)


class ConversationRead(ConversationBase):
    """Schema for reading conversation data."""
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ConversationList(BaseModel):
    """Schema for listing conversations."""
    conversations: List[ConversationRead]
    total_count: int