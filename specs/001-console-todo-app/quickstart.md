# Quickstart Guide: Console-Based Todo Application

## Getting Started

This guide will help you quickly set up and run the console-based todo application.

### Prerequisites

- Python 3.13+
- UV package manager

## Installation

1. Navigate to the `todo-app` directory:
   ```bash
   cd todo-app
   ```

2. Install the application in development mode:
   ```bash
   uv sync
   # or alternatively
   pip install -e .
   ```

## Running the Application

After installation, you can run the application in one of two ways:

1. Using the installed command:
   ```bash
   todo
   ```

2. Running directly from source:
   ```bash
   python -m src.todo_app.cli.todo_cli
   ```

### Basic Usage

Once the application is running, you'll see a menu with the following options:

1. **Add Todo** - Create a new todo with a title
2. **View Todos** - See all your todos with their status
3. **Mark Todo as Complete** - Mark a todo as completed
4. **Update Todo Title** - Change the title of an existing todo
5. **Delete Todo** - Remove a todo from your list
6. **Exit** - Quit the application

## Example Workflow

1. Select "1" to add a new todo, then enter a title like "Buy groceries"
2. Select "2" to view your todos and see the newly added item
3. Select "3" to mark the todo as complete
4. Select "4" to update the todo title if needed
5. Select "5" to delete a todo when you're done with it

## Troubleshooting

- If you get a "command not found" error for `todo`, make sure you installed the package with `pip install -e .` and that your PATH includes the Python scripts directory.
- If the application crashes, make sure you're entering valid inputs (e.g., numeric IDs, non-empty titles).