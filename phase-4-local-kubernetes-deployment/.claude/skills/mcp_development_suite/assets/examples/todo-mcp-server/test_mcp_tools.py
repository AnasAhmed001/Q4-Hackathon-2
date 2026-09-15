```python
# pytest tests for MCP todo tools
# Run: pytest test_mcp_tools.py -v

import pytest
from unittest.mock import AsyncMock, patch
from src.mcp import add_task, list_tasks  # etc.

@pytest.mark.asyncio
async def test_add_task():
    with patch('src.crud.task.create_task_for_user', new_callable=AsyncMock) as mock_create:
        mock_create.return_value = Task(id='test-id', title='Test', status='pending')
        result = await add_task('user-id', 'Test task')
        assert result['id'] == 'test-id'
        assert result['title'] == 'Test task'

@pytest.mark.asyncio
async def test_list_tasks():
    # Similar mocks...
    pass

# Add tests for all tools, error cases
```
