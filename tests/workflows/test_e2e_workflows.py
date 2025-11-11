"""
End-to-end workflow tests.

Tests cover complete user journeys and multi-step operations.
"""
import allure
import pytest

from clients.auth_client import AuthClient
from clients.users_client import UsersClient


@pytest.mark.workflows
@pytest.mark.regression
@allure.feature("Workflows")
@allure.story("User Lifecycle")
class TestUserLifecycleWorkflow:
    """Tests for complete user lifecycle: create -> update -> delete."""
    
    def test_create_update_delete_user_workflow(self, users_client: UsersClient, user_data: dict):
        """Test complete user lifecycle workflow."""
        # Step 1: Create user
        create_response = users_client.create_user(**user_data)
        assert create_response.is_success()
        user_id = create_response.json["id"]
        
        # Step 2: Update user
        update_data = {"name": "Updated Name", "job": "Updated Job"}
        update_response = users_client.update_user(int(user_id), **update_data)
        assert update_response.is_success()
        assert update_response.json.get("name") == update_data["name"]
        
        # Step 3: Delete user
        delete_response = users_client.delete_user(int(user_id))
        assert delete_response.status_code == 204
    
    def test_create_patch_delete_workflow(self, users_client: UsersClient, user_data: dict):
        """Test workflow with PATCH update."""
        # Create
        create_response = users_client.create_user(**user_data)
        assert create_response.is_success()
        user_id = int(create_response.json["id"])
        
        # Patch
        patch_response = users_client.partial_update_user(user_id, job="Patched Job")
        assert patch_response.is_success()
        
        # Delete
        delete_response = users_client.delete_user(user_id)
        assert delete_response.status_code == 204
    
    def test_multiple_users_creation_workflow(
        self,
        users_client: UsersClient,
        bulk_users_data: list
    ):
        """Test creating multiple users in sequence."""
        created_ids = []
        
        for user_data in bulk_users_data[:5]:  # Create 5 users
            response = users_client.create_user(**user_data)
            assert response.is_success()
            created_ids.append(response.json["id"])
        
        assert len(created_ids) == 5
        assert len(set(created_ids)) == 5  # All IDs are unique


@pytest.mark.workflows
@pytest.mark.regression
@allure.feature("Workflows")
@allure.story("Authentication Flow")
class TestAuthenticationWorkflow:
    """Tests for authentication workflows."""
    
    def test_register_then_login_workflow(
        self,
        auth_client: AuthClient,
        valid_register_data: dict
    ):
        """Test registering and then logging in."""
        # Register
        register_response = auth_client.register(**valid_register_data)
        assert register_response.is_success()
        assert "token" in register_response.json
        
        # Login with same credentials
        login_response = auth_client.login(**valid_register_data)
        assert login_response.is_success()
        assert "token" in login_response.json
    
    def test_failed_login_retry_workflow(self, auth_client: AuthClient, valid_auth_data: dict):
        """Test failing login then succeeding."""
        # Fail with wrong credentials
        fail_response = auth_client.login_unsuccessful(email="wrong@test.com")
        assert not fail_response.is_success()
        
        # Succeed with correct credentials
        success_response = auth_client.login(**valid_auth_data)
        assert success_response.is_success()
    
    def test_multiple_login_sessions(self, auth_client: AuthClient, valid_auth_data: dict):
        """Test multiple concurrent login sessions."""
        tokens = []
        
        for _ in range(3):
            response = auth_client.login(**valid_auth_data)
            assert response.is_success()
            tokens.append(response.json["token"])
        
        assert len(tokens) == 3


@pytest.mark.workflows
@pytest.mark.regression
@allure.feature("Workflows")
@allure.story("Data Retrieval")
class TestDataRetrievalWorkflow:
    """Tests for data retrieval workflows."""
    
    def test_pagination_workflow(self, users_client: UsersClient):
        """Test paginating through all users."""
        page = 1
        all_users = []
        
        while True:
            response = users_client.get_users(page=page)
            assert response.is_success()
            
            users = response.json["data"]
            if not users:
                break
            
            all_users.extend(users)
            
            if page >= response.json["total_pages"]:
                break
            
            page += 1
        
        assert len(all_users) > 0
    
    def test_retrieve_multiple_users_by_id(self, users_client: UsersClient):
        """Test retrieving multiple specific users."""
        user_ids = [1, 2, 3]
        users = []
        
        for user_id in user_ids:
            response = users_client.get_user(user_id)
            assert response.is_success()
            users.append(response.json["data"])
        
        assert len(users) == 3
        assert all(user["id"] in user_ids for user in users)


@pytest.mark.workflows
@pytest.mark.smoke
@allure.feature("Workflows")
@allure.story("Critical Path")
class TestCriticalPathWorkflows:
    """Tests for critical business workflows."""
    
    def test_happy_path_user_management(self, users_client: UsersClient):
        """Test the happy path for user management."""
        # List users
        list_response = users_client.get_users()
        assert list_response.is_success()
        assert len(list_response.json["data"]) > 0
        
        # Get specific user
        user_response = users_client.get_user(1)
        assert user_response.is_success()
        
        # Create new user
        create_response = users_client.create_user(name="Test User", job="Tester")
        assert create_response.is_success()
    
    def test_error_recovery_workflow(self, users_client: UsersClient, non_existent_user_id: int):
        """Test recovering from errors gracefully."""
        # Try to get non-existent user
        fail_response = users_client.get_user(non_existent_user_id)
        assert fail_response.status_code == 404
        
        # Successfully get existing user
        success_response = users_client.get_user(1)
        assert success_response.is_success()
