# Implementation Plan: Todo AI Chatbot – Phase III (Natural Language Task Management)

**Branch**: `001-todo-ai-chatbot` | **Date**: 2026-02-01 | **Spec**: [link](./spec.md)
**Input**: Feature specification from `/specs/[###-feature-name]/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Implementation of a natural language chatbot interface that allows authenticated users to manage tasks conversationally while reusing the existing authentication, authorization, and task database structure. The system will use MCP tools for all task operations and maintain statelessness with conversation history persisted in the database.

## Technical Context

**Language/Version**: Python 3.11, TypeScript/JavaScript for frontend
**Primary Dependencies**: FastAPI, OpenAI Agents SDK, Official MCP SDK, SQLModel, Neon PostgreSQL, Better Auth
**Storage**: Neon PostgreSQL with new conversation and message tables
**Testing**: pytest with integration and unit tests
**Target Platform**: Linux server (containerized), Web browser (Next.js frontend)
**Project Type**: web (existing backend with new chat API and frontend UI)
**Performance Goals**: <200ms p95 latency for chat responses, 1000+ concurrent users supported
**Constraints**: <200ms p95 response time, proper database connection pooling, secure auth enforcement
**Scale/Scope**: Multi-user environment with strict user isolation, persistent conversation history

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Stateless Architecture**: All conversation state persisted to Neon PostgreSQL, no server-side state maintained
- **MCP-First**: All task operations will go through 5 stateless MCP tools: create_task, list_tasks, update_task, complete_task, delete_task
- **User-Scoped**: Every operation requires user_id from auth context, strict user isolation enforced
- **Production-Ready**: Complete error handling, validation, structured logging, environment variables for config
- **Testing Discipline**: Unit and integration tests for all MCP tools and chat API endpoint

## Project Structure

### Documentation (this feature)

```text
specs/001-todo-ai-chatbot/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
backend-api/
├── src/
│   ├── __init__.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── task.py          # Existing task model
│   │   ├── user.py          # Existing user model
│   │   ├── conversation.py  # New conversation model
│   │   └── message.py       # New message model
│   ├── api/
│   │   ├── __init__.py
│   │   ├── auth.py          # Existing auth endpoints
│   │   ├── deps.py          # Existing auth dependencies
│   │   ├── tasks.py         # Existing task endpoints
│   │   └── chat.py          # New chat endpoint
│   ├── auth/
│   │   ├── __init__.py
│   │   └── jwt_validator.py # Existing JWT validation
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py      # Configuration settings
│   ├── crud/
│   │   ├── __init__.py
│   │   ├── task.py          # Existing task CRUD operations
│   │   ├── user.py          # Existing user CRUD operations
│   │   ├── conversation.py  # New conversation CRUD operations
│   │   └── message.py       # New message CRUD operations
│   ├── database.py          # Database connection
│   ├── main.py              # Application entry point
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── task.py          # Task schema definitions
│   │   ├── user.py          # User schema definitions
│   │   ├── conversation.py  # New conversation schema definitions
│   │   └── message.py       # New message schema definitions
│   ├── services/            # New services directory
│   │   ├── __init__.py
│   │   └── chat_service.py  # New chat service
│   ├── mcp/                 # New MCP tools directory
│   │   ├── __init__.py
│   │   ├── server.py        # New MCP server
│   │   └── tools/           # MCP tools directory
│   │       ├── __init__.py
│   │       ├── create_task.py
│   │       ├── list_tasks.py
│   │       ├── update_task.py
│   │       ├── complete_task.py
│   │       └── delete_task.py
│   └── utils/
│       ├── __init__.py
│       └── validators.py    # Utility validators
├── alembic/                 # Database migrations
│   └── ...
├── alembic.ini
├── requirements.txt
├── pyproject.toml
├── Dockerfile
├── .dockerignore
├── .gitignore
└── tests/
    ├── __init__.py
    ├── test_imports.py
    └── mcp/
        └── test_mcp_tools.py

frontend/
├── app/
│   ├── (protected)/
│   │   ├── layout.tsx
│   │   ├── tasks/
│   │   │   └── ...
│   │   └── chat/            # New chat page
│   │       └── page.tsx
│   └── ...
├── components/
│   └── chat/                # New chat components
│       ├── ChatInterface.tsx
│       ├── Message.tsx
│       └── MessageInput.tsx
└── lib/
    └── api-client.ts        # Updated with chat API calls
```

**Structure Decision**: Selected web application structure with new chat API endpoints in backend and chat UI in frontend, maintaining separation of concerns while integrating with existing authentication and task management systems.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| New database tables | Required for conversation persistence | Would lose conversation state on server restart |
| MCP tool layer | Required by constitution for AI integration | Direct DB access violates MCP-first principle |
| New API endpoint | Required for chat functionality | Existing task endpoints don't handle conversational context |