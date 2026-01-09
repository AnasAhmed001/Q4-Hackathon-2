"""
Todo data model representing a task with ID, title, and completion status.
"""
from dataclasses import dataclass
from typing import Optional
from datetime import datetime
from todo_app.lib.colors import Colors


@dataclass
class Todo:
    """
    Represents a todo item with an ID, title, and completion status.
    """
    id: int
    title: str
    completed: bool = False
    created_at: Optional[datetime] = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

    def __str__(self) -> str:
        if self.completed:
            status = Colors.success("✓")
            title_color = Colors.DIM
        else:
            status = Colors.warning("○")
            title_color = Colors.WHITE
        
        created = self.created_at.strftime("%Y-%m-%d %H:%M") if self.created_at else "N/A"
        id_str = Colors.colorize(str(self.id), Colors.BRIGHT_CYAN, bold=True)
        created_str = Colors.dim_text(f"(created: {created})")
        
        return f"[{status}] {id_str}: {title_color}{self.title}{Colors.RESET} {created_str}"