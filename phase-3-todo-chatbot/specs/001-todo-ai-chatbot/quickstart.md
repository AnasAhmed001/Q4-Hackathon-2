# Quickstart Guide: Todo AI Chatbot

## Overview
This guide provides the essential information to get the Todo AI Chatbot up and running in your development environment.

## Prerequisites
- Python 3.11+
- Node.js 18+ (for frontend)
- PostgreSQL (or Neon PostgreSQL account)
- Docker (recommended for containerized deployment)
- OpenAI API key
- Existing Phase II Todo application setup

## Setup Steps

### 1. Clone and Navigate
```bash
git clone <repository-url>
cd <repository-directory>
git checkout 001-todo-ai-chatbot
```

### 2. Backend Setup
```bash
cd backend-api
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL="postgresql://username:password@localhost:5432/todo_db"
export OPENAI_API_KEY="your-openai-api-key"
export BETTER_AUTH_SECRET="your-auth-secret"
export MCP_SERVER_HOST="localhost"
export MCP_SERVER_PORT=3000

# Run database migrations
alembic upgrade head

# Start the MCP server
python -m src.mcp.server

# In a separate terminal, start the FastAPI app
uvicorn src.main:app --reload --port 8000
```

### 3. Frontend Setup
```bash
cd frontend
npm install

# Set environment variables in .env.local
NEXT_PUBLIC_API_BASE_URL="http://localhost:8000"
NEXT_PUBLIC_MCP_SERVER_URL="ws://localhost:3000"

# Start the development server
npm run dev
```

### 4. Verify Installation
- Visit `http://localhost:3000` to access the frontend
- Log in with your existing credentials
- Navigate to the chat interface at `/chat`
- Test basic commands like "Create a task called 'Test'"
- Verify that tasks appear in the traditional task list

## Chat Feature Instructions
- **Creating Tasks**: Use phrases like "Create a task to buy groceries" or "Add a task to finish the report"
- **Listing Tasks**: Say "Show me my tasks" or "What are my tasks?"
- **Updating Tasks**: Use "Update the grocery task to 'buy milk and bread'"
- **Completing Tasks**: Say "Complete the report task" or "Mark the shopping task as done"
- **Deleting Tasks**: Use "Delete the old task" or "Remove the meeting task"

## Key Endpoints
- `POST /api/{user_id}/chat` - Main chat endpoint for natural language processing
- `GET /api/{user_id}/conversations` - List user's conversations
- `GET /api/{user_id}/conversations/{conversation_id}` - Get conversation history

## Configuration Options
- `OPENAI_MODEL`: Change the AI model used (default: gpt-4)
- `DATABASE_POOL_SIZE`: Connection pool size for database (default: 20)
- `CHAT_HISTORY_LIMIT`: Number of messages to include in context (default: 10)

## Troubleshooting
- If the MCP server doesn't start, ensure all required dependencies are installed
- If authentication fails, verify that the Better Auth configuration matches Phase II
- If database migrations fail, ensure PostgreSQL is running and credentials are correct
- If the AI doesn't respond, check that the OpenAI API key is valid and has sufficient quota
- If conversation history doesn't persist, verify that the database tables were created properly

## Next Steps
1. Customize the chat interface to match your application's design
2. Fine-tune the MCP tools for your specific use case
3. Add additional conversation management features
4. Implement analytics to track usage and effectiveness