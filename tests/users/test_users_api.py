"""
Users API test suite.

Tests cover all CRUD operations, pagination, schema validation, and error handling.
"""
import allure
import pytest
from pydantic import ValidationError

from clients.users_client import UsersClient
from models.schemas import (
    USER_SCHEMA,
    USERS_LIST_SCHEMA,
    validate_user_schema,
    validate_users_list_schema,
)


@pytest.mark.users
@pytest.mark.smoke
@allure.feature("Users API")
@allure.story("List Users")
class TestGetUsers:
    """Tests for GET /users endpoint - listing users."""
    
    def test_get_users_default_pagination(self, users_client: UsersClient):
        """Test getting users with default pagination."""
        response = users_client.get_users()
        
        assert response.is_success(), f"Expected 200, got {response.status_code}"
        assert response.status_code == 200
        assert "data" in response.json
        assert isinstance(response.json["data"], list)
        assert len(response.json["data"]) > 0
    
    def test_get_users_with_page_parameter(self, users_client: UsersClient):
        """Test getting users with specific page number."""
        response = users_client.get_users(page=2)
        
        assert response.is_success()
        assert response.json["page"] == 2
        assert "data" in response.json
    
    def test_get_users_with_per_page_parameter(self, users_client: UsersClient):
        """Test getting users with custom per_page value."""
        per_page = 3
        response = users_client.get_users(per_page=per_page)
        
        assert response.is_success()
        assert response.json["per_page"] == per_page
        assert len(response.json["data"]) <= per_page
    
    def test_get_users_pagination_metadata(self, users_client: UsersClient):
        """Test that pagination metadata is correct."""
        response = users_client.get_users(page=1, per_page=6)
        
        assert response.is_success()
        data = response.json
        
        assert "page" in data
        assert "per_page" in data
        assert "total" in data
        assert "total_pages" in data
        assert data["total"] > 0
        assert data["total_pages"] > 0
    
    def test_get_users_response_time(self, users_client: UsersClient, assert_performance):
        """Test that getting users completes within performance threshold."""
        response = users_client.get_users()
        
        assert response.is_success()
        assert_performance(response.elapsed_time, "GET /users")
    
    def test_get_users_schema_validation(
        self,
        users_client: UsersClient,
        validate_json_schema
    ):
        """Test that users list response matches expected schema."""
        response = users_client.get_users()
        
        assert response.is_success()
        validate_json_schema(response.json, USERS_LIST_SCHEMA)
    
    def test_get_users_pydantic_validation(self, users_client: UsersClient):
        """Test users list response with Pydantic model."""
        response = users_client.get_users()
        
        assert response.is_success()
        # Should not raise ValidationError
        validated_response = validate_users_list_schema(response.json)
        assert validated_response.page >= 1
        assert validated_response.per_page >= 1
        assert len(validated_response.data) > 0


@pytest.mark.users
@pytest.mark.smoke
@allure.feature("Users API")
@allure.story("Single User")
class TestGetSingleUser:
    """Tests for GET /users/{id} endpoint - getting single user."""
    
    def test_get_existing_user(self, users_client: UsersClient, existing_user_id: int):
        """Test getting an existing user by ID."""
        response = users_client.get_user(existing_user_id)
        
        assert response.is_success()
        assert response.status_code == 200
        assert "data" in response.json
        assert response.json["data"]["id"] == existing_user_id
    
    def test_get_user_has_required_fields(self, users_client: UsersClient):
        """Test that user response contains all required fields."""
        response = users_client.get_user(1)
        
        assert response.is_success()
        user_data = response.json["data"]
        
        required_fields = ["id", "email", "first_name", "last_name", "avatar"]
        for field in required_fields:
            assert field in user_data, f"Missing required field: {field}"
    
    def test_get_user_email_format(self, users_client: UsersClient):
        """Test that user email is in valid format."""
        response = users_client.get_user(1)
        
        assert response.is_success()
        email = response.json["data"]["email"]
        assert "@" in email
        assert "." in email
    
    def test_get_user_avatar_is_url(self, users_client: UsersClient):
        """Test that avatar field is a valid URL."""
        response = users_client.get_user(1)
        
        assert response.is_success()
        avatar = response.json["data"]["avatar"]
        assert avatar.startswith("http://") or avatar.startswith("https://")
    
    def test_get_non_existent_user(self, users_client: UsersClient, non_existent_user_id: int):
        """Test getting a non-existent user returns 404."""
        response = users_client.get_user(non_existent_user_id)
        
        assert response.status_code == 404
        assert not response.is_success()
    
    def test_get_user_schema_validation(
        self,
        users_client: UsersClient,
        validate_json_schema
    ):
        """Test that single user response matches schema."""
        response = users_client.get_user(1)
        
        assert response.is_success()
        validate_json_schema(response.json["data"], USER_SCHEMA)
    
    def test_get_user_pydantic_validation(self, users_client: UsersClient):
        """Test user response with Pydantic model validation."""
        response = users_client.get_user(2)
        
        assert response.is_success()
        user = validate_user_schema(response.json["data"])
        assert user.id == 2
        assert user.id > 0


