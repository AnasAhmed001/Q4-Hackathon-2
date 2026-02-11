# Actionable Tasks: Todo AI Chatbot – Phase III (Natural Language Task Management)

**Feature**: Todo AI Chatbot – Phase III (Natural Language Task Management)
**Branch**: `001-todo-ai-chatbot`
**Generated**: 2026-02-01
**Input**: spec.md, plan.md, data-model.md, contracts/api-spec.openapi.yaml

## Implementation Strategy

Implement the Todo AI Chatbot feature in incremental phases, starting with foundational components and progressing through user stories in priority order. Each phase builds upon the previous to deliver a complete, independently testable increment. Begin with database schema and MCP tools, then implement backend API, followed by frontend integration.

## Phase 1: Setup & Project Initialization

- [X] T001 Set up project structure per implementation plan in backend-api/src/mcp/
- [X] T002 Install required dependencies for MCP SDK, OpenAI Agents SDK in requirements.txt
- [X] T003 Configure environment variables for OpenAI API, database connection in .env.example
- [X] T004 [P] Update pyproject.toml with new dependencies for MCP and OpenAI integration

## Phase 2: Foundational Components

- [X] T005 Create database models for conversation in backend-api/src/models/conversation.py
- [X] T006 Create database models for message in backend-api/src/models/message.py
- [X] T007 Create schema definitions for conversation in backend-api/src/schemas/conversation.py
- [X] T008 Create schema definitions for message in backend-api/src/schemas/message.py
- [X] T009 Create CRUD operations for conversation in backend-api/src/crud/conversation.py
- [X] T010 Create CRUD operations for message in backend-api/src/crud/message.py
- [X] T011 Add database migration for conversation and message tables in backend-api/alembic/

## Phase 3: User Story 1 - Natural Language Task Management (Priority: P1)

**Goal**: Enable users to manage tasks using natural language commands in a chat interface.

**Independent Test**: Can be fully tested by interacting with the chatbot using natural language commands like "Add a task to buy groceries" and verifying that a task is created in the system.

- [X] T012 [P] [US1] Create MCP server in backend-api/src/mcp/server.py
- [X] T013 [P] [US1] Create create_task MCP tool in backend-api/src/mcp/tools/create_task.py
- [X] T014 [P] [US1] Create list_tasks MCP tool in backend-api/src/mcp/tools/list_tasks.py
- [X] T015 [P] [US1] Create update_task MCP tool in backend-api/src/mcp/tools/update_task.py
- [X] T016 [P] [US1] Create complete_task MCP tool in backend-api/src/mcp/tools/complete_task.py
- [X] T017 [P] [US1] Create delete_task MCP tool in backend-api/src/mcp/tools/delete_task.py
- [X] T018 [US1] Implement chat API endpoint in backend-api/src/api/chat.py
- [X] T019 [US1] Create chat service for handling conversation logic in backend-api/src/services/chat_service.py
- [X] T020 [US1] Implement frontend chat page in frontend/app/(protected)/chat/page.tsx
- [X] T021 [US1] Create ChatInterface component in frontend/components/chat/ChatInterface.tsx
- [X] T022 [US1] Create Message component in frontend/components/chat/Message.tsx
- [X] T023 [US1] Create MessageInput component in frontend/components/chat/MessageInput.tsx
- [X] T024 [US1] Update API client with chat endpoint in frontend/lib/api-client.ts
- [ ] T025 [US1] Test basic task creation via chat interface with acceptance scenario 1

## Phase 4: User Story 2 - Conversational Task Operations (Priority: P1)

**Goal**: Enable users to perform all standard task operations (create, update, complete, delete) through conversational commands.

**Independent Test**: Can be tested by performing each task operation through natural language commands and verifying the corresponding database changes.

- [X] T026 [US2] Enhance chat service to handle update operations in backend-api/src/services/chat_service.py
- [X] T027 [US2] Enhance chat service to handle complete operations in backend-api/src/services/chat_service.py
- [X] T028 [US2] Enhance chat service to handle delete operations in backend-api/src/services/chat_service.py
- [ ] T029 [US2] Test task completion via chat interface with acceptance scenario 1
- [ ] T030 [US2] Test task update via chat interface with acceptance scenario 2
- [ ] T031 [US2] Test task deletion via chat interface with acceptance scenario 3

## Phase 5: User Story 3 - Persistent Conversation Context (Priority: P2)

**Goal**: Maintain conversation history across browser refreshes and server restarts.

**Independent Test**: Can be tested by starting a conversation, refreshing the page, and continuing the conversation using references to previous exchanges.

- [X] T032 [US3] Enhance chat API to persist conversation history in backend-api/src/api/chat.py
- [X] T033 [US3] Implement conversation loading/resumption logic in backend-api/src/services/chat_service.py
- [X] T034 [US3] Update frontend to load existing conversation history in frontend/app/(protected)/chat/page.tsx
- [X] T035 [US3] Implement conversation persistence mechanism in database
- [ ] T036 [US3] Test conversation persistence across page refreshes with acceptance scenario 1

