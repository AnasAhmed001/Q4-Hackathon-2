"""
Schema definitions for Chat endpoints in the Todo AI Chatbot
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from uuid import UUID


class ChatRequest(BaseModel):
    """Request schema for chat endpoint."""
    message: str = Field(..., min_length=1, description="User's natural language message")
    conversation_id: Optional[UUID] = Field(None, description="Existing conversation ID")


class ToolCallSchema(BaseModel):
    """Schema for tool call metadata returned by the agent."""
    name: str
    arguments: Optional[Dict[str, Any]] = None


class ToolResponseSchema(BaseModel):
    """Schema for tool response metadata returned by the agent."""
    name: str
    output: Any


class ChatResponse(BaseModel):
    """Response schema for chat endpoint."""
    conversation_id: Optional[UUID]
    response: str
    tool_calls: List[ToolCallSchema] = Field(default_factory=list)
    tool_responses: List[ToolResponseSchema] = Field(default_factory=list)
