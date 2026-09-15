# Task Management Backend API

Secure REST API for managing user-specific todo tasks with Neon Serverless PostgreSQL storage, JWT authentication, and comprehensive user data isolation.

## Features

- JWT-based authentication with Bearer tokens
- Full CRUD operations for tasks with user ownership
- Task filtering and search capabilities
- User data isolation with multi-layer security
- Neon Serverless PostgreSQL for scalable storage
- Comprehensive error handling and validation

## Tech Stack

- FastAPI for REST endpoints
- SQLModel for ORM
- Neon Serverless PostgreSQL for storage
- JWT for authentication

## Setup

1. Install dependencies with Poetry:
   ```bash
   poetry install
   ```

2. Copy environment variables:
   ```bash
   cp .env.example .env
   ```

3. Update .env with your database configuration

4. Run database migrations:
   ```bash
   poetry run alembic upgrade head
   ```

5. Start the development server:
   ```bash
   poetry run uvicorn src.main:app --reload
   ```

## API Documentation

API documentation is available at `/docs` and `/redoc` endpoints when running the application.

## Environment Variables

See `.env.example` for all required environment variables.

## Development

Run tests:
```bash
poetry run pytest
```

Format code:
```bash
poetry run black src/
```

## License

[Specify license here]