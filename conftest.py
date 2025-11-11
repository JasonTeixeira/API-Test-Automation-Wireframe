"""
Pytest configuration and fixtures for API test automation.

Provides reusable fixtures for API clients, test data, and test utilities.
"""
import json
from typing import Any, Dict, Generator

import allure
import pytest
from _pytest.nodes import Item
from _pytest.runner import CallInfo

from clients.auth_client import AuthClient
from clients.resources_client import ResourcesClient
from clients.users_client import UsersClient
from config.settings import settings
from utils.logger import logger
from utils.test_data import test_data


# ============================================================================
# Session-scoped fixtures
# ============================================================================

@pytest.fixture(scope="session")
def api_base_url() -> str:
    """
    Get API base URL from settings.
    
    Returns:
        Base URL for API
    """
    return settings.api_base_url


# ============================================================================
# Function-scoped API client fixtures
# ============================================================================

@pytest.fixture
def users_client() -> Generator[UsersClient, None, None]:
    """
    Provide Users API client.
    
    Yields:
        UsersClient instance
    """
    client = UsersClient()
    yield client
    client.close()


@pytest.fixture
def resources_client() -> Generator[ResourcesClient, None, None]:
    """
    Provide Resources API client.
    
    Yields:
        ResourcesClient instance
    """
    client = ResourcesClient()
    yield client
    client.close()


@pytest.fixture
def auth_client() -> Generator[AuthClient, None, None]:
    """
    Provide Auth API client.
    
    Yields:
        AuthClient instance
    """
    client = AuthClient()
    yield client
    client.close()


# ============================================================================
# Test data fixtures
# ============================================================================

@pytest.fixture
def user_data() -> Dict[str, str]:
    """
    Generate random user data.
    
    Returns:
        Dictionary with name and job
    """
    return test_data.generate_user_data()


@pytest.fixture
def user_data_with_email() -> Dict[str, str]:
    """
    Generate random user data with email.
    
    Returns:
        Dictionary with name, job, and email
    """
    return test_data.generate_user_data(include_email=True)


@pytest.fixture
def full_user_data() -> Dict[str, str]:
    """
    Generate complete user profile data.
    
    Returns:
        Dictionary with all user fields
    """
    return test_data.generate_user_data_full()


@pytest.fixture
def resource_data() -> Dict[str, Any]:
    """
    Generate random resource data.
    
    Returns:
        Dictionary with resource fields
    """
    return test_data.generate_resource_data()


@pytest.fixture
def valid_auth_data() -> Dict[str, str]:
    """
    Generate valid authentication data.
    
    Returns:
        Dictionary with email and password
    """
    return test_data.generate_auth_data(valid=True)


@pytest.fixture
def invalid_auth_data() -> Dict[str, str]:
    """
    Generate invalid authentication data.
    
    Returns:
        Dictionary with invalid credentials
    """
    return test_data.generate_auth_data(valid=False)


@pytest.fixture
def valid_register_data() -> Dict[str, str]:
    """
    Generate valid registration data.
    
    Returns:
        Dictionary with email and password
    """
    return test_data.generate_register_data(valid=True)


@pytest.fixture
def invalid_register_data() -> Dict[str, str]:
    """
    Generate invalid registration data.
    
    Returns:
        Dictionary with incomplete registration data
    """
    return test_data.generate_register_data(valid=False)


@pytest.fixture
def bulk_users_data() -> list:
    """
    Generate bulk user data for testing.
    
    Returns:
        List of user dictionaries
    """
    return test_data.generate_bulk_users(count=10)


@pytest.fixture
def sql_injection_payloads() -> list:
    """
    Generate SQL injection test payloads.
    
    Returns:
        List of SQL injection strings
    """
    return test_data.generate_sql_injection_payloads()


@pytest.fixture
def xss_payloads() -> list:
    """
    Generate XSS test payloads.
    
    Returns:
        List of XSS strings
    """
    return test_data.generate_xss_payloads()


@pytest.fixture
def boundary_values() -> Dict[str, Any]:
    """
    Generate boundary test values.
    
    Returns:
        Dictionary with boundary values
    """
    return test_data.generate_boundary_values()


# ============================================================================
# Helper fixtures
# ============================================================================

@pytest.fixture
def auth_token(auth_client: AuthClient, valid_auth_data: Dict[str, str]) -> str:
    """
    Get authentication token by logging in.
    
    Args:
        auth_client: Auth API client
        valid_auth_data: Valid credentials
        
    Returns:
        Authentication token
    """
    response = auth_client.login(**valid_auth_data)
    assert response.is_success(), "Login failed"
    return response.json.get("token")


@pytest.fixture
def created_user(users_client: UsersClient, user_data: Dict[str, str]) -> Dict[str, Any]:
    """
    Create a user for testing (returns user data with ID).
    
    Args:
        users_client: Users API client
        user_data: User data to create
        
    Returns:
        Created user data with ID
    """
    response = users_client.create_user(**user_data)
    assert response.is_success(), "User creation failed"
    return response.json


@pytest.fixture(params=[1, 2])
def existing_user_id(request) -> int:
    """
    Provide existing user IDs for testing.
    
    Yields:
        User ID
    """
    return request.param


@pytest.fixture(params=[1, 2])
def existing_resource_id(request) -> int:
    """
    Provide existing resource IDs for testing.
    
    Yields:
        Resource ID
    """
    return request.param