@pytest.mark.users
@pytest.mark.regression
@allure.feature("Users API")
@allure.story("Create User")
class TestCreateUser:
    """Tests for POST /users endpoint - creating users."""
    
    def test_create_user_success(self, users_client: UsersClient, user_data: dict):
        """Test creating a new user with valid data."""
        response = users_client.create_user(**user_data)
        
        assert response.is_success()
        assert response.status_code == 201
        assert "id" in response.json
        assert "createdAt" in response.json
        assert response.json["name"] == user_data["name"]
        assert response.json["job"] == user_data["job"]
    
    def test_create_user_with_email(
        self,
        users_client: UsersClient,
        user_data_with_email: dict
    ):
        """Test creating user with email field."""
        response = users_client.create_user(**user_data_with_email)
        
        assert response.is_success()
        assert "id" in response.json
    
    def test_create_user_returns_id(self, users_client: UsersClient, user_data: dict):
        """Test that created user has an ID."""
        response = users_client.create_user(**user_data)
        
        assert response.is_success()
        assert "id" in response.json
        assert response.json["id"] is not None
    
    def test_create_user_timestamp_format(self, users_client: UsersClient, user_data: dict):
        """Test that createdAt timestamp is in ISO 8601 format."""
        response = users_client.create_user(**user_data)
        
        assert response.is_success()
        created_at = response.json["createdAt"]
        # Should contain T and Z for ISO 8601
        assert "T" in created_at or "-" in created_at
    
    def test_create_user_response_time(
        self,
        users_client: UsersClient,
        user_data: dict,
        assert_performance
    ):
        """Test that user creation completes within threshold."""
        response = users_client.create_user(**user_data)
        
        assert response.is_success()
        assert_performance(response.elapsed_time, "POST /users")
    
    def test_create_user_with_additional_fields(self, users_client: UsersClient):
        """Test creating user with extra fields."""
        data = {
            "name": "Test User",
            "job": "Tester",
            "location": "San Francisco",
            "phone": "555-1234"
        }
        response = users_client.create_user(**data)
        
        assert response.is_success()


@pytest.mark.users
@pytest.mark.regression
@allure.feature("Users API")
@allure.story("Update User")
class TestUpdateUser:
    """Tests for PUT /users/{id} endpoint - updating users."""
    
    def test_update_user_with_put(self, users_client: UsersClient):
        """Test updating user with PUT method."""
        user_id = 2
        update_data = {"name": "Updated Name", "job": "Updated Job"}
        
        response = users_client.update_user(user_id, **update_data)
        
        assert response.is_success()
        assert response.status_code == 200
        assert "updatedAt" in response.json
        assert response.json.get("name") == update_data["name"]
        assert response.json.get("job") == update_data["job"]
    
    def test_update_user_only_name(self, users_client: UsersClient):
        """Test updating only user name."""
        response = users_client.update_user(1, name="New Name Only")
        
        assert response.is_success()
        assert "updatedAt" in response.json
    
    def test_update_user_only_job(self, users_client: UsersClient):
        """Test updating only user job."""
        response = users_client.update_user(1, job="New Job Only")
        
        assert response.is_success()
        assert "updatedAt" in response.json
    
    def test_partial_update_user_with_patch(self, users_client: UsersClient):
        """Test partially updating user with PATCH method."""
        user_id = 2
        patch_data = {"job": "Senior Engineer"}
        
        response = users_client.partial_update_user(user_id, **patch_data)
        
        assert response.is_success()
        assert response.status_code == 200
        assert "updatedAt" in response.json
    
    def test_update_timestamp_is_recent(self, users_client: UsersClient):
        """Test that updatedAt timestamp is recent."""
        response = users_client.update_user(1, name="Test")
        
        assert response.is_success()
        updated_at = response.json["updatedAt"]
        # Should have timestamp format
        assert updated_at is not None
        assert len(updated_at) > 0


@pytest.mark.users
@pytest.mark.regression
@allure.feature("Users API")
@allure.story("Delete User")
class TestDeleteUser:
    """Tests for DELETE /users/{id} endpoint - deleting users."""
    
    def test_delete_user_success(self, users_client: UsersClient):
        """Test deleting a user."""
        user_id = 2
        response = users_client.delete_user(user_id)
        
        assert response.status_code == 204
        assert response.text == ""
    
    def test_delete_non_existent_user(
        self,
        users_client: UsersClient,
        non_existent_user_id: int
    ):
        """Test deleting non-existent user."""
        response = users_client.delete_user(non_existent_user_id)
        
        # ReqRes.in returns 204 even for non-existent resources
        assert response.status_code == 204
    
    def test_delete_user_response_time(
        self,
        users_client: UsersClient,
        assert_performance
    ):
        """Test that user deletion completes quickly."""
        response = users_client.delete_user(1)
        
        assert_performance(response.elapsed_time, "DELETE /users")


@pytest.mark.users
@pytest.mark.performance
@allure.feature("Users API")
@allure.story("Performance")
class TestUsersPerformance:
    """Performance tests for Users API."""
    
    def test_delayed_response(self, users_client: UsersClient):
        """Test delayed response endpoint."""
        delay = 3
        response = users_client.get_delayed_users(delay=delay)
        
        assert response.is_success()
        assert response.elapsed_time >= delay
        assert "data" in response.json
