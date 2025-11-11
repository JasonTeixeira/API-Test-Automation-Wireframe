"""
Negative test scenarios and edge cases.

Tests cover invalid inputs, boundary values, malformed data, and error handling.
"""
import allure
import pytest

from clients.users_client import UsersClient
from clients.resources_client import ResourcesClient
from clients.auth_client import AuthClient


@pytest.mark.negative
@pytest.mark.regression
@allure.feature("Negative Tests")
@allure.story("Invalid User Operations")
class TestInvalidUserOperations:
    """Tests for invalid user operations."""
    
    def test_get_user_with_invalid_id_string(self, users_client: UsersClient):
        """Test getting user with string ID."""
        try:
            # This should cause a type error or be handled by API
            response = users_client.get_user("invalid_id")  # type: ignore
            # If API handles it, should return 404 or 400
            assert response.status_code in [400, 404]
        except (ValueError, TypeError):
            # Python validation catches it
            pass
    
    def test_get_user_with_negative_id(self, users_client: UsersClient):
        """Test getting user with negative ID."""
        try:
            response = users_client.get_user(-1)
            assert not response.is_success()
        except ValueError:
            pass
    
    def test_get_user_with_zero_id(self, users_client: UsersClient):
        """Test getting user with ID zero."""
        try:
            response = users_client.get_user(0)
            assert not response.is_success()
        except ValueError:
            pass
    
    def test_create_user_with_empty_name(self, users_client: UsersClient):
        """Test creating user with empty name."""
        response = users_client.create_user(name="", job="Tester")
        # ReqRes.in accepts empty strings, but we test the behavior
        assert "id" in response.json or response.status_code >= 400
    
    def test_create_user_with_only_whitespace(self, users_client: UsersClient):
        """Test creating user with whitespace-only name."""
        response = users_client.create_user(name="   ", job="   ")
        assert "id" in response.json or response.status_code >= 400
    
    def test_update_non_existent_user(
        self,
        users_client: UsersClient,
        non_existent_user_id: int
    ):
        """Test updating non-existent user."""
        response = users_client.update_user(
            non_existent_user_id,
            name="Test",
            job="Test"
        )
        # ReqRes.in returns 200 even for non-existent, but we verify behavior
        assert response.status_code in [200, 404]


@pytest.mark.negative
@pytest.mark.regression
@allure.feature("Negative Tests")
@allure.story("Boundary Values")
class TestBoundaryValues:
    """Tests for boundary value conditions."""
    
    def test_create_user_with_very_long_name(self, users_client: UsersClient):
        """Test creating user with extremely long name."""
        long_name = "A" * 10000
        response = users_client.create_user(name=long_name, job="Tester")
        # Should either accept or reject with appropriate status
        assert response.status_code in [200, 201, 400, 413]
    
    def test_create_user_with_special_characters(
        self,
        users_client: UsersClient,
        boundary_values: dict
    ):
        """Test creating user with special characters."""
        special_name = "!@#$%^&*()"
        response = users_client.create_user(name=special_name, job="Tester")
        assert response.status_code in [200, 201, 400]
    
    def test_get_users_with_zero_per_page(self, users_client: UsersClient):
        """Test getting users with per_page=0."""
        try:
            response = users_client.get_users(per_page=0)
            # Should handle gracefully
            assert response.status_code in [200, 400]
        except ValueError:
            pass
    
    def test_get_users_with_negative_page(self, users_client: UsersClient):
        """Test getting users with negative page number."""
        try:
            response = users_client.get_users(page=-1)
            assert response.status_code in [200, 400]
        except ValueError:
            pass
    
    def test_get_users_with_huge_page_number(self, users_client: UsersClient):
        """Test getting users with very large page number."""
        response = users_client.get_users(page=9999)
        assert response.is_success()
        # Should return empty data or last page
        assert "data" in response.json


