"""
CRUD operations for Message in the Todo AI Chatbot
Handles database operations for message entities with user isolation.
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from ..models.message import Message, MessageCreate
from ..schemas.message import MessageRead


async def create_message(*, session: AsyncSession, message_create: MessageCreate) -> Message:
    """
    Create a new message in the database.

    Args:
        session: Database session
        message_create: Data for creating the message

    Returns:
        The created Message object
    """
    message = Message.model_validate(message_create)
    message.created_at = datetime.utcnow()
    session.add(message)
    await session.commit()
    await session.refresh(message)
    return message


async def get_message_by_id(*, session: AsyncSession, message_id: UUID, user_id: str) -> Optional[Message]:
    """
    Retrieve a message by its ID for a specific user.

    Args:
        session: Database session
        message_id: ID of the message to retrieve
        user_id: ID of the user requesting the message

    Returns:
        The Message object if found and owned by user, otherwise None
    """
    statement = select(Message).where(
        Message.id == message_id,
        Message.user_id == user_id
    )
    result = await session.exec(statement)
    return result.first()


async def get_messages_by_conversation(*, session: AsyncSession, conversation_id: UUID, user_id: str, skip: int = 0, limit: int = 100) -> List[Message]:
    """
    Retrieve all messages for a specific conversation and user.

    Args:
        session: Database session
        conversation_id: ID of the conversation whose messages to retrieve
        user_id: ID of the user requesting the messages
        skip: Number of records to skip
        limit: Maximum number of records to return

    Returns:
        List of Message objects for the conversation
    """
    statement = select(Message).where(
        Message.conversation_id == conversation_id,
        Message.user_id == user_id
    ).order_by(Message.created_at.asc()).offset(skip).limit(limit)
    result = await session.exec(statement)
    return result.all()


async def get_latest_messages(*, session: AsyncSession, user_id: str, limit: int = 10) -> List[Message]:
    """
    Retrieve the latest messages for a specific user.

    Args:
        session: Database session
        user_id: ID of the user whose messages to retrieve
        limit: Maximum number of messages to return

    Returns:
        List of latest Message objects for the user
    """
    statement = select(Message).where(
        Message.user_id == user_id
    ).order_by(Message.created_at.desc()).limit(limit)
    result = await session.exec(statement)
    return result.all()


async def update_message(*, session: AsyncSession, message: Message, update_data: dict) -> Message:
    """
    Update an existing message.

    Args:
        session: Database session
        message: Message object to update
        update_data: Dictionary of fields to update

    Returns:
        The updated Message object
    """
    for field, value in update_data.items():
        setattr(message, field, value)
    session.add(message)
    await session.commit()
    await session.refresh(message)
    return message


async def delete_message(*, session: AsyncSession, message: Message) -> bool:
    """
    Delete a message from the database.

    Args:
        session: Database session
        message: Message object to delete

    Returns:
        True if deletion was successful
    """
    await session.delete(message)
    await session.commit()
    return True