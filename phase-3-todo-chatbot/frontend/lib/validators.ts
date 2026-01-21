// Input Validation Functions

// Task validation
export const validateTask = (task: {
  title?: string;
  description?: string;
  dueDate?: string;
}): Record<string, string> => {
  const errors: Record<string, string> = {};

  // Validate title (required, 1-200 chars)
  if (!task.title || task.title.trim().length === 0) {
    errors.title = 'Title is required';
  } else if (task.title.length > 200) {
    errors.title = 'Title too long (max 200 characters)';
  }

  // Validate description (optional, max 1000 chars)
  if (task.description && task.description.length > 1000) {
    errors.description = 'Description too long (max 1000 characters)';
  }

  // Validate due date (if provided, must be in future)
  if (task.dueDate) {
    const dueDate = new Date(task.dueDate);
    const now = new Date();
    if (dueDate < now) {
      errors.dueDate = 'Due date must be in the future';
    }
  }

  return errors;
};

// User validation (for login/signup)
export const validateUser = (userData: {
  email?: string;
  password?: string;
  name?: string;
}): Record<string, string> => {
  const errors: Record<string, string> = {};

  // Validate email (required, valid format)
  if (!userData.email || userData.email.trim().length === 0) {
    errors.email = 'Email is required';
  } else if (!isValidEmail(userData.email)) {
    errors.email = 'Please enter a valid email address';
  }

  // Validate password (required, min 8 chars)
  if (!userData.password || userData.password.length < 8) {
    errors.password = 'Password must be at least 8 characters';
  }

  // Validate name (optional, max 100 chars)
  if (userData.name && userData.name.length > 100) {
    errors.name = 'Name too long (max 100 characters)';
  }

  return errors;
};

// Email validation helper
export const isValidEmail = (email: string): boolean => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

// Generic string validation
export const validateString = (
  value: string,
  fieldName: string,
  options: {
    required?: boolean;
    minLength?: number;
    maxLength?: number;
    pattern?: RegExp;
  } = {}
): Record<string, string> => {
  const errors: Record<string, string> = {};

  // Check if required
  if (options.required && (!value || value.trim().length === 0)) {
    errors[fieldName] = `${fieldName.charAt(0).toUpperCase() + fieldName.slice(1)} is required`;
    return errors;
  }

  // Skip further validation if not required and empty
  if (!options.required && (!value || value.trim().length === 0)) {
    return errors;
  }

  // Min length check
  if (options.minLength && value.length < options.minLength) {
    errors[fieldName] = `${fieldName.charAt(0).toUpperCase() + fieldName.slice(1)} must be at least ${options.minLength} characters`;
  }

  // Max length check
  if (options.maxLength && value.length > options.maxLength) {
    errors[fieldName] = `${fieldName.charAt(0).toUpperCase() + fieldName.slice(1)} must be no more than ${options.maxLength} characters`;
  }

  // Pattern check
  if (options.pattern && !options.pattern.test(value)) {
    errors[fieldName] = `${fieldName.charAt(0).toUpperCase() + fieldName.slice(1)} format is invalid`;
  }

  return errors;
};

// Task status validation
export const isValidTaskStatus = (status: string): status is 'pending' | 'completed' => {
  return status === 'pending' || status === 'completed';
};

// UUID validation (basic check)
export const isValidUuid = (uuid: string): boolean => {
  const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
  return uuidRegex.test(uuid);
};