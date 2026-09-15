"""
Chat API endpoints for the Todo AI Chatbot
Handles chat interactions and conversation management via HTTP endpoints.
"""

from datetime import datetime
from typing import Any, Dict, List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from .. import crud, models, schemas
from ..api.deps import get_db_session, validate_user_access_dependency
from ..auth.jwt_validator import JWTUser
from ..services.chat_service import ChatService

router = APIRouter()


@router.post("/{user_id}/chat", response_model=schemas.ChatResponse)
async def chat_with_bot(
    user_id: str,
    message: schemas.ChatRequest,
    db: AsyncSession = Depends(get_db_session),
    current_user: JWTUser = Depends(validate_user_access_dependency)
):
    """
    Send a message to the chatbot and receive a response.

    Processes natural language input and performs appropriate task operations.
    """
    # Verify that the user_id in the path matches the authenticated user
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this user's conversations"
        )

    # JWT validation already confirmed the user. Skip ORM lookup to avoid schema
    # mismatch with Better Auth user table (e.g., hashed_password not present).

    # Initialize the chat service
    chat_service = ChatService(db_session=db)

    # Process the message and get response
    response = await chat_service.process_message(
        user_id=user_id,
        message_content=message.message,
        conversation_id=message.conversation_id
    )

    return response


@router.get("/{user_id}/conversations", response_model=schemas.ConversationList)
async def list_user_conversations(
    user_id: str,
    skip: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(get_db_session),
    current_user: JWTUser = Depends(validate_user_access_dependency)
):
    """
    List all conversations for a specific user.
    """
    # Verify that the user_id in the path matches the authenticated user
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this user's conversations"
        )

    # Get conversations for the user
    conversations = await crud.conversation.get_conversations_by_user(
        session=db,
        user_id=user_id,
        skip=skip,
        limit=limit
    )

    # Count total conversations for the user
    total_statement = select(models.Conversation).where(models.Conversation.user_id == user_id)
    total_result = await db.exec(total_statement)
    total_count = len(total_result.all())

    return schemas.ConversationList(
        conversations=conversations,
        total_count=total_count
    )


@router.get("/{user_id}/conversations/{conversation_id}", response_model=schemas.MessageList)
async def get_conversation_history(
    user_id: str,
    conversation_id: UUID,
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db_session),
    current_user: JWTUser = Depends(validate_user_access_dependency)
):
    """
    Get the message history for a specific conversation.
    """
    # Verify that the user_id in the path matches the authenticated user
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this user's conversations"
        )

    # Verify that the conversation belongs to the user
    conversation = await crud.conversation.get_conversation_by_id(
        session=db,
        conversation_id=conversation_id,
        user_id=user_id
    )

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )

    # Get messages for the conversation
    messages = await crud.message.get_messages_by_conversation(
        session=db,
        conversation_id=conversation_id,
        user_id=user_id,
        skip=skip,
        limit=limit
    )

    # Count total messages in the conversation
    total_statement = select(models.Message).where(
        models.Message.conversation_id == conversation_id,
        models.Message.user_id == user_id
    )
    total_result = await db.exec(total_statement)
    total_count = len(total_result.all())

    return schemas.MessageList(
        messages=messages,
        total_count=total_count
    )