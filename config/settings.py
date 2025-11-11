"""
Configuration management for API test automation framework.

Uses Pydantic Settings for type-safe configuration with environment variable support.
"""
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables or .env file.
    
    All settings have sensible defaults and can be overridden via environment variables.
    """
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_ignore_empty=True,
        case_sensitive=False,
        extra="ignore",
    )
    
    # API Configuration
    api_base_url: str = Field(
        default="https://reqres.in/api",
        description="Base URL for the API under test"
    )
    api_timeout: int = Field(
        default=30,
        ge=1,
        le=300,
        description="Request timeout in seconds"
    )
    api_retry_count: int = Field(
        default=3,
        ge=0,
        le=10,
        description="Number of retry attempts for failed requests"
    )
    api_retry_delay: float = Field(
        default=1.0,
        ge=0.1,
        le=10.0,
        description="Delay between retries in seconds"
    )
    
    # Test Environment
    test_env: str = Field(
        default="staging",
        description="Test environment (dev, staging, prod)"
    )
    log_level: str = Field(
        default="INFO",
        description="Logging level (DEBUG, INFO, WARNING, ERROR)"
    )
    enable_logging: bool = Field(
        default=True,
        description="Enable/disable request/response logging"
    )
    
    # Authentication
    api_username: Optional[str] = Field(
        default=None,
        description="API username for authentication"
    )
    api_password: Optional[str] = Field(
        default=None,
        description="API password for authentication"
    )
    api_token: Optional[str] = Field(
        default=None,
        description="API bearer token for authentication"
    )
    
    # Test Execution
    parallel_workers: int = Field(
        default=4,
        ge=1,
        le=16,
        description="Number of parallel workers for test execution"
    )
    slow_test_threshold: float = Field(
        default=5.0,
        ge=0.1,
        description="Threshold in seconds to mark a test as slow"
    )
    
    # Reporting
    allure_results_dir: str = Field(
        default="reports/allure-results",
        description="Directory for Allure test results"
    )
    html_report_dir: str = Field(
        default="reports/html",
        description="Directory for HTML test reports"
    )
    
    # Performance Testing
    performance_threshold_ms: int = Field(
        default=1000,
        ge=1,
        description="Performance threshold in milliseconds"
    )
    enable_performance_tests: bool = Field(
        default=False,
        description="Enable/disable performance tests"
    )
    
    def get_full_url(self, endpoint: str) -> str:
        """
        Construct full URL from base URL and endpoint.
        
        Args:
            endpoint: API endpoint path
            
        Returns:
            Full URL with proper formatting
        """
        base = self.api_base_url.rstrip("/")
        endpoint = endpoint.lstrip("/")
        return f"{base}/{endpoint}"
    
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.test_env.lower() == "prod"
    
    def is_debug_mode(self) -> bool:
        """Check if debug logging is enabled."""
        return self.log_level.upper() == "DEBUG"


# Global settings instance
settings = Settings()
