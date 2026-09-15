---
id: 052
title: "OpenAI Agents SDK Integration with OpenRouter and MCP Tools"
stage: "implementation"
date_iso: "2026-02-04"
surface: "agent"
model: "claude-sonnet-4-5-20250929"
feature: "todo-ai-chatbot"
branch: "001-todo-ai-chatbot"
user: "claude"
command: "implement openai-agents-sdk-integration"
labels: ["openai-agents", "openrouter", "mcp-tools", "integration", "todo-ai-chatbot"]
spec: null
ticket: null
adr: null
pr: null
---

# OpenAI Agents SDK Integration with OpenRouter and MCP Tools

## PROMPT_TEXT

Based on the updated tasks.md file that includes tasks for creating an AI agent using the OpenAI Agents SDK Python library with OpenRouter connected to MCP tools, provide detailed implementation guidance for the following tasks:

1. T051: Setting up OpenAI Agents SDK dependencies for OpenRouter integration
2. T052: Configuring LiteLLM to work with OpenRouter models
3. T053: Creating MCP tool adapter functions for OpenAI Agents SDK
4. T054: Creating AI agent configuration for OpenRouter

Please provide specific code examples and configuration details for each of these tasks.

## RESPONSE_TEXT

Successfully implemented all four tasks for integrating OpenAI Agents SDK with OpenRouter and MCP tools:

### T051: Setting up OpenAI Agents SDK dependencies for OpenRouter integration
- Updated `requirements.txt` to include `openai-agents`, `litellm`, and `pydantic`
- Updated `pyproject.toml` to include `openai-agents` and `litellm` dependencies
- Added proper dependency versions for compatibility

### T052: Configuring LiteLLM to work with OpenRouter models
- Created `src/config/litellm_config.py` with comprehensive configuration classes
- Implemented `LiteLLMConfig` and `ModelConfig` for different model types
- Created `OpenRouterConfig` with multiple model configurations (fast, balanced, creative, precise)
- Added validation and helper functions for easy integration

### T053: Creating MCP tool adapter functions for OpenAI Agents SDK
- Created `src/agents/mcp_adapters.py` with adapter functions for all MCP tools
- Implemented async adapter functions for: `create_task`, `list_tasks`, `update_task`, `complete_task`, `delete_task`
- Added Pydantic models for request validation
- Included proper error handling and JSON serialization
- Provided synchronous wrappers for compatibility

### T054: Creating AI agent configuration for OpenRouter
- Created `src/agents/agent_config.py` with comprehensive agent configuration system
- Implemented `TodoAIAssistantConfig` factory class for creating different agent personalities
- Defined multiple agent personalities (Helpful Assistant, Task Manager, Productivity Coach, Organizational Expert)
- Created `AgentRegistry` for managing multiple agents
- Added predefined configurations for common use cases
- Implemented proper model configuration with OpenRouter integration

### Additional Enhancements:
- Updated `.env.example` with OpenRouter configuration variables
- Created proper package structure with `__init__.py` in the agents directory
- Added comprehensive documentation and type hints throughout
- Implemented proper error handling and validation

## FILES_TOUCHED

- D:\My Work\Q4-Hackathon-2\phase-3-todo-chatbot\backend-api\requirements.txt
- D:\My Work\Q4-Hackathon-2\phase-3-todo-chatbot\backend-api\pyproject.toml
- D:\My Work\Q4-Hackathon-2\phase-3-todo-chatbot\backend-api\src\config\litellm_config.py
- D:\My Work\Q4-Hackathon-2\phase-3-todo-chatbot\backend-api\src\agents\mcp_adapters.py
- D:\My Work\Q4-Hackathon-2\phase-3-todo-chatbot\backend-api\src\agents\agent_config.py
- D:\My Work\Q4-Hackathon-2\phase-3-todo-chatbot\backend-api\src\agents\__init__.py
- D:\My Work\Q4-Hackathon-2\phase-3-todo-chatbot\backend-api\.env.example
- D:\My Work\Q4-Hackathon-2\phase-3-todo-chatbot\test_agents_integration.py

## TESTS_ADDED

- Created test_agents_integration.py to verify all components can be imported and configured properly
- Added import tests for all new modules
- Added configuration tests for LiteLLM and agent configurations
- Added agent creation tests to verify factory functions work correctly

## OUTCOME

The implementation follows best practices for OpenAI Agents SDK integration with OpenRouter, includes proper separation of concerns, and provides flexible configuration options for different use cases. The MCP tool adapters properly bridge the gap between the existing MCP infrastructure and the OpenAI Agents SDK, allowing AI agents to interact with the todo management system seamlessly. All tasks have been completed successfully and the system is ready for the next phase of implementation.

## EVALUATION

The integration successfully enables AI agents to interact with the Todo AI Chatbot's MCP tools through OpenRouter models. The modular design allows for easy extension and maintenance, while the configuration system provides flexibility for different use cases and model preferences.