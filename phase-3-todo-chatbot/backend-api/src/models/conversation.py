"""
Conversation model for the Todo AI Chatbot
Defines the conversation entity that stores chat history between users and the AI assistant.
"""

from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel
from uuid import UUID, uuid4


class ConversationBase(SQLModel):
    """Base class for Conversation model with shared attributes."""
    title: Optional[str] = Field(default=None, max_length=255)
    user_id: str = Field(index=True)  # References the authenticated user ID


class Conversation(ConversationBase, table=True):
    """
    Conversation model representing a series of interactions between user and chatbot.
    """
    __tablename__ = "conversation"

    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)


class ConversationCreate(ConversationBase):
    """Schema for creating a new conversation."""
    pass


class ConversationRead(ConversationBase):
    """Schema for reading conversation data."""
    id: UUID
    created_at: datetime
    updated_at: datetime