@pytest.fixture
def non_existent_user_id() -> int:
    """
    Provide a non-existent user ID for negative testing.
    
    Returns:
        Non-existent user ID
    """
    return 99999


@pytest.fixture
def non_existent_resource_id() -> int:
    """
    Provide a non-existent resource ID for negative testing.
    
    Returns:
        Non-existent resource ID
    """
    return 99999


# ============================================================================
# Pytest hooks for logging and reporting
# ============================================================================

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item: Item, call: CallInfo) -> Generator:
    """
    Hook to capture test results and attach to Allure report.
    
    Args:
        item: Test item
        call: Test call info
    """
    outcome = yield
    report = outcome.get_result()
    
    if report.when == "call":
        # Log test result
        test_name = item.nodeid
        if report.passed:
            logger.log_test_end(test_name, "PASSED")
        elif report.failed:
            logger.log_test_end(test_name, "FAILED")
            
            # Attach failure info to Allure
            if hasattr(report, 'longreprtext'):
                allure.attach(
                    report.longreprtext,
                    name="Failure Details",
                    attachment_type=allure.attachment_type.TEXT
                )


def pytest_runtest_setup(item: Item) -> None:
    """
    Hook called before each test.
    
    Args:
        item: Test item
    """
    logger.log_test_start(item.nodeid)
    
    # Attach test info to Allure
    if hasattr(item, 'obj') and hasattr(item.obj, '__doc__'):
        if item.obj.__doc__:
            allure.dynamic.description(item.obj.__doc__)


def pytest_collection_modifyitems(items: list) -> None:
    """
    Modify test collection to add markers and metadata.
    
    Args:
        items: List of collected test items
    """
    for item in items:
        # Add markers based on test path
        if "users" in item.nodeid:
            item.add_marker(pytest.mark.users)
        if "resources" in item.nodeid:
            item.add_marker(pytest.mark.resources)
        if "auth" in item.nodeid:
            item.add_marker(pytest.mark.auth)
        if "workflows" in item.nodeid:
            item.add_marker(pytest.mark.workflows)
        if "negative" in item.nodeid:
            item.add_marker(pytest.mark.negative)
        
        # Add Allure labels
        if "smoke" in [mark.name for mark in item.iter_markers()]:
            allure.dynamic.tag("smoke")
            allure.dynamic.severity(allure.severity_level.CRITICAL)


# ============================================================================
# Performance tracking fixtures
# ============================================================================

@pytest.fixture
def performance_threshold() -> float:
    """
    Get performance threshold from settings.
    
    Returns:
        Performance threshold in seconds
    """
    return settings.performance_threshold_ms / 1000.0


@pytest.fixture
def assert_performance(performance_threshold: float):
    """
    Provide performance assertion helper.
    
    Args:
        performance_threshold: Threshold in seconds
        
    Returns:
        Helper function to assert response time
    """
    def _assert_performance(elapsed_time: float, operation: str = "API call") -> None:
        """
        Assert that operation completed within threshold.
        
        Args:
            elapsed_time: Actual elapsed time in seconds
            operation: Operation description
        """
        assert elapsed_time < performance_threshold, (
            f"{operation} took {elapsed_time:.3f}s, "
            f"exceeds threshold of {performance_threshold:.3f}s"
        )
        logger.info(f"✓ {operation} completed in {elapsed_time:.3f}s (within threshold)")
    
    return _assert_performance


# ============================================================================
# JSON Schema validation helper
# ============================================================================

@pytest.fixture
def validate_json_schema():
    """
    Provide JSON schema validation helper.
    
    Returns:
        Helper function to validate JSON against schema
    """
    from jsonschema import validate, ValidationError
    
    def _validate(data: Dict[str, Any], schema: Dict[str, Any]) -> None:
        """
        Validate data against JSON schema.
        
        Args:
            data: Data to validate
            schema: JSON schema
            
        Raises:
            ValidationError: If validation fails
        """
        try:
            validate(instance=data, schema=schema)
            logger.info("✓ JSON schema validation passed")
        except ValidationError as e:
            logger.error(f"✗ JSON schema validation failed: {e.message}")
            raise
    
    return _validate


# ============================================================================
# Allure attachment helpers
# ============================================================================

@pytest.fixture
def attach_request_to_allure():
    """
    Provide helper to attach request details to Allure report.
    
    Returns:
        Helper function
    """
    def _attach(method: str, url: str, **kwargs: Any) -> None:
        """
        Attach request details to Allure.
        
        Args:
            method: HTTP method
            url: Request URL
            **kwargs: Additional request details
        """
        request_info = {
            "method": method,
            "url": url,
            **kwargs
        }
        allure.attach(
            json.dumps(request_info, indent=2),
            name="Request Details",
            attachment_type=allure.attachment_type.JSON
        )
    
    return _attach


@pytest.fixture
def attach_response_to_allure():
    """
    Provide helper to attach response details to Allure report.
    
    Returns:
        Helper function
    """
    def _attach(status_code: int, body: Dict[str, Any], elapsed_time: float) -> None:
        """
        Attach response details to Allure.
        
        Args:
            status_code: HTTP status code
            body: Response body
            elapsed_time: Response time
        """
        response_info = {
            "status_code": status_code,
            "elapsed_time": f"{elapsed_time:.3f}s",
            "body": body
        }
        allure.attach(
            json.dumps(response_info, indent=2),
            name="Response Details",
            attachment_type=allure.attachment_type.JSON
        )
    
    return _attach
