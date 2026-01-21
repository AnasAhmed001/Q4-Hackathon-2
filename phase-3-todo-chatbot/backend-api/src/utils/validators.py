from typing import Optional
import re


def validate_email(email: str) -> bool:
    """Validate email format using regex."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_password_strength(password: str) -> tuple[bool, Optional[str]]:
    """Validate password strength requirements."""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r"\d", password):
        return False, "Password must contain at least one digit"
    
    return True, None


def validate_task_title(title: str) -> tuple[bool, Optional[str]]:
    """Validate task title requirements."""
    if not title or len(title.strip()) == 0:
        return False, "Task title is required"
    
    if len(title) > 200:
        return False, "Task title must be less than 200 characters"
    
    return True, None


def validate_task_description(description: Optional[str]) -> tuple[bool, Optional[str]]:
    """Validate task description requirements."""
    if description and len(description) > 1000:
        return False, "Task description must be less than 1000 characters"
    
    return True, None
