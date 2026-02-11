"""
AI Agent Configuration for Cohere V2 API

This module provides configuration classes for the Cohere-powered chatbot:
system instructions, personality definitions, and the Cohere client factory.
MCP tools remain unchanged — only the LLM layer changed from
OpenAI Agents SDK + Gemini → Cohere V2 (command-a-03-2025).
"""

import os
from typing import Dict, Optional
from dotenv import load_dotenv
from enum import Enum
import cohere

load_dotenv()

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
COHERE_MODEL = os.getenv("COHERE_MODEL", "command-a-03-2025")
MAX_TOOL_TURNS = 15  # safety limit for the tool-calling loop


class AgentPersonality(str, Enum):
    """Different personality types for AI agents."""
    HELPFUL_ASSISTANT = "helpful_assistant"
    TASK_MANAGER = "task_manager"
    PRODUCTIVITY_COACH = "productivity_coach"
    ORGANIZATIONAL_EXPERT = "organizational_expert"


# ---------------------------------------------------------------------------
# System instructions per personality
# ---------------------------------------------------------------------------
PERSONALITY_INSTRUCTIONS: Dict[AgentPersonality, str] = {
    AgentPersonality.HELPFUL_ASSISTANT: (
        "You are a task management assistant. Help users create, update, complete, and delete tasks using the available tools. Be concise. "
        "IMPORTANT: When the user asks to delete, update, or complete multiple/all tasks, ALWAYS call list_tasks first to get every task ID, then operate on each one. Never rely only on task IDs from the conversation history."
    ),
    AgentPersonality.TASK_MANAGER: (
        "You are a task management expert. Help users organize tasks, suggest due dates, and prioritize. Use the available tools. "
        "IMPORTANT: When the user asks to delete, update, or complete multiple/all tasks, ALWAYS call list_tasks first to get every task ID, then operate on each one."
    ),
    AgentPersonality.PRODUCTIVITY_COACH: (
        "You are a productivity coach. Help users manage tasks efficiently with tips on prioritization. Use the available tools. "
        "IMPORTANT: When the user asks to delete, update, or complete multiple/all tasks, ALWAYS call list_tasks first to get every task ID, then operate on each one."
    ),
    AgentPersonality.ORGANIZATIONAL_EXPERT: (
        "You are an organizational expert. Help users create task management strategies and workflows. Use the available tools. "
        "IMPORTANT: When the user asks to delete, update, or complete multiple/all tasks, ALWAYS call list_tasks first to get every task ID, then operate on each one."
    ),
}


def get_system_instruction(
    personality: AgentPersonality = AgentPersonality.HELPFUL_ASSISTANT,
    user_id: Optional[str] = None,
) -> str:
    """Return the system instruction, optionally injecting the user_id."""
    base = PERSONALITY_INSTRUCTIONS.get(
        personality,
        PERSONALITY_INSTRUCTIONS[AgentPersonality.HELPFUL_ASSISTANT],
    )
    if user_id:
        base += f"\n\nUser ID: {user_id}. Always use this user_id when calling tools."
    return base


# ---------------------------------------------------------------------------
# Cohere async client (singleton-ish)
# ---------------------------------------------------------------------------
_cohere_client: Optional[cohere.AsyncClientV2] = None


def get_cohere_client() -> cohere.AsyncClientV2:
    """Return a reusable async Cohere V2 client."""
    global _cohere_client
    if _cohere_client is None:
        api_key = os.getenv("COHERE_API_KEY", "")
        if not api_key:
            raise RuntimeError("COHERE_API_KEY environment variable is not set")
        _cohere_client = cohere.AsyncClientV2(api_key=api_key)
    return _cohere_client