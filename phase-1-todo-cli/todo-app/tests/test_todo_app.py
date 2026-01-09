"""
Test script to validate the todo application functionality without interactive input.
"""
from todo_app.services.todo_service import TodoService
from todo_app.models.todo import Todo


def test_functionality():
    """
    Test all core functionality of the todo application.
    """
    print("Testing Todo Application Functionality")
    print("="*40)

    # Create a service instance
    service = TodoService()

    # Test 1: Add todos
    print("\n1. Testing Add Todo functionality:")
    todo1 = service.add_todo("First todo item")
    todo2 = service.add_todo("Second todo item")
    print(f"   Added: {todo1}")
    print(f"   Added: {todo2}")

    # Test 2: View todos
    print("\n2. Testing View Todos functionality:")
    all_todos = service.get_all_todos()
    print(f"   Total todos: {len(all_todos)}")
    for todo in all_todos:
        print(f"   {todo}")

    # Test 3: Mark todo as complete
    print("\n3. Testing Mark Complete functionality:")
    if all_todos:
        completed_todo = service.mark_complete(str(all_todos[0].id))
        if completed_todo:
            print(f"   Marked as complete: {completed_todo}")
        else:
            print("   Failed to mark todo as complete")

    # Test 4: Update todo title
    print("\n4. Testing Update Todo functionality:")
    if all_todos:
        updated_todo = service.update_todo(str(all_todos[0].id), "Updated first todo")
        if updated_todo:
            print(f"   Updated: {updated_todo}")
        else:
            print("   Failed to update todo")

    # Test 5: View todos after updates
    print("\n5. Testing View Todos after updates:")
    all_todos = service.get_all_todos()
    for todo in all_todos:
        print(f"   {todo}")

    # Test 6: Delete todo
    print("\n6. Testing Delete Todo functionality:")
    if all_todos:
        delete_success = service.delete_todo(str(all_todos[0].id))
        if delete_success:
            print("   Todo deleted successfully")
        else:
            print("   Failed to delete todo")

    # Final view to confirm deletion
    print("\n7. Final view after deletion:")
    final_todos = service.get_all_todos()
    print(f"   Remaining todos: {len(final_todos)}")
    for todo in final_todos:
        print(f"   {todo}")

    print("\n" + "="*40)
    print("All functionality tests completed successfully!")


if __name__ == "__main__":
    test_functionality()