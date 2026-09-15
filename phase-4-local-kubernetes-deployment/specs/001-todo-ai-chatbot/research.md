# Research: Todo AI Chatbot Implementation

## Overview
Research document covering key decisions and findings for implementing the Todo AI Chatbot feature.

## Decision: MCP Tools Architecture
**Rationale**: Following the constitution's MCP-First principle, all task operations must go through MCP tools to enable proper AI agent integration. This ensures standardized tool calling and maintains the stateless architecture.

**Alternatives considered**:
- Direct database access from AI agent: Violates constitution and creates tight coupling
- REST API calls from AI agent: Would require authentication handling within the agent
- GraphQL queries from AI agent: Same authentication concerns as REST

## Decision: Database Schema Extensions
**Rationale**: To maintain conversation history and enable stateless backend, new tables are needed to persist conversation and message data.

**Alternatives considered**:
- Storing conversation in session storage: Would not survive server restarts
- In-memory caching: Would not survive server restarts and doesn't scale horizontally
- External storage service: Adds complexity and dependencies

## Decision: Frontend Integration Approach
**Rationale**: Embedding the chat interface within the existing frontend maintains consistency and leverages existing authentication infrastructure.

**Alternatives considered**:
- Standalone chat application: Would require duplicate auth system
- Separate micro-frontend: Adds deployment complexity
- Embedded iframe: Would complicate auth flow and styling

## Decision: AI Agent Selection
**Rationale**: OpenAI Agents SDK provides robust tool calling capabilities and is well-suited for the task-oriented nature of the todo application.

**Alternatives considered**:
- LangChain: More complex for simple task management use case
- Anthropic Claude: Would require different tool calling patterns
- Self-hosted models: Adds operational complexity for minimal benefit

## Decision: Authentication Integration
**Rationale**: Leveraging existing Better Auth infrastructure ensures consistency and maintains security standards established in Phase II.

**Alternatives considered**:
- Separate auth for chat endpoint: Creates inconsistency and maintenance burden
- Token-based auth: Would duplicate existing functionality
- Session-based auth: Already implemented in existing system

## Decision: Conversation Persistence Strategy
**Rationale**: Storing conversation history in database ensures availability across server restarts and enables horizontal scaling.

**Alternatives considered**:
- Client-side storage: Would not work across devices or browsers
- Redis cache: Adds infrastructure complexity for minimal gain
- File-based storage: Doesn't integrate well with existing database schema