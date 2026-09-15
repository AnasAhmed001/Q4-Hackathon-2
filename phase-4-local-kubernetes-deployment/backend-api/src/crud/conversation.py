"""
CRUD operations for Conversation in the Todo AI Chatbot
Handles database operations for conversation entities with user isolation.
"""

from datetime import datetime
from typing import List, Optional
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from uuid import UUID

from ..models.conversation import Conversation, ConversationCreate
from ..schemas.conversation import ConversationRead


async def create_conversation(*, session: AsyncSession, conversation_create: ConversationCreate) -> Conversation:
    """
    Create a new conversation in the database.

    Args:
        session: Database session
        conversation_create: Data for creating the conversation

    Returns:
        The created Conversation object
    """
    conversation = Conversation.model_validate(conversation_create)
    conversation.created_at = datetime.utcnow()
    conversation.updated_at = datetime.utcnow()
    session.add(conversation)
    await session.commit()
    await session.refresh(conversation)
    return conversation


async def get_conversation_by_id(*, session: AsyncSession, conversation_id: UUID, user_id: str) -> Optional[Conversation]:
    """
    Retrieve a conversation by its ID for a specific user.

    Args:
        session: Database session
        conversation_id: ID of the conversation to retrieve
        user_id: ID of the user requesting the conversation

    Returns:
        The Conversation object if found and owned by user, otherwise None
    """
    statement = select(Conversation).where(
        Conversation.id == conversation_id,
        Conversation.user_id == user_id
    )
    result = await session.exec(statement)
    return result.first()


async def get_conversations_by_user(*, session: AsyncSession, user_id: str, skip: int = 0, limit: int = 100) -> List[Conversation]:
    """
    Retrieve all conversations for a specific user.

    Args:
        session: Database session
        user_id: ID of the user whose conversations to retrieve
        skip: Number of records to skip
        limit: Maximum number of records to return

    Returns:
        List of Conversation objects for the user
    """
    statement = select(Conversation).where(Conversation.user_id == user_id).offset(skip).limit(limit)
    result = await session.exec(statement)
    return result.all()


async def update_conversation(*, session: AsyncSession, conversation: Conversation, update_data: dict) -> Conversation:
    """
    Update an existing conversation.

    Args:
        session: Database session
        conversation: Conversation object to update
        update_data: Dictionary of fields to update

    Returns:
        The updated Conversation object
    """
    for field, value in update_data.items():
        setattr(conversation, field, value)
    conversation.updated_at = datetime.utcnow()
    session.add(conversation)
    await session.commit()
    await session.refresh(conversation)
    return conversation


async def delete_conversation(*, session: AsyncSession, conversation: Conversation) -> bool:
    """
    Delete a conversation from the database.

    Args:
        session: Database session
        conversation: Conversation object to delete

    Returns:
        True if deletion was successful
    """
    await session.delete(conversation)
    await session.commit()
    return True