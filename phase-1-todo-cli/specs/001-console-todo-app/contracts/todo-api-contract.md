# Todo API Contract

This contract defines the functional operations that will be available for the todo application, designed to be framework-agnostic and ready for future API integration.

## Core Operations

### Add Todo
- **Operation**: Create a new todo
- **Input**: title (string), description (optional string)
- **Output**: Todo object with assigned ID
- **Success**: Todo is added to the collection with unique ID and "incomplete" status
- **Errors**: Invalid title (empty/whitespace)

### View Todos
- **Operation**: Retrieve all todos
- **Input**: None
- **Output**: List of all Todo objects
- **Success**: Returns complete list of todos with ID, title, and completion status
- **Errors**: None

### Update Todo
- **Operation**: Modify an existing todo's title
- **Input**: todo ID (integer), new title (string)
- **Output**: Updated Todo object
- **Success**: Todo title is updated
- **Errors**: Invalid ID, invalid title

### Delete Todo
- **Operation**: Remove a todo by ID
- **Input**: todo ID (integer)
- **Output**: Confirmation of deletion
- **Success**: Todo is removed from collection
- **Errors**: Invalid ID

### Mark Todo Complete
- **Operation**: Toggle or set completion status of a todo
- **Input**: todo ID (integer), completed status (boolean, optional)
- **Output**: Updated Todo object
- **Success**: Todo completion status is updated
- **Errors**: Invalid ID