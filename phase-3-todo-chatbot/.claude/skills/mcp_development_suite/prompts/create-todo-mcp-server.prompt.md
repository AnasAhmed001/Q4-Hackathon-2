# Create Todo MCP Server Prompt

You are the MCP Development Suite skill. Generate complete code to integrate MCP todo tools into the existing FastAPI backend-api.

REQUIREMENTS:
- Reuse existing: src/models/task.py, src/crud/task.py, src/database.py, src/schemas/task.py
- Mount MCP at /mcp in src/main.py
- Tools: add_task, list_tasks, update_task, complete_task (status='completed'), delete_task
- All tools: async, user_id scoped, DB session per call (get_async_session)
- Pydantic params with descriptions/examples
- Return TaskResponse or List[TaskResponse]
- Error: raise ValueError with friendly msg
- Lifespan: share engine if needed

GENERATE:
1. src/mcp.py: FastMCP server with tools
2. Update src/main.py: mount + lifespan
3. tests/test_mcp_tools.py: pytest for tools

VALIDATE: Tool schemas match MCP spec, async DB works.
