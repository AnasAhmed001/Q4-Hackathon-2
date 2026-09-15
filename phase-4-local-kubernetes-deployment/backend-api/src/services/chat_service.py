"""
Chat Service for the Todo AI Chatbot — Cohere V2 Edition

Implements the tool-calling loop:
  1. Build messages (system + history + new user message)
  2. Call Cohere chat with tools
  3. If the model requests tool calls → execute them → feed results back → repeat
  4. Return the final text response
"""

import asyncio
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID
from sqlmodel.ext.asyncio.session import AsyncSession
import json
import logging

from .. import crud, models, schemas
from ..agents.agent_config import (
    AgentPersonality,
    COHERE_MODEL,
    MAX_TOOL_TURNS,
    get_cohere_client,
    get_system_instruction,
)
from ..agents.mcp_adapters import COHERE_TOOLS, TOOL_FUNCTIONS


class ChatService:
    """
    Service class for handling chat interactions via Cohere V2 + MCP tools.
    """

    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
        self.logger = logging.getLogger(__name__)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def process_message(
        self,
        user_id: str,
        message_content: str,
        conversation_id: Optional[UUID] = None,
    ) -> Dict[str, Any]:
        try:
            self.logger.info(
                "Processing message for user %s in conversation %s",
                user_id,
                conversation_id,
            )

            conversation = await self._get_or_create_conversation(user_id, conversation_id)
            self.logger.debug("Using conversation %s for user %s", conversation.id, user_id)

            # Load recent history (keep small for speed)
            history_messages = await crud.message.get_messages_by_conversation(
                session=self.db_session,
                conversation_id=conversation.id,
                user_id=user_id,
                skip=0,
                limit=10,
            )

            # Build the Cohere messages list
            messages = self._build_cohere_messages(history_messages, message_content, user_id)

            # Persist the user message
            await self._save_message(
                conversation_id=conversation.id,
                user_id=user_id,
                role="user",
                content=message_content,
            )

            # Run the Cohere tool-calling loop
            response_text, tool_calls, tool_responses = await self._run_tool_loop(messages)

            if not response_text:
                response_text = "I'm here to help you manage your tasks."

            # Persist the assistant message
            await self._save_message(
                conversation_id=conversation.id,
                user_id=user_id,
                role="assistant",
                content=response_text,
                tool_calls={"calls": tool_calls},
                tool_responses={"responses": tool_responses},
            )

            result = {
                "conversation_id": conversation.id,
                "response": response_text,
                "tool_calls": tool_calls,
                "tool_responses": tool_responses,
            }
            self.logger.info(
                "Completed processing message for user %s, conversation %s",
                user_id,
                conversation.id,
            )
            return result

        except Exception as e:
            self.logger.error(
                "Error processing message for user %s: %s", user_id, str(e), exc_info=True
            )
            return {
                "conversation_id": conversation_id,
                "response": "Sorry, I encountered an error processing your request.",
                "tool_calls": [],
                "tool_responses": [],
            }

    async def get_conversation_history(
        self, user_id: str, conversation_id: UUID, limit: int = 10, offset: int = 0
    ) -> List[models.Message]:
        return await crud.message.get_messages_by_conversation(
            session=self.db_session,
            conversation_id=conversation_id,
            user_id=user_id,
            skip=offset,
            limit=limit,
        )

    # ------------------------------------------------------------------
    # Cohere tool-calling loop
    # ------------------------------------------------------------------

    async def _run_tool_loop(
        self, messages: List[Dict[str, Any]]
    ) -> Tuple[str, List[Dict], List[Dict]]:
        """
        Repeatedly call Cohere chat until the model returns a text response
        (i.e. no more tool_calls), or we hit MAX_TOOL_TURNS.
        """
        client = get_cohere_client()
        all_tool_calls: List[Dict[str, Any]] = []
        all_tool_responses: List[Dict[str, Any]] = []

        for _ in range(MAX_TOOL_TURNS):
            response = await client.chat(
                model=COHERE_MODEL,
                messages=messages,
                tools=COHERE_TOOLS,
                temperature=0.3,
            )

            # If no tool calls, we have the final answer
            if not response.message.tool_calls:
                text = ""
                if response.message.content:
                    text = response.message.content[0].text
                return text, all_tool_calls, all_tool_responses

            # Append the assistant's tool-call turn
            messages.append(response.message)

            # Execute each tool call
            for tc in response.message.tool_calls:
                fn_name = tc.function.name
                fn_args = json.loads(tc.function.arguments) if tc.function.arguments else {}

                all_tool_calls.append({"name": fn_name, "arguments": fn_args})

                executor = TOOL_FUNCTIONS.get(fn_name)
                if executor:
                    tool_output = await executor(**fn_args)
                else:
                    tool_output = json.dumps({"error": f"Unknown tool: {fn_name}"})

                all_tool_responses.append({"name": fn_name, "output": tool_output})

                # Append tool result message
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": tool_output,
                })

        # If we exhausted turns, get one last response without tools
        response = await client.chat(
            model=COHERE_MODEL,
            messages=messages,
            temperature=0.3,
        )
        text = ""
        if response.message.content:
            text = response.message.content[0].text
        return text, all_tool_calls, all_tool_responses

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _build_cohere_messages(
        self,
        history: List[models.Message],
        message_content: str,
        user_id: str,
    ) -> List[Dict[str, Any]]:
        """Build the messages list for Cohere V2 chat."""
        messages: List[Dict[str, Any]] = []

        # System instruction
        system_text = get_system_instruction(
            AgentPersonality.HELPFUL_ASSISTANT, user_id=user_id
        )
        messages.append({"role": "system", "content": system_text})

        # Conversation history
        for msg in history:
            if msg.role not in {"user", "assistant"}:
                continue
            messages.append({"role": msg.role, "content": msg.content})

        # Current user message
        messages.append({"role": "user", "content": message_content})
        return messages

    async def _get_or_create_conversation(
        self, user_id: str, conversation_id: Optional[UUID] = None
    ) -> models.Conversation:
        if conversation_id:
            conversation = await crud.conversation.get_conversation_by_id(
                session=self.db_session,
                conversation_id=conversation_id,
                user_id=user_id,
            )
            if conversation:
                return conversation

        conversation_create = schemas.ConversationCreate(
            user_id=user_id,
            title=(
                f"Conversation with {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}"
                if not conversation_id
                else None
            ),
        )
        return await crud.conversation.create_conversation(
            session=self.db_session,
            conversation_create=conversation_create,
        )

    async def _save_message(
        self,
        conversation_id: UUID,
        user_id: str,
        role: str,
        content: str,
        tool_calls: Optional[Dict[str, Any]] = None,
        tool_responses: Optional[Dict[str, Any]] = None,
    ) -> models.Message:
        message_create = schemas.MessageCreate(
            conversation_id=conversation_id,
            user_id=user_id,
            role=role,
            content=content,
            tool_calls=tool_calls,
            tool_responses=tool_responses,
        )
        return await crud.message.create_message(
            session=self.db_session,
            message_create=message_create,
        )

