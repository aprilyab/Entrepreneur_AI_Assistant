# backend/app/schemas/user.py
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from uuid import UUID
from datetime import datetime


class UserCreate(BaseModel):
    email: EmailStr
    name: str = Field(min_length=1, max_length=255)
    password: str = Field(min_length=8, max_length=72)


class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=72)


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: EmailStr
    name: str
    created_at: datetime


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
