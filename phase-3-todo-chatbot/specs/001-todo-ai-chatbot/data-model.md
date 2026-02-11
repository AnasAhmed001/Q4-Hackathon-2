# Data Model: Todo AI Chatbot

## Overview
Data model extensions for the Todo AI Chatbot feature, building upon the existing Phase II database schema.

## Extended Database Schema

### Existing Tables (from Phase II)
- **user**: id, email, hashed_password, created_at, updated_at
- **task**: id, user_id (FK → user.id), title, description, completed, created_at, updated_at
- **account**: id, user_id (FK → user.id), provider, provider_account_id, created_at, updated_at
- **session**: id, user_id (FK → user.id), expires_at, created_at
- **jwks**: id, user_id (FK → user.id), kid, kty, use, n, e, alg, created_at
- **verification**: id, user_id (FK → user.id), target, value, type, expires_at, created_at

### New Tables (Phase III additions)

#### conversation
- **id**: Primary key, UUID or auto-incrementing integer
- **user_id**: Foreign key referencing user.id, enforces user ownership
- **created_at**: Timestamp when conversation was initiated
- **updated_at**: Timestamp of last activity in conversation
- **title**: Optional title for the conversation (derived from first message or user input)

#### message
- **id**: Primary key, UUID or auto-incrementing integer
- **conversation_id**: Foreign key referencing conversation.id
- **user_id**: Foreign key referencing user.id, ensures user isolation
- **role**: Enum/string with values "user" or "assistant"
- **content**: Text content of the message
- **created_at**: Timestamp when message was created
- **tool_calls**: Optional JSON field storing tool calls made during this message
- **tool_responses**: Optional JSON field storing responses from tools

## Relationships
- conversation.user_id → user.id (one user to many conversations)
- message.conversation_id → conversation.id (one conversation to many messages)
- message.user_id → user.id (enforces user isolation)

## Validation Rules
- All foreign key constraints must be enforced at database level
- conversation.user_id and message.user_id must match authenticated user
- message.role must be either "user" or "assistant"
- conversation and message timestamps are automatically managed
- Messages are soft-deleted when tasks are deleted (preserve conversation context)

## State Transitions
- conversation.updated_at is updated when new messages are added
- No direct state transitions for messages (they are immutable once created)
- Conversations are implicitly archived after period of inactivity (implementation detail)

## Indexes
- conversation.user_id (for user-specific queries)
- conversation.created_at (for chronological ordering)
- message.conversation_id (for conversation history retrieval)
- message.created_at (for chronological ordering within conversation)
- composite index on (message.conversation_id, message.created_at) for efficient history queries