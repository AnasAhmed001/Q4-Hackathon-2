# 🚀 Quickstart Guide: Console-Based Todo Application

## Getting Started

This guide will help you quickly set up and run the colorful console-based todo application in under 2 minutes!

### Prerequisites

- **Python 3.13+** installed on your system
- **UV package manager** ([Install UV](https://github.com/astral-sh/uv))

---

## 📦 Installation (2 Steps)

### Step 1: Navigate to the Project

```bash
cd todo-app
```

### Step 2: Install Dependencies

```bash
uv sync
```

This command will:
- ✅ Create a virtual environment (`.venv/`)
- ✅ Install the todo-app package
- ✅ Configure the `todo` command
- ✅ Set up all dependencies

**That's it!** You're ready to run the app. 🎉

---

## ▶️ Running the Application

### Method 1: Using UV (Recommended)

```bash
uv run todo
```

### Method 2: Direct Python Execution

```bash
uv run python main.py
```

### Method 3: As a Module

```bash
uv run python -m todo_app.cli.todo_cli
```

---

## 🎨 Using the Application

### Main Menu

When you start the app, you'll see a colorful menu:

```
┌──────────────────────────────────────────────────┐
│              📋 MAIN MENU                        │
├──────────────────────────────────────────────────┤
│  1. Add Todo                                     │
│  2. View Todos                                   │
│  3. Mark Todo as Complete                        │
│  4. Update Todo Title                            │
│  5. Delete Todo                                  │
│  6. Exit                                         │
└──────────────────────────────────────────────────┘
```

### Menu Options Explained

1. **➕ Add Todo** - Create a new task with a title
   - Enter a descriptive title (up to 200 characters)
   - Gets a unique ID and timestamp automatically

2. **👁️ View Todos** - Display all your tasks
   - Shows ID, title, completion status (✅/○), and creation time
   - Empty message if no todos exist

3. **✅ Mark Todo as Complete** - Toggle completion status
   - Enter the todo ID to mark as done
   - Validates ID before updating

4. **✏️ Update Todo Title** - Modify an existing task
   - Enter the todo ID and new title
   - Original creation time is preserved

5. **🗑️ Delete Todo** - Remove a task permanently
   - Enter the todo ID
   - Asks for confirmation before deletion

6. **🚪 Exit** - Quit the application gracefully

---

## 📝 Example Workflow

### Scenario: Managing Your Day

```bash
# Step 1: Start the application
uv run todo

# Step 2: Add your first todo
👉 Enter your choice (1-6): 1
📝 Enter todo title: Buy groceries
✅ Successfully added: [○] 1: Buy groceries (created: 2026-01-03 16:30)

# Step 3: Add more todos
👉 Enter your choice (1-6): 1
📝 Enter todo title: Call dentist
✅ Successfully added: [○] 2: Call dentist (created: 2026-01-03 16:31)

# Step 4: View all todos
👉 Enter your choice (1-6): 2

👁️ YOUR TODO LIST
────────────────────────────────────────────────────
📊 Total tasks: 2

  [○] 1: Buy groceries (created: 2026-01-03 16:30)
  [○] 2: Call dentist (created: 2026-01-03 16:31)

# Step 5: Mark first todo as complete
👉 Enter your choice (1-6): 3
🔢 Enter the ID of the todo to mark as complete: 1
✅ Successfully marked todo as complete: [✓] 1: Buy groceries

# Step 6: Update a todo title
👉 Enter your choice (1-6): 4
🔢 Enter the ID of the todo to update: 2
✏️ Enter the new title: Schedule dentist appointment
✅ Successfully updated todo: [○] 2: Schedule dentist appointment

# Step 7: Delete completed todo
👉 Enter your choice (1-6): 5
🔢 Enter the ID of the todo to delete: 1
⚠️ Are you sure? (yes/no): yes
✅ Successfully deleted todo.

# Step 8: Exit
👉 Enter your choice (1-6): 6
✅ Thank you for using the Todo Application. Goodbye! 👋
```

---

## 🧪 Testing the Application

Run automated tests to verify everything works:

```bash
# Run functional tests
uv run python tests/test_todo_app.py

# Run requirement validation tests
uv run python tests/test_validate.py
```

---

## ❗ Troubleshooting

### Issue: "command not found: uv"

**Solution:** Install UV package manager:
```bash
# On Windows (PowerShell)
iwr https://astral.sh/uv/install.ps1 | iex

# On macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Issue: "Failed to spawn: `todo`"

**Solution:** Make sure you ran `uv sync` first, then use:
```bash
uv run todo
```

### Issue: Application crashes on input

**Solution:** Ensure you're entering:
- Valid integers for menu choices (1-6)
- Valid todo IDs (positive integers)
- Non-empty titles for todos

### Issue: Colors not displaying correctly

**Solution:** 
- Windows: Use Windows Terminal or PowerShell 7+
- Ensure your terminal supports ANSI color codes

---

## 💡 Tips for Best Experience

- ✨ Use **Windows Terminal** or **PowerShell 7+** on Windows for best color display
- 📱 Keep todo titles concise (under 50 chars) for better readability
- 🎯 Use descriptive titles: "Buy milk" ✅ instead of "Shopping" ❌
- 🗑️ Delete completed todos regularly to keep your list clean
- 💾 Remember: Data is stored in memory only (resets when app closes)

---

## 🎓 Next Steps

- Read the full [README.md](../todo-app/README.md) for architecture details
- Check out [spec.md](spec.md) for complete feature specifications
- Review [data-model.md](data-model.md) for data structure details

Happy task managing! 🎉