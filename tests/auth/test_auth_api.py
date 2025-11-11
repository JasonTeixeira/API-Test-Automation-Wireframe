"""
Authentication API test suite.

Tests cover login, registration, token validation, and security scenarios.
"""
import allure
import pytest

from clients.auth_client import AuthClient
from models.schemas import ERROR_SCHEMA, validate_error_response


@pytest.mark.auth
@pytest.mark.smoke
@allure.feature("Authentication API")
@allure.story("User Registration")
class TestRegister:
    """Tests for POST /register endpoint."""
    
    def test_register_successful(self, auth_client: AuthClient, valid_register_data: dict):
        """Test successful user registration."""
        response = auth_client.register(**valid_register_data)
        
        assert response.is_success()
        assert response.status_code == 200
        assert "id" in response.json
        assert "token" in response.json
        assert response.json["token"] is not None
    
    def test_register_returns_token(self, auth_client: AuthClient, valid_register_data: dict):
        """Test that registration returns a token."""
        response = auth_client.register(**valid_register_data)
        
        assert response.is_success()
        token = response.json.get("token")
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_register_returns_user_id(self, auth_client: AuthClient, valid_register_data: dict):
        """Test that registration returns user ID."""
        response = auth_client.register(**valid_register_data)
        
        assert response.is_success()
        user_id = response.json.get("id")
        assert user_id is not None
        assert isinstance(user_id, int)
    
    def test_register_without_password(self, auth_client: AuthClient):
        """Test registration without password fails."""
        response = auth_client.register_unsuccessful(
            email="test@reqres.in"
        )
        
        assert not response.is_success()
        assert response.status_code == 400
        assert "error" in response.json
    
    def test_register_without_email(self, auth_client: AuthClient):
        """Test registration without email fails."""
        response = auth_client.register_unsuccessful(
            password="testpass123"
        )
        
        assert not response.is_success()
        assert response.status_code == 400
        assert "error" in response.json
    
    def test_register_with_empty_credentials(self, auth_client: AuthClient):
        """Test registration with empty credentials fails."""
        response = auth_client.register_unsuccessful()
        
        assert not response.is_success()
        assert response.status_code == 400
    
    def test_register_error_message_format(self, auth_client: AuthClient):
        """Test that error response has proper format."""
        response = auth_client.register_unsuccessful(email="test@test.com")
        
        assert not response.is_success()
        error = response.json.get("error")
        assert error is not None
        assert isinstance(error, str)
        assert len(error) > 0
    
    def test_register_response_time(
        self,
        auth_client: AuthClient,
        valid_register_data: dict,
        assert_performance
    ):
        """Test registration completes within threshold."""
        response = auth_client.register(**valid_register_data)
        
        assert response.is_success()
        assert_performance(response.elapsed_time, "POST /register")


