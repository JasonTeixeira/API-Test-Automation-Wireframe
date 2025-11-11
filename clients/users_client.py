"""
Users API client for ReqRes.in Users endpoints.

Provides methods for all user-related API operations.
"""
from typing import Any, Dict, List, Optional

from clients.base_client import APIResponse, BaseClient


class UsersClient(BaseClient):
    """Client for Users API endpoints."""
    
    def __init__(self, **kwargs: Any):
        """Initialize Users client."""
        super().__init__(**kwargs)
        self.endpoint_prefix = "users"
    
    def get_users(
        self,
        page: Optional[int] = None,
        per_page: Optional[int] = None
    ) -> APIResponse:
        """
        Get list of users with pagination.
        
        Args:
            page: Page number
            per_page: Number of users per page
            
        Returns:
            APIResponse with list of users
        """
        params = {}
        if page is not None:
            params["page"] = page
        if per_page is not None:
            params["per_page"] = per_page
        
        return self.get(self.endpoint_prefix, params=params)
    
    def get_user(self, user_id: int) -> APIResponse:
        """
        Get single user by ID.
        
        Args:
            user_id: User ID
            
        Returns:
            APIResponse with user data
        """
        return self.get(f"{self.endpoint_prefix}/{user_id}")
    
    def create_user(
        self,
        name: str,
        job: str,
        **additional_fields: Any
    ) -> APIResponse:
        """
        Create a new user.
        
        Args:
            name: User name
            job: User job title
            **additional_fields: Additional user fields
            
        Returns:
            APIResponse with created user data
        """
        data = {
            "name": name,
            "job": job,
            **additional_fields
        }
        return self.post(self.endpoint_prefix, json_data=data)
    
    def update_user(
        self,
        user_id: int,
        name: Optional[str] = None,
        job: Optional[str] = None,
        **additional_fields: Any
    ) -> APIResponse:
        """
        Update user using PUT (full update).
        
        Args:
            user_id: User ID
            name: User name
            job: User job title
            **additional_fields: Additional fields to update
            
        Returns:
            APIResponse with updated user data
        """
        data = {}
        if name is not None:
            data["name"] = name
        if job is not None:
            data["job"] = job
        data.update(additional_fields)
        
        return self.put(f"{self.endpoint_prefix}/{user_id}", json_data=data)
    
    def partial_update_user(
        self,
        user_id: int,
        **fields: Any
    ) -> APIResponse:
        """
        Partially update user using PATCH.
        
        Args:
            user_id: User ID
            **fields: Fields to update
            
        Returns:
            APIResponse with updated user data
        """
        return self.patch(f"{self.endpoint_prefix}/{user_id}", json_data=fields)
    
    def delete_user(self, user_id: int) -> APIResponse:
        """
        Delete user by ID.
        
        Args:
            user_id: User ID
            
        Returns:
            APIResponse (typically 204 No Content)
        """
        return self.delete(f"{self.endpoint_prefix}/{user_id}")
    
    def get_delayed_users(self, delay: int = 3) -> APIResponse:
        """
        Get users with artificial delay (for performance testing).
        
        Args:
            delay: Delay in seconds
            
        Returns:
            APIResponse with users after delay
        """
        return self.get(f"{self.endpoint_prefix}?delay={delay}")
