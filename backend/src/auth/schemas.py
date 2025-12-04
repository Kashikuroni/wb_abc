"""
Pydantic schemas for authentication and user management.

Defines data models for user registration, login, and user profile responses.
Used for request validation and response serialization in authentication endpoints.
"""
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from src.auth.models import Role


class UserShort(BaseModel):
    """
    Lightweight user model without nested relationships.
    
    Simplified user representation containing only essential fields,
    used when full user details are not needed (e.g., in lists or references).
    
    Attributes:
        id: Unique user identifier (UUID).
        email: User email address.
        first_name: User first name.
        last_name: User last name.
        username: Optional username/nickname.
    """
    id: UUID
    email: EmailStr
    first_name: str
    last_name: str
    username: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class RegisterForm(BaseModel):
    """
    User registration request schema.
    
    Validates user input for account creation. Accepts camelCase field names
    from frontend via aliases while using snake_case internally.
    
    Attributes:
        email: User email address (must be valid email format).
        password: User password (plain text, will be hashed before storage).
        first_name: User first name (accepts 'firstName' from frontend).
        last_name: User last name (accepts 'lastName' from frontend).
        username: Optional username/nickname.
    """
    email: EmailStr
    password: str
    first_name: str = Field(..., alias="firstName")
    last_name: str = Field(..., alias="lastName")
    username: Optional[str] = None


class LoginForm(BaseModel):
    """
    User login request schema.
    
    Validates credentials for authentication.
    
    Attributes:
        email: User email address.
        password: User password (plain text, verified against hashed password).
    """
    email: EmailStr
    password: str


class UserRead(BaseModel):
    """
    User profile response schema.
    
    Complete user information returned to authenticated clients.
    Includes role information for authorization purposes.
    
    Attributes:
        id: Unique user identifier (UUID).
        email: User email address.
        first_name: User first name.
        last_name: User last name.
        username: Optional username/nickname.
        role: User role (ADMIN, USER, GUEST, etc.) for access control.
    """
    id: UUID
    email: EmailStr
    first_name: str
    last_name: str
    username: Optional[str]
    role: Role

    model_config = ConfigDict(from_attributes=True)
