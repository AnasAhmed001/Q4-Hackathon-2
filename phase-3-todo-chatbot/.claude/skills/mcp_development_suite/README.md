# MCP Development Suite Skill

## Overview
Expert skill for building production-ready Model Context Protocol (MCP) servers and tools using the official `mcp` Python SDK. Specializes in:
- FastAPI integration with existing backends (e.g., todo-chatbot's backend-api)
- Stateless, database-backed tools (Neon PostgreSQL + SQLModel)
- User-scoped CRUD tools (add/list/update/complete/delete todos)
- LLM-optimized tool schemas (Pydantic, detailed descriptions/examples)
- Async/await, proper sessions/transactions, logging, validation, security
- OpenAI Agents SDK compatibility (standard JSON schema tools)

Proactively fetches latest MCP SDK docs from Context7 before code generation.

## Usage in Todo Chatbot Project
1. Invoke: `/mcp_development_suite create-todo-mcp-server`
2. Generates MCP tools reusing existing `Task` model/CRUD from `backend-api/src/`
3. Mounts MCP endpoint at `/mcp` in existing FastAPI app
4. Tools: `add_task`, `list_tasks`, `update_task`, `complete_task`, `delete_task`
   - All require `user_id: str` for scoping
   - Return structured JSON for agent parsing

### Example Tool Schema (LLM-Optimized)
```python
@mcp.tool()
async def add_task(
    user_id: str = Field(..., description="User ID to scope the task"),
    title: str = Field(..., description="Task title"),
    description: Optional[str] = None,
    due_date: Optional[str] = None  # ISO datetime
) -> dict:
    \"\"\"Add a new todo task for the user. Returns created task details. Example: add_task(user_id='uuid', title='Buy groceries') -> {'id': 'new-uuid', 'status': 'pending'} \"\"\"
    # Implementation using existing CRUD
```

## Assets Structure
- **boilerplate/**: Generic skeletons
  - `mcp_server.py`: Standalone FastMCP server
  - `fastapi_mcp_integration.py`: Mount in existing FastAPI
  - `requirements.in`: Dependencies (`mcp`, `sqlmodel`, etc.)
- **examples/todo-mcp-server/**: Full todo MCP server example
  - Integrated with project DB/models
  - Tests: `test_mcp_tools.py`
  - `Dockerfile`, `docker-compose.yml` for Neon

## Workflows (prompts/)
Use these for guided generation:
- `create-todo-mcp-server.prompt.md`: Generate full todo MCP integration
- `add-custom-tool.prompt.md`: Add new tool (e.g., search_tasks)

## Integration Steps
1. `pip install mcp` (add to requirements.txt)
2. Copy boilerplate to `backend-api/src/mcp.py`
3. Import existing models/CRUD
4. Mount in `main.py`: `app.mount("/mcp", mcp.streamable_http_app())`
5. Add lifespan for DB engine
6. Run: `uvicorn src.main:app --reload`
7. Test: OpenAI agent calls `add_task(user_id=..., title=...)`

## Production Best Practices (Auto-Enforced)
- Stateless HTTP (`stateless_http=True`)
- Per-request DB sessions
- Pydantic validation + Field descriptions
- Structured returns (TaskResponse models)
- Logging + error handling (friendly agent messages)
- No hard-coded secrets (env vars)
- Tests for all tools

## MCP Tool Examples for Agents
```
Tools for Todo AI Chatbot:
1. list_tasks(user_id: str, limit: int=10, status: Optional[str]='pending') -> List[Task]
2. add_task(user_id: str, title: str, ...) -> Task
3. complete_task(user_id: str, task_id: str) -> Task
```