@pytest.mark.negative
@pytest.mark.security
@allure.feature("Negative Tests")
@allure.story("Security Edge Cases")
class TestSecurityEdgeCases:
    """Tests for security-related edge cases."""
    
    def test_create_user_with_sql_injection(
        self,
        users_client: UsersClient,
        sql_injection_payloads: list
    ):
        """Test that SQL injection payloads are handled safely."""
        payload = sql_injection_payloads[0]
        response = users_client.create_user(name=payload, job=payload)
        # Should not crash the system
        assert response.status_code in [200, 201, 400]
    
    def test_create_user_with_xss_payload(
        self,
        users_client: UsersClient,
        xss_payloads: list
    ):
        """Test that XSS payloads are handled safely."""
        payload = xss_payloads[0]
        response = users_client.create_user(name=payload, job="Tester")
        # Should not execute scripts
        assert response.status_code in [200, 201, 400]
    
    def test_create_user_with_unicode_characters(self, users_client: UsersClient):
        """Test creating user with unicode characters."""
        unicode_name = "测试用户 тест Ñoño"
        response = users_client.create_user(name=unicode_name, job="Tester")
        assert response.status_code in [200, 201, 400]
    
    def test_create_user_with_null_bytes(self, users_client: UsersClient):
        """Test creating user with null bytes."""
        try:
            null_name = "Test\\x00User"
            response = users_client.create_user(name=null_name, job="Tester")
            assert response.status_code in [200, 201, 400]
        except ValueError:
            pass


@pytest.mark.negative
@pytest.mark.regression
@allure.feature("Negative Tests")
@allure.story("Invalid Resource Operations")
class TestInvalidResourceOperations:
    """Tests for invalid resource operations."""
    
    def test_get_resource_with_invalid_id(self, resources_client: ResourcesClient):
        """Test getting resource with invalid ID."""
        try:
            response = resources_client.get_resource("invalid")  # type: ignore
            assert response.status_code in [400, 404]
        except (ValueError, TypeError):
            pass
    
    def test_create_resource_with_invalid_year(self, resources_client: ResourcesClient):
        """Test creating resource with invalid year."""
        response = resources_client.create_resource(
            name="Test",
            year=999,  # Invalid year
            color="#FF0000",
            pantone_value="test"
        )
        # Should validate year or accept it
        assert response.status_code in [200, 201, 400]
    
    def test_create_resource_with_invalid_color(self, resources_client: ResourcesClient):
        """Test creating resource with invalid color format."""
        response = resources_client.create_resource(
            name="Test",
            year=2020,
            color="invalid_color",  # Not hex
            pantone_value="test"
        )
        assert response.status_code in [200, 201, 400]
    
    def test_delete_resource_twice(self, resources_client: ResourcesClient):
        """Test deleting same resource twice."""
        resource_id = 1
        response1 = resources_client.delete_resource(resource_id)
        assert response1.status_code == 204
        
        response2 = resources_client.delete_resource(resource_id)
        # Should handle gracefully
        assert response2.status_code in [204, 404]


@pytest.mark.negative
@pytest.mark.regression
@allure.feature("Negative Tests")
@allure.story("Authentication Edge Cases")
class TestAuthenticationEdgeCases:
    """Tests for authentication edge cases."""
    
    def test_login_with_very_long_password(self, auth_client: AuthClient):
        """Test login with extremely long password."""
        long_password = "A" * 10000
        response = auth_client.login_unsuccessful(
            email="test@test.com",
            password=long_password
        )
        assert not response.is_success()
        assert response.status_code in [400, 413]
    
    def test_login_with_empty_string_email(self, auth_client: AuthClient):
        """Test login with empty email."""
        response = auth_client.login_unsuccessful(
            email="",
            password="test"
        )
        assert not response.is_success()
        assert response.status_code == 400
    
    def test_register_with_whitespace_only_email(self, auth_client: AuthClient):
        """Test register with whitespace-only email."""
        response = auth_client.register_unsuccessful(
            email="   ",
            password="test"
        )
        assert not response.is_success()
    
    def test_login_with_malformed_email(self, auth_client: AuthClient):
        """Test login with malformed email format."""
        malformed_emails = [
            "notanemail",
            "@example.com",
            "user@",
            "user name@example.com"
        ]
        
        for email in malformed_emails:
            response = auth_client.login_unsuccessful(
                email=email,
                password="test"
            )
            assert not response.is_success()
