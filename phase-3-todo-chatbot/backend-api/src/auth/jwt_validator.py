"""
JWT Authentication Module for FastAPI

This module handles JWT token validation for requests from the Next.js frontend.
It verifies JWT tokens issued by Better Auth and extracts user information.
"""

import os
from datetime import datetime
from typing import Optional, Any, Dict

import jwt
from jwt import PyJWKClient
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel

# HTTP Bearer token scheme
security = HTTPBearer()


class JWTUser(BaseModel):
    """User information extracted from JWT token"""
    id: str
    email: Optional[str] = None
    name: Optional[str] = None


class JWTSession(BaseModel):
    """Session information from JWT token"""
    id: str
    expiresAt: datetime


class JWTPayload(BaseModel):
    """Complete JWT payload structure"""
    user: Optional[JWTUser] = None
    session: Optional[JWTSession] = None
    sub: Optional[str] = None
    email: Optional[str] = None
    name: Optional[str] = None
    iat: int  # Issued at
    exp: int  # Expiration


def get_jwks_url() -> str:
    """Resolve the Better Auth JWKS endpoint."""
    env_url = os.getenv("BETTER_AUTH_JWKS_URL")
    if env_url:
        return env_url

    base_url = os.getenv("BETTER_AUTH_URL") or os.getenv("NEXT_PUBLIC_BETTER_AUTH_URL")
    if base_url:
        return base_url.rstrip("/") + "/api/auth/jwks"

    return "http://localhost:3000/api/auth/jwks"


def get_jwks_client() -> PyJWKClient:
    """Create a JWKS client for verifying Better Auth JWTs."""
    return PyJWKClient(get_jwks_url())


def decode_jwt_token(token: str) -> JWTPayload:
    """
    Decode and validate JWT token from Better Auth.

    Args:
        token: JWT token string from Authorization header

    Returns:
        JWTPayload: Decoded and validated token payload

    Raises:
        HTTPException: If token is invalid, expired, or malformed
    """
    try:
        jwks_client = get_jwks_client()
        signing_key = jwks_client.get_signing_key_from_jwt(token)

        unverified_header = jwt.get_unverified_header(token)
        alg = unverified_header.get("alg", "RS256")

        payload: Dict[str, Any] = jwt.decode(
            token,
            signing_key.key,
            algorithms=[alg],
            audience=None,
            options={"verify_aud": False},
        )

        return JWTPayload(**payload)

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired. Please sign in again.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid authentication token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication error: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> JWTUser:
    """
    FastAPI dependency to get the current authenticated user.

    This extracts the JWT token from the Authorization header,
    validates it, and returns the user information.

    Usage:
        @app.get("/api/me")
        async def get_me(user: JWTUser = Depends(get_current_user)):
            return {"user_id": user.id, "email": user.email}

    Args:
        credentials: HTTP Bearer token from Authorization header

    Returns:
        JWTUser: Current authenticated user information

    Raises:
        HTTPException: If authentication fails
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = decode_jwt_token(credentials.credentials)

    user = payload.user or JWTUser(
        id=payload.sub or "",
        email=payload.email,
        name=payload.name,
    )

    if not user.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token: missing user id",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


async def validate_user_access(
    user_id: str,
    current_user: JWTUser = Depends(get_current_user)
) -> JWTUser:
    """
    Validate that the authenticated user matches the requested user_id.

    This is a critical security check for routes like /api/{user_id}/tasks
    to ensure users can only access their own data.

    Usage:
        @app.get("/api/{user_id}/tasks")
        async def get_tasks(
            user_id: str,
            user: JWTUser = Depends(validate_user_access)
        ):
            # user_id is guaranteed to match authenticated user
            return await fetch_user_tasks(user_id)

    Args:
        user_id: User ID from the URL path parameter
        current_user: Current authenticated user from JWT token

    Returns:
        JWTUser: Validated current user

    Raises:
        HTTPException: If user_id doesn't match authenticated user
    """
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                f"Access denied. You are authenticated as user {current_user.id} "
                f"but attempting to access data for user {user_id}."
            ),
        )

    return current_user


# Optional: Dependency to extract user ID for use in queries
async def get_current_user_id(
    current_user: JWTUser = Depends(get_current_user)
) -> str:
    """
    Simple dependency to extract just the user ID.

    Usage:
        @app.get("/api/my-profile")
        async def get_profile(user_id: str = Depends(get_current_user_id)):
            return await fetch_profile(user_id)
    """
    return current_user.id
