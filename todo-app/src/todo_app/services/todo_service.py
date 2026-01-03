"""
Todo service containing the core business logic for the todo application.
"""
from typing import List, Optional
from todo_app.models.todo import Todo
from todo_app.services.todo_store import TodoStore
from todo_app.lib.validators import validate_todo_title, validate_todo_id, sanitize_input


class TodoService:
    """
    Service layer containing business logic for todo operations.
    """
    def __init__(self):
        self.store = TodoStore()

    def add_todo(self, title: str) -> Optional[Todo]:
        """
        Add a new todo with the given title.
        Returns the created Todo or None if validation fails.
        """
        title = sanitize_input(title)
        is_valid, error_msg = validate_todo_title(title)

        if not is_valid:
            print(f"Error: {error_msg}")
            return None

        return self.store.add_todo(title)

    def get_all_todos(self) -> List[Todo]:
        """
        Get all todos.
        """
        return self.store.get_all_todos()

    def mark_complete(self, todo_id_str: str) -> Optional[Todo]:
        """
        Mark a todo as complete by its ID string.
        Returns the updated Todo or None if validation fails or todo doesn't exist.
        """
        is_valid, todo_id, error_msg = validate_todo_id(todo_id_str)

        if not is_valid:
            print(f"Error: {error_msg}")
            return None

        todo = self.store.get_todo(todo_id)
        if not todo:
            print(f"Error: Todo with ID {todo_id} does not exist.")
            return None

        return self.store.update_todo(todo_id, completed=True)

    def update_todo(self, todo_id_str: str, new_title: str) -> Optional[Todo]:
        """
        Update a todo's title by its ID string.
        Returns the updated Todo or None if validation fails or todo doesn't exist.
        """
        # Validate the ID
        is_valid_id, todo_id, error_msg_id = validate_todo_id(todo_id_str)

        if not is_valid_id:
            print(f"Error: {error_msg_id}")
            return None

        # Validate the new title
        new_title = sanitize_input(new_title)
        is_valid_title, error_msg_title = validate_todo_title(new_title)

        if not is_valid_title:
            print(f"Error: {error_msg_title}")
            return None

        # Check if todo exists
        todo = self.store.get_todo(todo_id)
        if not todo:
            print(f"Error: Todo with ID {todo_id} does not exist.")
            return None

        # Update the todo
        return self.store.update_todo(todo_id, title=new_title)

    def delete_todo(self, todo_id_str: str) -> bool:
        """
        Delete a todo by its ID string.
        Returns True if successful, False if validation fails or todo doesn't exist.
        """
        is_valid, todo_id, error_msg = validate_todo_id(todo_id_str)

        if not is_valid:
            print(f"Error: {error_msg}")
            return False

        todo = self.store.get_todo(todo_id)
        if not todo:
            print(f"Error: Todo with ID {todo_id} does not exist.")
            return False

        return self.store.delete_todo(todo_id)