"""Basic tests to verify imports work correctly."""

def test_fastapi_app_import():
    """Test that the main FastAPI app can be imported."""
    try:
        from src.main import app
        assert app is not None
        assert hasattr(app, 'routes')
    except ImportError as e:
        raise AssertionError(f"Failed to import main app: {e}")


def test_models_import():
    """Test that models can be imported."""
    try:
        from src.models.user import User
        from src.models.task import Task
        assert User is not None
        assert Task is not None
    except ImportError as e:
        raise AssertionError(f"Failed to import models: {e}")


def test_schemas_import():
    """Test that schemas can be imported."""
    try:
        from src.schemas.user import UserCreate
        from src.schemas.task import TaskCreate
        assert UserCreate is not None
        assert TaskCreate is not None
    except ImportError as e:
        raise AssertionError(f"Failed to import schemas: {e}")


def test_crud_import():
    """Test that CRUD operations can be imported."""
    try:
        from src.crud.user import create_user
        from src.crud.task import create_task_for_user
        assert create_user is not None
        assert create_task_for_user is not None
    except ImportError as e:
        raise AssertionError(f"Failed to import CRUD operations: {e}")


def test_auth_import():
    """Test that authentication components can be imported."""
    try:
        from src.auth.jwt import create_access_token
        from src.auth.security import get_current_user
        assert create_access_token is not None
        assert get_current_user is not None
    except ImportError as e:
        raise AssertionError(f"Failed to import authentication components: {e}")
