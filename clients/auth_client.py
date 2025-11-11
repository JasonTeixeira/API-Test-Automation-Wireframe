"""
Authentication API client for ReqRes.in Auth endpoints.

Provides methods for authentication operations.
"""
from typing import Any, Optional

from clients.base_client import APIResponse, BaseClient


class AuthClient(BaseClient):
    """Client for Authentication API endpoints."""
    
    def __init__(self, **kwargs: Any):
        """Initialize Auth client."""
        super().__init__(**kwargs)
    
    def register(
        self,
        email: str,
        password: str,
        **additional_fields: Any
    ) -> APIResponse:
        """
        Register a new user.
        
        Args:
            email: User email
            password: User password
            **additional_fields: Additional registration fields
            
        Returns:
            APIResponse with token and user ID
        """
        data = {
            "email": email,
            "password": password,
            **additional_fields
        }
        return self.post("register", json_data=data)
    
    def register_unsuccessful(
        self,
        email: Optional[str] = None,
        password: Optional[str] = None
    ) -> APIResponse:
        """
        Attempt registration with incomplete data (for negative testing).
        
        Args:
            email: User email (optional)
            password: User password (optional)
            
        Returns:
            APIResponse with error
        """
        data = {}
        if email is not None:
            data["email"] = email
        if password is not None:
            data["password"] = password
        
        return self.post("register", json_data=data)
    
    def login(
        self,
        email: str,
        password: str,
        **additional_fields: Any
    ) -> APIResponse:
        """
        Login user and get token.
        
        Args:
            email: User email
            password: User password
            **additional_fields: Additional login fields
            
        Returns:
            APIResponse with authentication token
        """
        data = {
            "email": email,
            "password": password,
            **additional_fields
        }
        return self.post("login", json_data=data)
    
    def login_unsuccessful(
        self,
        email: Optional[str] = None,
        password: Optional[str] = None
    ) -> APIResponse:
        """
        Attempt login with invalid credentials (for negative testing).
        
        Args:
            email: User email (optional)
            password: User password (optional)
            
        Returns:
            APIResponse with error
        """
        data = {}
        if email is not None:
            data["email"] = email
        if password is not None:
            data["password"] = password
        
        return self.post("login", json_data=data)
    
    def logout(self, token: Optional[str] = None) -> APIResponse:
        """
        Logout user (if endpoint exists).
        
        Args:
            token: Authentication token
            
        Returns:
            APIResponse
            
        Note:
            ReqRes.in doesn't have a logout endpoint,
            but this is here for completeness
        """
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        
        return self.post("logout", headers=headers)
