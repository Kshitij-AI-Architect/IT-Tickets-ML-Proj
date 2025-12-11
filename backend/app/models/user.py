"""User models."""
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    ADMIN = "admin"
    SME = "sme"
    PO = "po"
    ANALYST = "analyst"


class UserBase(BaseModel):
    email: EmailStr
    role: UserRole = UserRole.ANALYST


class UserCreate(UserBase):
    password: str
    org_id: Optional[str] = None  # If not provided, creates new org


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class User(UserBase):
    id: str
    org_id: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: User
