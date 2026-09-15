from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from enum import Enum


class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"


class UserBase(BaseModel):
    email: str = Field(..., description="User's email address")
    name: Optional[str] = Field(None, max_length=100, description="User's display name")


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, description="User's password")


class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100, description="User's display name")
    email: Optional[str] = Field(None, description="User's email address")


class UserRead(UserBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    email: str = Field(..., description="User's email address")
    password: str = Field(..., description="User's password")


class UserResponse(BaseModel):
    user: UserRead
    token: str
    expires_at: datetime

    class Config:
        from_attributes = True
