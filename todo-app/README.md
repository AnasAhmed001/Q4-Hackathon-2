# 📝 Todo Application

A beautiful console-based todo application with in-memory storage built in Python. Features a colorful, menu-driven interface for efficient task management.

## ✨ Features

- ➕ Add new todos with unique IDs and timestamps
- 👁️ View all todos with their status and creation time
- ✅ Mark todos as complete/incomplete
- ✏️ Update todo titles
- 🗑️ Delete todos with confirmation
- 🎨 Colorful, user-friendly interface
- 🛡️ Comprehensive input validation and error handling

## 📋 Requirements

- Python 3.13+
- UV package manager ([Install UV](https://github.com/astral-sh/uv))

## 🚀 Installation

1. Navigate to the todo-app directory:
   ```bash
   cd todo-app
   ```

2. Sync dependencies and install the package:
   ```bash
   uv sync
   ```

   This will:
   - Create a virtual environment
   - Install the todo-app package
   - Set up the `todo` command

## 💻 Usage

### Running the Application

After installation, run:

```bash
uv run todo
```

Or if you've activated the virtual environment:

```bash
todo
```

### Menu Options

The application presents a colorful menu with 6 options:

1. **Add Todo** - Create a new task
2. **View Todos** - Display all tasks with status and timestamps
3. **Mark Todo as Complete** - Toggle completion status by ID
4. **Update Todo Title** - Modify an existing task's title
5. **Delete Todo** - Remove a task (with confirmation)
6. **Exit** - Quit the application

### Example Workflow

```bash
# Start the app
uv run todo

# Follow the prompts:
# 1. Add a todo: "Buy groceries"
# 2. View todos to see your new task
# 3. Mark it complete when done
# 4. Update the title if needed
# 5. Delete it when no longer needed
```

## 🧪 Testing

Run the test suite:

```bash
# Functional tests
uv run python tests/test_todo_app.py

# Validation tests
uv run python tests/test_validate.py
```

## 📁 Project Structure

```
todo-app/
├── src/
│   └── todo_app/
│       ├── __init__.py
│       ├── models/          # Data models (Todo)
│       ├── services/        # Business logic (TodoService, TodoStore)
│       ├── lib/             # Utilities (validators)
│       └── cli/             # CLI interface
├── tests/                   # Test files
├── pyproject.toml          # Project configuration
├── main.py                 # Alternative entry point
└── README.md
```

## 🏗️ Architecture

The application follows a clean architecture pattern:

- **Models** (`src/todo_app/models/`): Data structures with the Todo model
- **Services** (`src/todo_app/services/`): Business logic layer (TodoService, TodoStore)
- **Lib** (`src/todo_app/lib/`): Utility functions (input validators)
- **CLI** (`src/todo_app/cli/`): User interface layer with colorful menu

## 🔧 Development

### Running Directly from Source

```bash
uv run python main.py
```

### Running as a Module

```bash
uv run python -m todo_app.cli.todo_cli
```

## 📝 License

MIT