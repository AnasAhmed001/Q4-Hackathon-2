from fastapi import APIRouter, Depends, HTTPException, status

from src.auth.jwt_validator import JWTUser, decode_jwt_token
from src.api.deps import get_current_user_dependency

router = APIRouter()


@router.get("/auth/me")
async def get_current_user_info(current_user: JWTUser = Depends(get_current_user_dependency)):
    """Get current authenticated user information from Better Auth JWT.
    
    This endpoint validates the JWT token from Better Auth and returns
    the user information. Authentication is handled by Better Auth in Next.js.
    """
    return {
        "user": {
            "id": current_user.id,
            "email": current_user.email,
            "name": current_user.name,
        },
        "message": "JWT token is valid"
    }


@router.post("/auth/verify-token")
async def verify_token(token: str):
    """Verify a Better Auth JWT token (for debugging purposes).
    
    This endpoint can be used to manually verify JWT tokens during development.
    In production, token validation happens automatically via middleware.
    """
    try:
        payload = decode_jwt_token(token)
        return {
            "valid": True,
            "user": {
                "id": payload.user.id,
                "email": payload.user.email,
                "name": payload.user.name,
            },
            "session": {
                "id": payload.session.id,
                "expiresAt": payload.session.expiresAt.isoformat(),
            }
        }
    except HTTPException as e:
        return {
            "valid": False,
            "error": e.detail
        }