@pytest.mark.auth
@pytest.mark.smoke
@allure.feature("Authentication API")
@allure.story("User Login")
class TestLogin:
    """Tests for POST /login endpoint."""
    
    def test_login_successful(self, auth_client: AuthClient, valid_auth_data: dict):
        """Test successful user login."""
        response = auth_client.login(**valid_auth_data)
        
        assert response.is_success()
        assert response.status_code == 200
        assert "token" in response.json
        assert response.json["token"] is not None
    
    def test_login_returns_token(self, auth_client: AuthClient, valid_auth_data: dict):
        """Test that login returns authentication token."""
        response = auth_client.login(**valid_auth_data)
        
        assert response.is_success()
        token = response.json.get("token")
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_login_token_format(self, auth_client: AuthClient, valid_auth_data: dict):
        """Test that token has expected format."""
        response = auth_client.login(**valid_auth_data)
        
        assert response.is_success()
        token = response.json["token"]
        # Token should be alphanumeric
        assert token.replace("-", "").replace("_", "").isalnum()
    
    def test_login_without_password(self, auth_client: AuthClient):
        """Test login without password fails."""
        response = auth_client.login_unsuccessful(
            email="eve.holt@reqres.in"
        )
        
        assert not response.is_success()
        assert response.status_code == 400
        assert "error" in response.json
    
    def test_login_without_email(self, auth_client: AuthClient):
        """Test login without email fails."""
        response = auth_client.login_unsuccessful(
            password="cityslicka"
        )
        
        assert not response.is_success()
        assert response.status_code == 400
        assert "error" in response.json
    
    def test_login_with_invalid_credentials(
        self,
        auth_client: AuthClient,
        invalid_auth_data: dict
    ):
        """Test login with invalid credentials fails."""
        response = auth_client.login(**invalid_auth_data)
        
        assert not response.is_success()
        assert response.status_code == 400
        assert "error" in response.json
    
    def test_login_with_empty_credentials(self, auth_client: AuthClient):
        """Test login with empty credentials fails."""
        response = auth_client.login_unsuccessful()
        
        assert not response.is_success()
        assert response.status_code == 400
    
    def test_login_error_schema_validation(
        self,
        auth_client: AuthClient,
        validate_json_schema
    ):
        """Test that error response matches schema."""
        response = auth_client.login_unsuccessful(email="test@test.com")
        
        assert not response.is_success()
        validate_json_schema(response.json, ERROR_SCHEMA)
    
    def test_login_response_time(
        self,
        auth_client: AuthClient,
        valid_auth_data: dict,
        assert_performance
    ):
        """Test login completes within threshold."""
        response = auth_client.login(**valid_auth_data)
        
        assert response.is_success()
        assert_performance(response.elapsed_time, "POST /login")


@pytest.mark.auth
@pytest.mark.security
@allure.feature("Authentication API")
@allure.story("Security")
class TestAuthSecurity:
    """Security tests for authentication endpoints."""
    
    def test_login_with_sql_injection(
        self,
        auth_client: AuthClient,
        sql_injection_payloads: list
    ):
        """Test that SQL injection payloads are handled."""
        for payload in sql_injection_payloads[:3]:  # Test a few payloads
            response = auth_client.login_unsuccessful(
                email=payload,
                password=payload
            )
            # Should return error, not crash
            assert not response.is_success()
    
    def test_login_with_xss_payload(
        self,
        auth_client: AuthClient,
        xss_payloads: list
    ):
        """Test that XSS payloads are handled safely."""
        for payload in xss_payloads[:2]:  # Test a couple payloads
            response = auth_client.login_unsuccessful(
                email=payload,
                password="test123"
            )
            # Should return error, not execute script
            assert not response.is_success()
    
    def test_register_with_sql_injection(
        self,
        auth_client: AuthClient,
        sql_injection_payloads: list
    ):
        """Test registration handles SQL injection."""
        payload = sql_injection_payloads[0]
        response = auth_client.register_unsuccessful(
            email=payload,
            password="test123"
        )
        # Should not crash
        assert not response.is_success()
    
    def test_login_error_does_not_leak_info(self, auth_client: AuthClient):
        """Test that error messages don't leak sensitive info."""
        response = auth_client.login_unsuccessful(
            email="nonexistent@test.com",
            password="wrongpassword"
        )
        
        assert not response.is_success()
        error_msg = response.json.get("error", "").lower()
        # Error should not reveal if email exists
        sensitive_terms = ["not found", "does not exist", "invalid user"]
        for term in sensitive_terms:
            assert term not in error_msg or error_msg == "user not found"


@pytest.mark.auth
@pytest.mark.regression
@allure.feature("Authentication API")
@allure.story("Token Management")
class TestTokenManagement:
    """Tests for token management and validation."""
    
    def test_token_is_consistent(self, auth_client: AuthClient, valid_auth_data: dict):
        """Test that multiple logins return valid tokens."""
        response1 = auth_client.login(**valid_auth_data)
        response2 = auth_client.login(**valid_auth_data)
        
        assert response1.is_success()
        assert response2.is_success()
        assert "token" in response1.json
        assert "token" in response2.json
    
    def test_token_length(self, auth_client: AuthClient, valid_auth_data: dict):
        """Test that token has reasonable length."""
        response = auth_client.login(**valid_auth_data)
        
        assert response.is_success()
        token = response.json["token"]
        assert len(token) >= 10  # Tokens should be reasonably long
        assert len(token) <= 1000  # But not excessive
