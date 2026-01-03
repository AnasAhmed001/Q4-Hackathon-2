# Data Model: Console-Based Todo Application

## Todo Entity

### Fields
- **id** (int): Unique identifier for the todo, assigned sequentially starting from 1
- **title** (str): Title of the todo, provided by the user
- **completed** (bool): Completion status, defaults to False when created
- **description** (str, optional): Optional description of the todo, defaults to empty string

### Validation Rules
- **id**: Must be a positive integer, unique across all todos
- **title**: Must be a non-empty string (after trimming whitespace)
- **completed**: Must be a boolean value
- **description**: Optional, can be an empty string

### State Transitions
- **Creation**: id assigned, title set, completed = False, description = ""
- **Update**: title can be modified, description can be modified
- **Completion**: completed status toggles from False to True
- **Uncompletion**: completed status toggles from True to False
- **Deletion**: todo is removed from the collection

## In-Memory Store

### Structure
- **todos** (dict): Dictionary with integer keys (todo IDs) and Todo objects as values
- **next_id** (int): Counter to track the next available ID for new todos

### Operations
- **Create**: Add new todo to the dictionary with the next available ID
- **Read**: Retrieve todo by ID from the dictionary
- **Update**: Modify existing todo in the dictionary
- **Delete**: Remove todo from the dictionary by ID
- **List**: Return all todos in the dictionary