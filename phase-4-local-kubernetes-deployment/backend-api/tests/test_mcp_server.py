"""
Test script to verify the MCP server can be imported without errors
"""

import asyncio
import sys
import os

# Add the current directory to the path so we can import the mcp_server
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from mcp_server import server, list_available_tools
    print("✓ Successfully imported MCP server and tools")

    # Test getting the tools list
    async def test_get_tools():
        tools = await list_available_tools()
        print(f"✓ Found {len(tools)} tools:")
        for tool in tools:
            print(f"  - {tool.name}: {tool.description}")
        return tools

    tools = asyncio.run(test_get_tools())

    print("\n✓ MCP Server is ready!")
    print("\nTo run the server, use:")
    print("  python mcp_server.py")
    print("\nThe server provides these tools:")
    for tool in tools:
        print(f"  • {tool.name}: {tool.description}")

except ImportError as e:
    print(f"✗ Import error: {e}")
    print("Make sure you have installed the required packages:")
    print("  pip install -r requirements-mcp.txt")

except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()