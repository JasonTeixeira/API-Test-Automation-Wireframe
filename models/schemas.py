"""
Pydantic models for API request/response schema validation.

Provides type-safe models for all API entities with validation.
"""
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, EmailStr, Field, HttpUrl, field_validator


class Support(BaseModel):
    """Support information model."""
    url: HttpUrl
    text: str


class User(BaseModel):
    """User model for API responses."""
    id: int
    email: EmailStr
    first_name: str
    last_name: str
    avatar: HttpUrl
    
    @field_validator('id')
    @classmethod
    def validate_id(cls, v: int) -> int:
        """Validate user ID is positive."""
        if v <= 0:
            raise ValueError('User ID must be positive')
        return v


class UserCreate(BaseModel):
    """Model for user creation requests."""
    name: str = Field(..., min_length=1, max_length=100)
    job: str = Field(..., min_length=1, max_length=100)
    
    @field_validator('name', 'job')
    @classmethod
    def validate_not_empty(cls, v: str) -> str:
        """Validate fields are not empty or whitespace."""
        if not v.strip():
            raise ValueError('Field cannot be empty or whitespace')
        return v


class UserCreateResponse(BaseModel):
    """Model for user creation response."""
    name: str
    job: str
    id: str
    createdAt: str  # ISO 8601 datetime string


class UserUpdate(BaseModel):
    """Model for user update requests."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    job: Optional[str] = Field(None, min_length=1, max_length=100)


class UserUpdateResponse(BaseModel):
    """Model for user update response."""
    name: Optional[str] = None
    job: Optional[str] = None
    updatedAt: str  # ISO 8601 datetime string


class PaginationMeta(BaseModel):
    """Pagination metadata model."""
    page: int = Field(..., ge=1)
    per_page: int = Field(..., ge=1, le=100)
    total: int = Field(..., ge=0)
    total_pages: int = Field(..., ge=0)


class UsersListResponse(BaseModel):
    """Model for users list response."""
    page: int
    per_page: int
    total: int
    total_pages: int
    data: List[User]
    support: Support


class SingleUserResponse(BaseModel):
    """Model for single user response."""
    data: User
    support: Support


class Resource(BaseModel):
    """Resource model for API responses."""
    id: int
    name: str
    year: int = Field(..., ge=1900, le=2100)
    color: str = Field(..., pattern=r'^#[0-9A-Fa-f]{6}$')  # Hex color
    pantone_value: str
    
    @field_validator('id')
    @classmethod
    def validate_id(cls, v: int) -> int:
        """Validate resource ID is positive."""
        if v <= 0:
            raise ValueError('Resource ID must be positive')
        return v


class ResourceCreate(BaseModel):
    """Model for resource creation requests."""
    name: str = Field(..., min_length=1, max_length=100)
    year: int = Field(..., ge=1900, le=2100)
    color: str = Field(..., pattern=r'^#[0-9A-Fa-f]{6}$')
    pantone_value: str = Field(..., min_length=1)


class ResourcesListResponse(BaseModel):
    """Model for resources list response."""
    page: int
    per_page: int
    total: int
    total_pages: int
    data: List[Resource]
    support: Support


class SingleResourceResponse(BaseModel):
    """Model for single resource response."""
    data: Resource
    support: Support


class RegisterRequest(BaseModel):
    """Model for registration requests."""
    email: EmailStr
    password: str = Field(..., min_length=6)


class RegisterResponse(BaseModel):
    """Model for successful registration response."""
    id: int
    token: str
    
    @field_validator('token')
    @classmethod
    def validate_token(cls, v: str) -> str:
        """Validate token is not empty."""
        if not v:
            raise ValueError('Token cannot be empty')
        return v


class LoginRequest(BaseModel):
    """Model for login requests."""
    email: EmailStr
    password: str = Field(..., min_length=1)


class LoginResponse(BaseModel):
    """Model for successful login response."""
    token: str
    
    @field_validator('token')
    @classmethod
    def validate_token(cls, v: str) -> str:
        """Validate token is not empty."""
        if not v:
            raise ValueError('Token cannot be empty')
        return v


class ErrorResponse(BaseModel):
    """Model for error responses."""
    error: str
    
    @field_validator('error')
    @classmethod
    def validate_error(cls, v: str) -> str:
        """Validate error message is not empty."""
        if not v:
            raise ValueError('Error message cannot be empty')
        return v


class DelayedResponse(BaseModel):
    """Model for delayed API responses (performance testing)."""
    page: int
    per_page: int
    total: int
    total_pages: int
    data: List[User]
    support: Support


# Schema validation helper functions
def validate_user_schema(data: Dict[str, Any]) -> User:
    """
    Validate user data against User schema.
    
    Args:
        data: User data dictionary
        
    Returns:
        Validated User model
        
    Raises:
        ValidationError: If validation fails
    """
    return User(**data)


def validate_users_list_schema(data: Dict[str, Any]) -> UsersListResponse:
    """
    Validate users list response against schema.
    
    Args:
        data: Users list data dictionary
        
    Returns:
        Validated UsersListResponse model
        
    Raises:
        ValidationError: If validation fails
    """
    return UsersListResponse(**data)


def validate_resource_schema(data: Dict[str, Any]) -> Resource:
    """
    Validate resource data against Resource schema.
    
    Args:
        data: Resource data dictionary
        
    Returns:
        Validated Resource model
        
    Raises:
        ValidationError: If validation fails
    """
    return Resource(**data)


def validate_error_response(data: Dict[str, Any]) -> ErrorResponse:
    """
    Validate error response against schema.
    
    Args:
        data: Error data dictionary
        
    Returns:
        Validated ErrorResponse model
        
    Raises:
        ValidationError: If validation fails
    """
    return ErrorResponse(**data)


# Schema dictionaries for JSON Schema validation
USER_SCHEMA = {
    "type": "object",
    "properties": {
        "id": {"type": "integer", "minimum": 1},
        "email": {"type": "string", "format": "email"},
        "first_name": {"type": "string", "minLength": 1},
        "last_name": {"type": "string", "minLength": 1},
        "avatar": {"type": "string", "format": "uri"}
    },
    "required": ["id", "email", "first_name", "last_name", "avatar"]
}

USERS_LIST_SCHEMA = {
    "type": "object",
    "properties": {
        "page": {"type": "integer", "minimum": 1},
        "per_page": {"type": "integer", "minimum": 1},
        "total": {"type": "integer", "minimum": 0},
        "total_pages": {"type": "integer", "minimum": 0},
        "data": {
            "type": "array",
            "items": USER_SCHEMA
        },
        "support": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "format": "uri"},
                "text": {"type": "string"}
            },
            "required": ["url", "text"]
        }
    },
    "required": ["page", "per_page", "total", "total_pages", "data", "support"]
}

RESOURCE_SCHEMA = {
    "type": "object",
    "properties": {
        "id": {"type": "integer", "minimum": 1},
        "name": {"type": "string", "minLength": 1},
        "year": {"type": "integer", "minimum": 1900, "maximum": 2100},
        "color": {"type": "string", "pattern": "^#[0-9A-Fa-f]{6}$"},
        "pantone_value": {"type": "string", "minLength": 1}
    },
    "required": ["id", "name", "year", "color", "pantone_value"]
}

ERROR_SCHEMA = {
    "type": "object",
    "properties": {
        "error": {"type": "string", "minLength": 1}
    },
    "required": ["error"]
}
