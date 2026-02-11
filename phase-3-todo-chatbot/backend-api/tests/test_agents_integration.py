"""
Test script to verify that the Cohere V2 + MCP integration components are working correctly.
"""

import sys
import os

# Add the backend-api/src to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend-api', 'src'))


def test_imports():
    """Test that all modules can be imported without errors."""
    print("Testing imports...")

    try:
        from src.agents.mcp_adapters import COHERE_TOOLS, TOOL_FUNCTIONS
        print(f"✓ Successfully imported MCP adapters ({len(COHERE_TOOLS)} tools, {len(TOOL_FUNCTIONS)} executors)")

        from src.agents.agent_config import (
            AgentPersonality,
            COHERE_MODEL,
            get_system_instruction,
            get_cohere_client,
        )
        print(f"✓ Successfully imported agent config (model={COHERE_MODEL})")

        print("All imports successful!")
        return True

    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error during import: {e}")
        return False


def test_configurations():
    """Test that configurations can be created without errors."""
    print("\nTesting configurations...")

    try:
        from src.agents.agent_config import get_system_instruction, AgentPersonality

        instruction = get_system_instruction(AgentPersonality.HELPFUL_ASSISTANT, user_id="test-user")
        assert "test-user" in instruction
        print("✓ System instruction contains user_id")

        from src.agents.mcp_adapters import COHERE_TOOLS
        tool_names = [t["function"]["name"] for t in COHERE_TOOLS]
        expected = {"add_task", "list_tasks", "update_task", "complete_task", "delete_task"}
        assert set(tool_names) == expected
        print(f"✓ All {len(expected)} tool schemas present")

        print("All configuration tests passed!")
        return True

    except Exception as e:
        print(f"✗ Configuration test error: {e}")
        return False


def main():
    """Run all tests."""
    print("Running Cohere + MCP Integration Tests...\n")

    all_passed = True
    all_passed &= test_imports()
    all_passed &= test_configurations()

    if all_passed:
        print("\n🎉 All tests passed! Cohere + MCP integration is ready.")
    else:
        print("\n❌ Some tests failed. Please check the errors above.")

    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)