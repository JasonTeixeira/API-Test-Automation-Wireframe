"""
Base API client with common HTTP operations and enterprise features.

Provides request/response handling, retry logic, logging, and response validation.
"""
import time
from typing import Any, Dict, Optional, Union

import requests
from requests.adapters import HTTPAdapter
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)
from urllib3.util.retry import Retry as URLRetry

from config.settings import settings
from utils.logger import logger


class APIResponse:
    """Wrapper for API response with convenient accessors."""
    
    def __init__(self, response: requests.Response, elapsed_time: float):
        """
        Initialize API response wrapper.
        
        Args:
            response: requests.Response object
            elapsed_time: Response time in seconds
        """
        self.response = response
        self.status_code = response.status_code
        self.headers = dict(response.headers)
        self.elapsed_time = elapsed_time
        self._json_data: Optional[Dict[str, Any]] = None
        self.text = response.text
    
    @property
    def json(self) -> Dict[str, Any]:
        """
        Get JSON response body.
        
        Returns:
            JSON response as dictionary
        """
        if self._json_data is None:
            try:
                self._json_data = self.response.json()
            except requests.exceptions.JSONDecodeError:
                logger.error(f"Failed to decode JSON response: {self.text[:200]}")
                self._json_data = {}
        return self._json_data
    
    def is_success(self) -> bool:
        """Check if response status is 2xx."""
        return 200 <= self.status_code < 300
    
    def is_client_error(self) -> bool:
        """Check if response status is 4xx."""
        return 400 <= self.status_code < 500
    
    def is_server_error(self) -> bool:
        """Check if response status is 5xx."""
        return 500 <= self.status_code < 600
    
    def __repr__(self) -> str:
        return f"<APIResponse [{self.status_code}] {self.elapsed_time:.3f}s>"


class BaseClient:
    """
    Base HTTP client for API testing with enterprise features.
    
    Features:
    - Automatic retry with exponential backoff
    - Request/response logging
    - Session management
    - Response time tracking
    - Error handling
    """
    
    def __init__(
        self,
        base_url: Optional[str] = None,
        timeout: Optional[int] = None,
        verify_ssl: bool = True
    ):
        """
        Initialize the API client.
        
        Args:
            base_url: Base URL for API
            timeout: Request timeout in seconds
            verify_ssl: Whether to verify SSL certificates
        """
        self.base_url = base_url or settings.api_base_url
        self.timeout = timeout or settings.api_timeout
        self.verify_ssl = verify_ssl
        self.session = self._create_session()
        self._default_headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    
    def _create_session(self) -> requests.Session:
        """
        Create and configure requests session with retry strategy.
        
        Returns:
            Configured requests.Session
        """
        session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = URLRetry(
            total=settings.api_retry_count,
            backoff_factor=settings.api_retry_delay,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST", "PUT", "PATCH", "DELETE"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        return session
    
    def _build_url(self, endpoint: str) -> str:
        """
        Build full URL from base and endpoint.
        
        Args:
            endpoint: API endpoint path
            
        Returns:
            Full URL
        """
        base = self.base_url.rstrip("/")
        endpoint = endpoint.lstrip("/")
        return f"{base}/{endpoint}"
    
    def _prepare_headers(
        self,
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, str]:
        """
        Prepare request headers.
        
        Args:
            headers: Additional headers
            
        Returns:
            Merged headers dictionary
        """
        prepared_headers = self._default_headers.copy()
        if headers:
            prepared_headers.update(headers)
        return prepared_headers
    
    def request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        data: Optional[Union[str, Dict[str, Any]]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
        **kwargs: Any
    ) -> APIResponse:
        """
        Make HTTP request with logging and error handling.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE, etc.)
            endpoint: API endpoint
            params: URL parameters
            json_data: JSON request body
            data: Form data or raw body
            headers: Request headers
            timeout: Request timeout
            **kwargs: Additional requests arguments
            
        Returns:
            APIResponse object
        """
        url = self._build_url(endpoint)
        prepared_headers = self._prepare_headers(headers)
        timeout = timeout or self.timeout
        
        # Log request
        if settings.enable_logging:
            logger.log_request(method, url, prepared_headers, json_data or data)
        
        # Make request and track time
        start_time = time.time()
        try:
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                json=json_data,
                data=data,
                headers=prepared_headers,
                timeout=timeout,
                verify=self.verify_ssl,
                **kwargs
            )
            elapsed = time.time() - start_time
            
            # Log response
            if settings.enable_logging:
                logger.log_response(
                    response.status_code,
                    elapsed,
                    response.headers,
                    response.json() if response.text else None
                )
            
            return APIResponse(response, elapsed)
            
        except requests.exceptions.Timeout:
            elapsed = time.time() - start_time
            logger.error(f"Request timeout after {elapsed:.2f}s: {method} {url}")
            raise
        except requests.exceptions.RequestException as e:
            elapsed = time.time() - start_time
            logger.error(f"Request failed after {elapsed:.2f}s: {method} {url} - {str(e)}")
            raise
    
    def get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        **kwargs: Any
    ) -> APIResponse:
        """
        Make GET request.
        
        Args:
            endpoint: API endpoint
            params: URL parameters
            **kwargs: Additional request arguments
            
        Returns:
            APIResponse object
        """
        return self.request("GET", endpoint, params=params, **kwargs)
    
    def post(
        self,
        endpoint: str,
        json_data: Optional[Dict[str, Any]] = None,
        data: Optional[Union[str, Dict[str, Any]]] = None,
        **kwargs: Any
    ) -> APIResponse:
        """
        Make POST request.
        
        Args:
            endpoint: API endpoint
            json_data: JSON request body
            data: Form data or raw body
            **kwargs: Additional request arguments
            
        Returns:
            APIResponse object
        """
        return self.request("POST", endpoint, json_data=json_data, data=data, **kwargs)
    
    def put(
        self,
        endpoint: str,
        json_data: Optional[Dict[str, Any]] = None,
        **kwargs: Any
    ) -> APIResponse:
        """
        Make PUT request.
        
        Args:
            endpoint: API endpoint
            json_data: JSON request body
            **kwargs: Additional request arguments
            
        Returns:
            APIResponse object
        """
        return self.request("PUT", endpoint, json_data=json_data, **kwargs)
    
    def patch(
        self,
        endpoint: str,
        json_data: Optional[Dict[str, Any]] = None,
        **kwargs: Any
    ) -> APIResponse:
        """
        Make PATCH request.
        
        Args:
            endpoint: API endpoint
            json_data: JSON request body
            **kwargs: Additional request arguments
            
        Returns:
            APIResponse object
        """
        return self.request("PATCH", endpoint, json_data=json_data, **kwargs)
    
    def delete(
        self,
        endpoint: str,
        **kwargs: Any
    ) -> APIResponse:
        """
        Make DELETE request.
        
        Args:
            endpoint: API endpoint
            **kwargs: Additional request arguments
            
        Returns:
            APIResponse object
        """
        return self.request("DELETE", endpoint, **kwargs)
    
    def set_auth_token(self, token: str) -> None:
        """
        Set authentication token in default headers.
        
        Args:
            token: Bearer token
        """
        self._default_headers["Authorization"] = f"Bearer {token}"
        logger.info("Authentication token set")
    
    def clear_auth_token(self) -> None:
        """Remove authentication token from headers."""
        if "Authorization" in self._default_headers:
            del self._default_headers["Authorization"]
            logger.info("Authentication token cleared")
    
    def close(self) -> None:
        """Close the session."""
        self.session.close()
        logger.debug("API client session closed")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
