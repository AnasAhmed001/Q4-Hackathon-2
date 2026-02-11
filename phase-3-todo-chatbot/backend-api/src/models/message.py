"""
Message model for the Todo AI Chatbot
Defines the message entity that stores individual chat messages within a conversation.
"""

from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import Column, JSON
from sqlmodel import Field, SQLModel
from uuid import UUID, uuid4


class MessageBase(SQLModel):
    """Base class for Message model with shared attributes."""
    conversation_id: UUID = Field(index=True, foreign_key="conversation.id")
    user_id: str = Field(index=True)  # References the authenticated user ID
    role: str = Field(regex="^(user|assistant)$", max_length=20)  # Role: 'user' or 'assistant'
    content: str = Field(max_length=10000)  # Content of the message
    tool_calls: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    tool_responses: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))


class Message(MessageBase, table=True):
    """
    Message model representing individual messages in a conversation.
    """
    __tablename__ = "message"

    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)


class MessageCreate(MessageBase):
    """Schema for creating a new message."""
    pass


class MessageRead(MessageBase):
    """Schema for reading message data."""
    id: UUID
    created_at: datetime