## Phase 6: User Story 4 - User Isolation and Security (Priority: P1)

**Goal**: Ensure chatbot only shows and modifies the authenticated user's tasks.

**Independent Test**: Can be tested by logging in as different users and verifying that they only see their own tasks.

- [X] T037 [US4] Implement user authentication checks in chat API in backend-api/src/api/chat.py
- [ ] T038 [US4] Enhance MCP tools to enforce user ownership checks in backend-api/src/mcp/tools/
- [ ] T039 [US4] Add authorization middleware for conversation access in backend-api/src/api/chat.py
- [ ] T040 [US4] Test user isolation with acceptance scenario 1
- [ ] T041 [US4] Test user isolation with acceptance scenario 2

## Phase 7: Polish & Cross-Cutting Concerns

- [X] T042 Add comprehensive error handling for unclear requests in backend-api/src/services/chat_service.py
- [ ] T043 Implement graceful handling of missing tasks in MCP tools
- [X] T044 Add structured logging for chat interactions in backend-api/src/services/chat_service.py
- [X] T045 Create integration tests for chat functionality in backend-api/tests/mcp/test_mcp_tools.py
- [X] T046 Add unit tests for MCP tools in backend-api/tests/mcp/test_mcp_tools.py
- [X] T047 Update quickstart guide with chat feature instructions in specs/001-todo-ai-chatbot/quickstart.md
- [X] T048 Document API endpoints in OpenAPI spec in specs/001-todo-ai-chatbot/contracts/api-spec.openapi.yaml
- [ ] T049 Perform end-to-end testing of all user stories
- [ ] T050 Deploy and verify production readiness

## Phase 8: AI Agent Integration with OpenAI Agents SDK and OpenRouter (Priority: P1)

**Goal**: Create an AI agent using the OpenAI Agents SDK Python library with OpenRouter that connects to MCP tools for advanced natural language task management capabilities. The agent will provide enhanced understanding and more sophisticated task management operations.

**Independent Test**: Can be tested by interacting with the AI agent through natural language commands and verifying that the agent correctly interprets requests and uses MCP tools to perform appropriate task operations.

- [ ] T051 [P] Set up OpenAI Agents SDK dependencies for OpenRouter integration in requirements.txt
- [ ] T052 [P] Configure LiteLLM to work with OpenRouter models in backend-api/src/config/litellm_config.py
- [ ] T053 Create MCP tool adapter functions for OpenAI Agents SDK in backend-api/src/agents/mcp_adapters.py
- [ ] T054 Create AI agent configuration for OpenRouter in backend-api/src/agents/agent_config.py
- [ ] T055 Implement AI agent service using OpenAI Agents SDK in backend-api/src/agents/ai_agent_service.py
- [ ] T056 Integrate AI agent with existing chat service in backend-api/src/services/chat_service.py
- [ ] T057 Update chat API endpoint to optionally use AI agent in backend-api/src/api/chat.py
- [ ] T058 Create AI agent management endpoints in backend-api/src/api/agents.py
- [ ] T059 Add AI agent session management in backend-api/src/services/agent_session_service.py
- [ ] T060 Test AI agent task creation through MCP tools with acceptance scenario 1
- [ ] T061 Test AI agent task management capabilities with complex natural language requests
- [ ] T062 Perform comparative testing between rule-based and AI-powered chat services

## Phase 9: Frontend AI Agent Integration (Priority: P1)

**Goal**: Connect the AI agent to the frontend chatbot interface to enable users to interact with the AI-powered task management system through the web interface.

**Independent Test**: Can be tested by using the web chat interface to interact with the AI agent and verifying that natural language requests are processed correctly and responses are displayed properly.

- [ ] T063 Update frontend API client to support AI agent endpoints in frontend/lib/api-client.ts
- [ ] T064 Add AI agent configuration options in frontend chat interface
- [ ] T065 Create AI agent status indicators in frontend/components/chat/ChatInterface.tsx
- [ ] T066 Update message handling to distinguish between rule-based and AI agent responses
- [ ] T067 Add AI agent loading states and progress indicators in frontend/components/chat/Message.tsx
- [ ] T068 Create AI agent error handling in frontend components
- [ ] T069 Implement AI agent-specific UI elements for enhanced interaction
- [ ] T070 Test AI agent integration through frontend chat interface with acceptance scenario 1
- [ ] T071 Perform end-to-end testing of AI agent functionality from frontend to backend

## Dependencies

- User Story 1 (Natural Language Task Management) must be completed before User Story 2 (Conversational Task Operations)
- Foundational components (Phase 2) must be completed before any user story phases
- User Story 4 (User Isolation) can be developed in parallel but must be validated with other user stories

## Parallel Execution Examples

- MCP tools can be developed in parallel (T013-T017) as they are independent
- Frontend components can be developed in parallel (T020-T022) once backend API is stable
- Database models and schemas can be developed in parallel (T005-T008)