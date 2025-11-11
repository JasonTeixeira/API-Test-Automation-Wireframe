"""
Resources API client for ReqRes.in Resource endpoints.

Provides methods for resource-related API operations.
"""
from typing import Any, Optional

from clients.base_client import APIResponse, BaseClient


class ResourcesClient(BaseClient):
    """Client for Resources API endpoints."""
    
    def __init__(self, **kwargs: Any):
        """Initialize Resources client."""
        super().__init__(**kwargs)
        self.endpoint_prefix = "unknown"  # ReqRes.in uses 'unknown' for resources
    
    def get_resources(
        self,
        page: Optional[int] = None,
        per_page: Optional[int] = None
    ) -> APIResponse:
        """
        Get list of resources with pagination.
        
        Args:
            page: Page number
            per_page: Number of resources per page
            
        Returns:
            APIResponse with list of resources
        """
        params = {}
        if page is not None:
            params["page"] = page
        if per_page is not None:
            params["per_page"] = per_page
        
        return self.get(self.endpoint_prefix, params=params)
    
    def get_resource(self, resource_id: int) -> APIResponse:
        """
        Get single resource by ID.
        
        Args:
            resource_id: Resource ID
            
        Returns:
            APIResponse with resource data
        """
        return self.get(f"{self.endpoint_prefix}/{resource_id}")
    
    def create_resource(
        self,
        name: str,
        year: int,
        color: str,
        pantone_value: str,
        **additional_fields: Any
    ) -> APIResponse:
        """
        Create a new resource.
        
        Args:
            name: Resource name
            year: Resource year
            color: Resource color code
            pantone_value: Pantone value
            **additional_fields: Additional resource fields
            
        Returns:
            APIResponse with created resource data
        """
        data = {
            "name": name,
            "year": year,
            "color": color,
            "pantone_value": pantone_value,
            **additional_fields
        }
        return self.post(self.endpoint_prefix, json_data=data)
    
    def update_resource(
        self,
        resource_id: int,
        **fields: Any
    ) -> APIResponse:
        """
        Update resource using PUT.
        
        Args:
            resource_id: Resource ID
            **fields: Fields to update
            
        Returns:
            APIResponse with updated resource data
        """
        return self.put(f"{self.endpoint_prefix}/{resource_id}", json_data=fields)
    
    def partial_update_resource(
        self,
        resource_id: int,
        **fields: Any
    ) -> APIResponse:
        """
        Partially update resource using PATCH.
        
        Args:
            resource_id: Resource ID
            **fields: Fields to update
            
        Returns:
            APIResponse with updated resource data
        """
        return self.patch(f"{self.endpoint_prefix}/{resource_id}", json_data=fields)
    
    def delete_resource(self, resource_id: int) -> APIResponse:
        """
        Delete resource by ID.
        
        Args:
            resource_id: Resource ID
            
        Returns:
            APIResponse (typically 204 No Content)
        """
        return self.delete(f"{self.endpoint_prefix}/{resource_id}")
