---
id: 002
title: Todo AI Chatbot Implementation Planning
stage: plan
date_iso: 2026-02-01
surface: agent
model: claude-sonnet-4-5-20250929
feature: todo-ai-chatbot
branch: 001-todo-ai-chatbot
user: claude
command: /sp.plan "Todo AI Chatbot – Phase III (Implementation Plan)..."
labels: ["planning", "todo-chatbot", "architecture", "database", "mcp"]
links:
  spec: "specs/001-todo-ai-chatbot/spec.md"
  ticket: null
  adr: null
  pr: null
files_yaml: |
  - specs/001-todo-ai-chatbot/plan.md
  - specs/001-todo-ai-chatbot/research.md
  - specs/001-todo-ai-chatbot/data-model.md
  - specs/001-todo-ai-chatbot/contracts/api-spec.openapi.yaml
  - specs/001-todo-ai-chatbot/quickstart.md
tests_yaml: |
  - "Manual validation of plan completeness"
prompt_text: |
  Todo AI Chatbot – Phase III (Implementation Plan)

  Overview:
  Implement a natural language chatbot interface on top of the existing Phase II Todo application. The chatbot will allow authenticated users to manage tasks conversationally while reusing the existing authentication, authorization, and task database structure.

  Existing Infrastructure:
  - Neon PostgreSQL database
  - Existing tables:
    - user
    - task
    - account
    - session
    - jwks
    - verification
  - Authentication handled via existing Better Auth setup
  - Task ownership enforced via task.user_id

  No existing tables will be modified.

  Database Changes (Additive Only):
  1. Create `conversation` table
     - id (primary key)
     - user_id (foreign key → user.id)
     - created_at
     - updated_at

  2. Create `message` table
     - id (primary key)
     - conversation_id (foreign key → conversation.id)
     - user_id (foreign key → user.id)
     - role (user | assistant)
     - content (text)
     - created_at

  Purpose:
  - Persist chat history
  - Enable stateless backend chat handling
  - Allow conversation recovery after refresh or restart

  Backend Architecture:
  - Introduce a dedicated Chat API endpoint
  - Every request is authenticated using existing session/JWT logic
  - user_id is derived exclusively from auth context (never from client input)
  - conversation_id is optional:
    - If provided, reuse the conversation
    - If missing, create a new conversation automatically

  Chat Flow:
  1. Client sends a natural language message
  2. Backend resolves user identity via auth
  3. Conversation is loaded or created
  4. User message is stored in `message` table
  5. AI agent processes intent using conversation context
  6. Agent selects appropriate MCP tool
  7. MCP tool executes task operation
  8. AI generates a friendly confirmation or response
  9. Assistant message is persisted in `message` table
  10. Response is returned to client

  MCP Tool Layer:
  - All task operations must go through MCP tools
  - MCP tools are stateless
  - MCP tools directly interact with the existing `task` table
  - MCP tools must enforce:
    - user ownership
    - task existence checks
    - safe error responses
  - The AI agent never accesses the database directly

  Required MCP Tools:
  - create_task
  - list_tasks
  - update_task
  - complete_task
  - delete_task

  Each tool:
  - Accepts structured input
  - Returns structured output suitable for AI consumption
  - Operates only on tasks belonging to the authenticated user

  AI Agent Responsibilities:
  - Interpret natural language intent
  - Map intent to correct MCP tool
  - Handle missing or ambiguous information gracefully
  - Chain actions when required (e.g. list before delete)
  - Never hallucinate task data
  - Always confirm successful operations clearly

  Conversation Handling Rules:
  - Server remains stateless between requests
  - All chat state is restored from the database
  - Conversation history is passed to the agent as context
  - Only messages belonging to the authenticated user are accessible

  Frontend Integration:
  - Add a chat UI inside the existing frontend
  - Chat UI acts as an alternative interface to task management
  - UI supports:
    - sending messages
    - receiving assistant responses
    - displaying conversation history
  - Existing task UI remains unchanged and functional

  Security & Authorization:
  - All requests require authentication
  - Chatbot cannot access tasks across users
  - Authorization rules remain identical to Phase II
  - MCP tools enforce final ownership checks

  Error Handling:
  - Graceful handling of:
    - unclear user input
    - non-existent tasks
    - invalid operations
  - AI responds politely with clarification prompts
  - System errors are not exposed to the user

  Testing Strategy:
  - Verify all Phase II task features work via chat
  - Verify conversation persistence across reloads
  - Verify strict task isolation per user
  - Verify chatbot does not bypass auth or MCP tools

  Completion Criteria:
  - Users can fully manage tasks using natural language
  - Chatbot uses existing task system without duplication
  - Conversations persist reliably
  - System is secure, predictable, and demo-ready
  - Phase III integrates cleanly with Phase II architecture
response_text: |
  Completed implementation planning for the Todo AI Chatbot feature. Created the following artifacts:
  - Implementation plan (plan.md): Outlined the technical architecture and project structure
  - Research document (research.md): Captured key decisions and alternatives considered
  - Data model (data-model.md): Defined the extended database schema with conversation and message tables
  - API contracts (contracts/api-spec.openapi.yaml): Specified the chat API endpoints
  - Quickstart guide (quickstart.md): Provided setup instructions for developers

  The plan follows the constitution principles of stateless architecture, MCP-first approach, user-scoped operations, and production-ready implementation. All required database changes, API endpoints, and system components are defined.
outcome: |
  Successfully completed Phase 0 and Phase 1 of the planning process. All required documentation has been created according to the template structure. The implementation plan is aligned with the project constitution and ready for the task generation phase (/sp.tasks).
evaluation: |
  The planning phase successfully produced all required artifacts with appropriate detail and technical accuracy. The implementation approach is consistent with the constitution and addresses all requirements from the original feature specification. The plan provides clear direction for the development team.
---
