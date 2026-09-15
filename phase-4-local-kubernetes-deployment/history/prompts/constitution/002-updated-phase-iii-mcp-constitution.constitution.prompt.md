---
id: 002
title: Updated Phase III MCP Chatbot Constitution
stage: constitution
date: 2026-01-26
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: todo-ai-chatbot
user: unknown
command: /sp.constitution
labels: ["constitution", "mcp", "stateless", "phase-iii", "chatbot"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests:
  - none
---

## Prompt

Project: Todo AI Chatbot - Phase III (Natural Language Task Management)
Architecture: Stateless, Database-Backed, MCP-Powered Conversational Interface

Core Principles:
- Stateless architecture: NO server-side state, all state persisted to Neon PostgreSQL
- MCP-first: All AI-to-backend interactions through Official MCP SDK tools
- User-scoped: Every operation requires user_id for authorization
- Production-ready: Complete implementations with error handling, validation, and tests

Technology Stack (Non-Negotiable):
- Frontend: OpenAI ChatKit
- Backend: Python FastAPI
- AI Framework: OpenAI Agents SDK
- MCP Server: Official MCP SDK (Python)
- ORM: SQLModel
- Database: Neon Serverless PostgreSQL
- Auth: Better Auth with JWT

MCP Tools Requirements:
- 5 stateless tools: add_task, list_tasks, complete_task, delete_task, update_task
- All tools accept user_id as required parameter
- All tools interact with database (no in-memory state)
- Return formats optimized for AI agent consumption
- LLM-friendly schemas with clear descriptions and examples

Database Models (Fixed):
- Task: user_id, id, title, description, completed, created_at, updated_at
- Conversation: user_id, id, created_at, updated_at
- Message: user_id, id, conversation_id, role, content, created_at

API Endpoint:
- POST /api/{user_id}/chat
- Request: conversation_id (optional), message (required)
- Response: conversation_id, response, tool_calls

Code Quality Standards:
- Complete implementations (no placeholders or TODOs)
- Python type hints throughout
- Async/await patterns for database operations
- Comprehensive error handling with user-friendly messages
- Database session per request (proper cleanup)
- Environment variables for all configuration
- Logging for debugging and monitoring

Natural Language Understanding:
- Tools must map to common user phrasings
- Agent confirms all actions with friendly responses
- Graceful error handling for unclear requests
- Multi-step tool composition when needed

Stateless Architecture Rules (CRITICAL):
- Server restarts must not lose conversation state
- Any backend instance can handle any request
- All conversation history fetched from database
- No class-level or global state variables
- Database is single source of truth

Development Workflow:
- Always fetch latest SDK docs from Context 7 before implementation
- Validate against MCP protocol specifications
- Test natural language to tool call mappings
- Ensure horizontal scalability

Success Criteria:
- AI chatbot manages tasks through natural language
- Conversations persist across server restarts
- All 5 CRUD operations working via MCP tools
- Stateless server architecture verified
- Production-ready with tests and documentation

## Response snapshot

Constitution updated to v2.0.0 at .specify/memory/constitution.md. MAJOR bump for Phase III: MCP-first/stateless principles, tech stack, models, API spec. Sync Impact Report included; templates validated.

## Outcome
- ✅ Impact: Constitution now governs Phase III MCP-powered todo chatbot development.
- 🧪 Tests: none
- 📁 Files: .specify/memory/constitution.md
- 🔁 Next prompts: /sp.specify "Implement todo AI chatbot per constitution"
- 🧠 Reflection: User input fully integrated; MAJOR version justified by architecture shift.

## Evaluation notes (flywheel)
- Failure modes observed: none
- Graders run and results (PASS/FAIL): PASS
- Prompt variant (if applicable): none
- Next experiment (smallest change to try): none
