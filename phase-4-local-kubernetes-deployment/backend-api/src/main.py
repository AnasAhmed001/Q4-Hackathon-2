from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config.settings import settings
from src.api.auth import router as auth_router
from src.api.tasks import router as tasks_router
from src.api.chat import router as chat_router


def create_application() -> FastAPI:
    """Create and configure the FastAPI application."""

    # Create FastAPI app with metadata
    app = FastAPI(
        title="Task Management API",
        description="Secure REST API for managing user-specific todo tasks",
        version="1.0.0",
        openapi_url=f"{settings.api_prefix}/openapi.json",
        docs_url=f"{settings.api_prefix}/docs",
        redoc_url=f"{settings.api_prefix}/redoc",
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        # Additional security headers can be added here
    )

    # Include API routers
    app.include_router(auth_router, prefix=settings.api_prefix, tags=["Authentication"])
    app.include_router(tasks_router, prefix=settings.api_prefix, tags=["Tasks"])
    app.include_router(chat_router, prefix=settings.api_prefix, tags=["Chat"])

    # Health check endpoint
    @app.get("/health")
    async def health_check():
        return {"status": "healthy", "environment": settings.environment}

    return app


# Create the application instance
app = create_application()


# Application event handlers
@app.on_event("startup")
async def startup_event():
    """Handle startup events."""
    print(f"Starting Task Management API in {settings.environment} mode")


@app.on_event("shutdown")
async def shutdown_event():
    """Handle shutdown events."""
    print("Shutting down Task Management API")
