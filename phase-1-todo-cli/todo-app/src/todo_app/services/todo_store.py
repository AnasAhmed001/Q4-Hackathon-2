"""
In-memory store for managing todos.
"""
from typing import Dict, List, Optional
from todo_app.models.todo import Todo


class TodoStore:
    """
    In-memory storage for todos with basic CRUD operations.
    """
    def __init__(self):
        self._todos: Dict[int, Todo] = {}
        self._next_id = 1

    def add_todo(self, title: str) -> Todo:
        """
        Add a new todo with the given title.
        Returns the created Todo with a unique ID.
        """
        todo = Todo(id=self._next_id, title=title, completed=False)
        self._todos[todo.id] = todo
        self._next_id += 1
        return todo

    def get_todo(self, todo_id: int) -> Optional[Todo]:
        """
        Get a todo by its ID.
        Returns None if the todo doesn't exist.
        """
        return self._todos.get(todo_id)

    def get_all_todos(self) -> List[Todo]:
        """
        Get all todos in the store.
        """
        return list(self._todos.values())

    def update_todo(self, todo_id: int, title: Optional[str] = None, completed: Optional[bool] = None) -> Optional[Todo]:
        """
        Update a todo's title or completion status.
        Returns the updated Todo or None if it doesn't exist.
        """
        if todo_id not in self._todos:
            return None

        todo = self._todos[todo_id]
        if title is not None:
            todo.title = title
        if completed is not None:
            todo.completed = completed

        return todo

    def delete_todo(self, todo_id: int) -> bool:
        """
        Delete a todo by its ID.
        Returns True if the todo was deleted, False if it didn't exist.
        """
        if todo_id in self._todos:
            del self._todos[todo_id]
            return True
        return False

    def clear_all(self):
        """
        Clear all todos from the store.
        """
        self._todos.clear()