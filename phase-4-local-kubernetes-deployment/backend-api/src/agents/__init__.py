"""
Agents Package for Todo AI Chatbot

This package contains all AI agent-related functionality for the Todo AI Chatbot,
including MCP tool adapters (Cohere-compatible) and agent configuration.
"""

from .mcp_adapters import (
    COHERE_TOOLS,
    TOOL_FUNCTIONS,
)

from .agent_config import (
    AgentPersonality,
    COHERE_MODEL,
    MAX_TOOL_TURNS,
    get_cohere_client,
    get_system_instruction,
)

__all__ = [
    # MCP Adapters (Cohere format)
    'COHERE_TOOLS',
    'TOOL_FUNCTIONS',

    # Agent Configuration
    'AgentPersonality',
    'COHERE_MODEL',
    'MAX_TOOL_TURNS',
    'get_cohere_client',
    'get_system_instruction',
]