# Todo MCP Server Example

Full production-ready MCP server for todo-chatbot.

## Setup
1. Copy `server.py` to `backend-api/src/mcp.py`
2. Update imports if needed
3. Add to `requirements.txt`: `mcp`
4. Update `src/main.py` using `main_integration.py`
5. Migrate DB if needed
6. Run: `uvicorn src.main:app --reload`
7. MCP at: `http://localhost:8000/mcp`

## Test with curl (or OpenAI agent)
```bash
# List tools (MCP discovery)
curl http://localhost:8000/mcp -H 'Content-Type: application/json' --data '{"jsonrpc": "2.0", "id": 1, "method": "list_tools"}'
```

## Agent Usage (OpenAI SDK)
Tools auto-discovered via MCP client. Optimized schemas/descriptions.

## Validation
- [x] MCP spec compliant (FastMCP + streamable-http)
- [x] User-scoped (user_id param)
- [x] Async DB (per-request sessions)
- [x] Pydantic validation + LLM examples
- [x] Error handling (ValueError -> agent-friendly)
- [x] Logging
- [x] Tests (pytest)
```
