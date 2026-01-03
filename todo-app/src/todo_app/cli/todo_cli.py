"""
Main CLI entry point for the todo application.
"""
from todo_app.services.todo_service import TodoService
from todo_app.lib.colors import Colors


def main():
    """
    Main entry point for the todo application CLI.
    """
    service = TodoService()
    app = TodoCLI(service)
    app.run()


class TodoCLI:
    """
    Command-line interface for the todo application.
    """
    def __init__(self, service: TodoService):
        self.service = service

    def run(self):
        """
        Run the main application loop.
        """
        self.clear_screen()
        print(Colors.BRIGHT_CYAN + "╔" + "═" * 58 + "╗" + Colors.RESET)
        print(Colors.BRIGHT_CYAN + "║" + Colors.RESET + " " * 15 + Colors.colorize("📝 TODO APPLICATION", Colors.BRIGHT_MAGENTA, bold=True) + " " * 24 + Colors.BRIGHT_CYAN + "║" + Colors.RESET)
        print(Colors.BRIGHT_CYAN + "╚" + "═" * 58 + "╝" + Colors.RESET)
        print("\n" + Colors.colorize("✨ Manage your tasks efficiently with this console-based tool.", Colors.BRIGHT_YELLOW) + "\n")

        while True:
            self.display_menu()
            choice = input("\n" + Colors.colorize("👉 Enter your choice (1-6): ", Colors.BRIGHT_WHITE, bold=True)).strip()

            if choice == '1':
                self.add_todo()
            elif choice == '2':
                self.view_todos()
            elif choice == '3':
                self.mark_complete()
            elif choice == '4':
                self.update_todo()
            elif choice == '5':
                self.delete_todo()
            elif choice == '6':
                print("\n" + Colors.success("✅ Thank you for using the Todo Application. Goodbye! 👋") + "\n")
                break
            else:
                print("\n" + Colors.error("❌ Invalid choice. Please enter a number between 1-6."))
            
            input("\n" + Colors.dim_text("⏸️  Press Enter to continue..."))

    def clear_screen(self):
        """
        Clear the terminal screen.
        """
        import os
        os.system('cls' if os.name == 'nt' else 'clear')

    def display_menu(self):
        """
        Display the main menu options.
        """
        self.clear_screen()
        border = Colors.BRIGHT_BLUE
        reset = Colors.RESET
        width = 50
        
        def format_line(text, visual_length):
            """Format a line with proper padding to align right border"""
            padding = width - 2 - visual_length
            return border + "│  " + reset + text + (" " * padding) + border + "│" + reset
        
        print("\n" + border + "┌" + "─" * width + "┐" + reset)
        # Title line - "📋 MAIN MENU" = emoji(2) + " MAIN MENU"(10) = 12 total
        title_text = Colors.colorize("📋 MAIN MENU", Colors.BRIGHT_CYAN, bold=True)
        title_visual = 12
        title_padding_left = (width - title_visual) // 2
        title_padding_right = width - title_visual - title_padding_left
        print(border + "│" + reset + (" " * title_padding_left) + title_text + (" " * title_padding_right) + border + "│" + reset)
        print(border + "├" + "─" * width + "┤" + reset)
        
        # Menu items with exact visual lengths
        print(format_line(Colors.colorize("1. Add Todo", Colors.BRIGHT_GREEN, bold=True), 11))
        print(format_line(Colors.colorize("2. View Todos", Colors.BRIGHT_CYAN, bold=True), 13))
        print(format_line(Colors.colorize("3. Mark Todo as Complete", Colors.BRIGHT_YELLOW, bold=True), 24))
        print(format_line(Colors.colorize("4. Update Todo Title", Colors.BRIGHT_MAGENTA, bold=True), 20))
        print(format_line(Colors.colorize("5. Delete Todo", Colors.BRIGHT_RED, bold=True), 14))
        print(format_line(Colors.colorize("6. Exit", Colors.BRIGHT_WHITE, bold=True), 7))
        
        print(border + "└" + "─" * width + "┘" + reset)

    def add_todo(self):
        """
        Handle adding a new todo.
        """
        print("\n" + Colors.BRIGHT_GREEN + "─" * 60 + Colors.RESET)
        print(Colors.colorize("➕ ADD NEW TODO", Colors.BRIGHT_GREEN, bold=True))
        print(Colors.BRIGHT_GREEN + "─" * 60 + Colors.RESET)
        title = input("\n" + Colors.colorize("📝 Enter todo title: ", Colors.BRIGHT_CYAN, bold=True)).strip()
        result = self.service.add_todo(title)

        if result:
            print("\n" + Colors.success(f"✅ Successfully added: {result}"))
        else:
            print("\n" + Colors.error("❌ Failed to add todo. Please check your input."))

    def view_todos(self):
        """
        Handle viewing all todos.
        """
        todos = self.service.get_all_todos()

        print("\n" + Colors.BRIGHT_CYAN + "─" * 60 + Colors.RESET)
        print(Colors.colorize("👁️  YOUR TODO LIST", Colors.BRIGHT_CYAN, bold=True))
        print(Colors.BRIGHT_CYAN + "─" * 60 + Colors.RESET)

        if not todos:
            print("\n" + Colors.warning("📭 No todos found. Your list is empty!"))
            return

        print(f"\n" + Colors.info(f"📊 Total tasks: {len(todos)}"))
        print("\n" + Colors.BRIGHT_BLUE + "═" * 60 + Colors.RESET)
        for todo in todos:
            print(f"  {todo}")
        print(Colors.BRIGHT_BLUE + "═" * 60 + Colors.RESET)

    def mark_complete(self):
        """
        Handle marking a todo as complete.
        """
        self.view_todos()
        if not self.service.get_all_todos():
            return

        todo_id_str = input("\n" + Colors.colorize("🔢 Enter the ID of the todo to mark as complete: ", Colors.BRIGHT_YELLOW, bold=True)).strip()
        result = self.service.mark_complete(todo_id_str)

        if result:
            print("\n" + Colors.success(f"✅ Successfully marked todo as complete: {result}"))
        else:
            print("\n" + Colors.error("❌ Failed to mark todo as complete. Please check the ID."))

    def update_todo(self):
        """
        Handle updating a todo title.
        """
        self.view_todos()
        if not self.service.get_all_todos():
            return

        todo_id_str = input("\n" + Colors.colorize("🔢 Enter the ID of the todo to update: ", Colors.BRIGHT_MAGENTA, bold=True)).strip()
        new_title = input(Colors.colorize("✏️  Enter the new title: ", Colors.BRIGHT_MAGENTA, bold=True)).strip()

        result = self.service.update_todo(todo_id_str, new_title)

        if result:
            print("\n" + Colors.success(f"✅ Successfully updated todo: {result}"))
        else:
            print("\n" + Colors.error("❌ Failed to update todo. Please check the ID and new title."))

    def delete_todo(self):
        """
        Handle deleting a todo.
        """
        self.view_todos()
        if not self.service.get_all_todos():
            return

        todo_id_str = input("\n" + Colors.colorize("🔢 Enter the ID of the todo to delete: ", Colors.BRIGHT_RED, bold=True)).strip()
        confirm = input(Colors.warning("⚠️  Are you sure? (yes/no): ")).strip().lower()
        
        if confirm not in ['yes', 'y']:
            print("\n" + Colors.info("🚫 Deletion cancelled."))
            return

        result = self.service.delete_todo(todo_id_str)

        if result:
            print("\n" + Colors.success("✅ Successfully deleted todo."))
        else:
            print("\n" + Colors.error("❌ Failed to delete todo. Please check the ID."))


if __name__ == "__main__":
    main()