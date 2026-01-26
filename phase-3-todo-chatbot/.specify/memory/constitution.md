<!--
Version: 1.0.0 → 2.0.0 (MAJOR: New core principles for Phase III - MCP-first, stateless architecture; added Technology Stack, MCP Tools, Database Models, API specs)
Modified Principles: Correctness→Stateless Architecture; Reliability→MCP-First; User Isolation→User-Scoped; Security-First→Production-Ready; Added Core Principles matching Phase III
Added Sections: Technology Stack, MCP Tools Requirements, Database Models (Fixed), API Endpoint, Code Quality Standards, Natural Language Understanding, Stateless Architecture Rules (CRITICAL), Development Workflow, Success Criteria
Removed Sections: Key Standards (consolidated into Code Quality), Constraints (merged into principles)
Templates Requiring Updates:
  ✅ .specify/templates/plan-template.md - Constitution Check aligns with new MCP/stateless principles
  ✅ .specify/templates/spec-template.md - Requirements align with MCP tools and models
  ✅ .specify/templates/tasks-template.md - Task organization supports MCP tool implementation and testing
Follow-up TODOs: None - All placeholders resolved
-->
# Todo AI Chatbot - Phase III Constitution
## Stateless, Database-Backed, MCP-Powered Conversational Interface

## Core Principles

### I. Stateless Architecture
NO server-side state; all state persisted to Neon PostgreSQL. Server restarts must not lose conversation state. Any backend instance can handle any request. All conversation history fetched from database. No class-level or global state variables. Database is single source of truth.

**Rationale**: Ensures horizontal scalability and reliability for production conversational AI.

### II. MCP-First
All AI-to-backend interactions through Official MCP SDK tools. 5 stateless tools: add_task, list_tasks, complete_task, delete_task, update_task. All tools accept user_id as required parameter, interact with database (no in-memory state), return formats optimized for AI agent consumption, LLM-friendly schemas with clear descriptions and examples.

**Rationale**: Standardizes AI agent integration, leverages MCP protocol for tool calling.

### III. User-Scoped
Every operation requires user_id for authorization. User isolation strictly enforced across all layers.

**Rationale**: Prevents data leakage in multi-user environment.

### IV. Production-Ready
Complete implementations with error handling, validation, tests. Comprehensive error handling with user-friendly messages. Database session per request (proper cleanup). Environment variables for all configuration. Logging for debugging and monitoring.

**Rationale**: Hackathon must deliver deployable, robust system.

## Technology Stack (Non-Negotiable)
- Frontend: OpenAI ChatKit
- Backend: Python FastAPI
- AI Framework: OpenAI Agents SDK
- MCP Server: Official MCP SDK (Python)
- ORM: SQLModel
- Database: Neon Serverless PostgreSQL
- Auth: Better Auth with JWT

## Database Models (Fixed)
- **Task**: user_id, id, title, description, completed, created_at, updated_at
- **Conversation**: user_id, id, created_at, updated_at
- **Message**: user_id, id, conversation_id, role, content, created_at

## API Endpoint
- **POST /api/{user_id}/chat**
  - Request: conversation_id (optional), message (required)
  - Response: conversation_id, response, tool_calls

## Code Quality Standards
- Complete implementations (no placeholders or TODOs)
- Python type hints throughout
- Async/await patterns for database operations
- Tools map to common user phrasings
- Agent confirms all actions with friendly responses
- Graceful error handling for unclear requests
- Multi-step tool composition when needed

## Development Workflow
- Always fetch latest SDK docs from Context 7 before implementation
- Validate against MCP protocol specifications
- Test natural language to tool call mappings
- Ensure horizontal scalability

## Success Criteria
- AI chatbot manages tasks through natural language
- Conversations persist across server restarts
- All 5 CRUD operations working via MCP tools
- Stateless server architecture verified
- Production-ready with tests and documentation

## Governance

### Constitution Authority
This constitution supersedes all other development practices. All code changes MUST comply.

### Amendment Procedure
1. Documented justification
2. Approval from project stakeholders
3. Migration plan if affecting existing code
4. Version increment per semantic versioning

### Compliance & Review
- All PRs verify compliance
- Reviews check principle violations
- MCP tool validation required

### Versioning
- **MAJOR**: Incompatible principle changes
- **MINOR**: New principles/sections
- **PATCH**: Clarifications

**Version**: 2.0.0 | **Ratified**: 2026-01-12 | **Last Amended**: 2026-01-26
