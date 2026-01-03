# Todo Application

A console-based todo application with in-memory storage built in Python.

## Features

- Add new todos with unique IDs
- View all todos with their status
- Mark todos as complete/incomplete
- Update todo titles
- Delete todos
- Input validation and error handling

## Requirements

- Python 3.13+
- UV package manager

## Installation

1. Clone or download the repository
2. Navigate to the `todo-app` directory
3. Install the package in development mode:

```bash
uv sync
# or
pip install -e .
```

## Usage

Run the application:

```bash
# After installation
todo
```

Or run directly from source:

```bash
python -m src.todo_app.cli.todo_cli
```

## Architecture

The application follows a clean architecture pattern:

- **Models**: Data structures (Todo model)
- **Services**: Business logic (TodoService, TodoStore)
- **Lib**: Utilities (Input validators)
- **CLI**: User interface layer

## License

MIT