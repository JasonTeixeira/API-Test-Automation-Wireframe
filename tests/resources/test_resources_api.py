"""
Resources API test suite.

Tests cover resource CRUD operations, pagination, schema validation, and error handling.
"""
import allure
import pytest

from clients.resources_client import ResourcesClient
from models.schemas import RESOURCE_SCHEMA, validate_resource_schema


@pytest.mark.resources
@pytest.mark.smoke
@allure.feature("Resources API")
@allure.story("List Resources")
class TestGetResources:
    """Tests for GET /unknown endpoint - listing resources."""
    
    def test_get_resources_default(self, resources_client: ResourcesClient):
        """Test getting resources with default pagination."""
        response = resources_client.get_resources()
        
        assert response.is_success()
        assert response.status_code == 200
        assert "data" in response.json
        assert isinstance(response.json["data"], list)
        assert len(response.json["data"]) > 0
    
    def test_get_resources_with_page(self, resources_client: ResourcesClient):
        """Test getting resources with specific page."""
        response = resources_client.get_resources(page=2)
        
        assert response.is_success()
        assert response.json["page"] == 2
    
    def test_get_resources_with_per_page(self, resources_client: ResourcesClient):
        """Test getting resources with custom per_page."""
        per_page = 4
        response = resources_client.get_resources(per_page=per_page)
        
        assert response.is_success()
        assert response.json["per_page"] == per_page
        assert len(response.json["data"]) <= per_page
    
    def test_get_resources_pagination_metadata(self, resources_client: ResourcesClient):
        """Test pagination metadata structure."""
        response = resources_client.get_resources()
        
        assert response.is_success()
        data = response.json
        assert "page" in data
        assert "per_page" in data
        assert "total" in data
        assert "total_pages" in data
    
    def test_get_resources_response_time(
        self,
        resources_client: ResourcesClient,
        assert_performance
    ):
        """Test response time is within threshold."""
        response = resources_client.get_resources()
        
        assert response.is_success()
        assert_performance(response.elapsed_time, "GET /unknown")


@pytest.mark.resources
@pytest.mark.smoke
@allure.feature("Resources API")
@allure.story("Single Resource")
class TestGetSingleResource:
    """Tests for GET /unknown/{id} endpoint - getting single resource."""
    
    def test_get_existing_resource(
        self,
        resources_client: ResourcesClient,
        existing_resource_id: int
    ):
        """Test getting an existing resource by ID."""
        response = resources_client.get_resource(existing_resource_id)
        
        assert response.is_success()
        assert response.status_code == 200
        assert "data" in response.json
        assert response.json["data"]["id"] == existing_resource_id
    
    def test_get_resource_has_required_fields(self, resources_client: ResourcesClient):
        """Test that resource has all required fields."""
        response = resources_client.get_resource(1)
        
        assert response.is_success()
        resource_data = response.json["data"]
        
        required_fields = ["id", "name", "year", "color", "pantone_value"]
        for field in required_fields:
            assert field in resource_data, f"Missing required field: {field}"
    
    def test_get_resource_color_format(self, resources_client: ResourcesClient):
        """Test that color field is in hex format."""
        response = resources_client.get_resource(1)
        
        assert response.is_success()
        color = response.json["data"]["color"]
        assert color.startswith("#")
        assert len(color) == 7  # #RRGGBB
    
    def test_get_resource_year_is_valid(self, resources_client: ResourcesClient):
        """Test that year is a valid value."""
        response = resources_client.get_resource(1)
        
        assert response.is_success()
        year = response.json["data"]["year"]
        assert isinstance(year, int)
        assert 1900 <= year <= 2100
    
    def test_get_non_existent_resource(
        self,
        resources_client: ResourcesClient,
        non_existent_resource_id: int
    ):
        """Test getting non-existent resource returns 404."""
        response = resources_client.get_resource(non_existent_resource_id)
        
        assert response.status_code == 404
        assert not response.is_success()
    
    def test_get_resource_schema_validation(
        self,
        resources_client: ResourcesClient,
        validate_json_schema
    ):
        """Test resource response matches schema."""
        response = resources_client.get_resource(2)
        
        assert response.is_success()
        validate_json_schema(response.json["data"], RESOURCE_SCHEMA)
    
    def test_get_resource_pydantic_validation(self, resources_client: ResourcesClient):
        """Test resource with Pydantic model validation."""
        response = resources_client.get_resource(2)
        
        assert response.is_success()
        resource = validate_resource_schema(response.json["data"])
        assert resource.id == 2
        assert resource.id > 0


@pytest.mark.resources
@pytest.mark.regression
@allure.feature("Resources API")
@allure.story("Create Resource")
class TestCreateResource:
    """Tests for POST /unknown endpoint - creating resources."""
    
    def test_create_resource_success(
        self,
        resources_client: ResourcesClient,
        resource_data: dict
    ):
        """Test creating a new resource with valid data."""
        response = resources_client.create_resource(**resource_data)
        
        assert response.is_success()
        assert response.status_code == 201
        assert "id" in response.json
        assert "createdAt" in response.json
    
    def test_create_resource_returns_id(
        self,
        resources_client: ResourcesClient,
        resource_data: dict
    ):
        """Test that created resource has an ID."""
        response = resources_client.create_resource(**resource_data)
        
        assert response.is_success()
        assert "id" in response.json
        assert response.json["id"] is not None
    
    def test_create_resource_timestamp(
        self,
        resources_client: ResourcesClient,
        resource_data: dict
    ):
        """Test that creation timestamp is present."""
        response = resources_client.create_resource(**resource_data)
        
        assert response.is_success()
        assert "createdAt" in response.json
        created_at = response.json["createdAt"]
        assert created_at is not None
        assert len(created_at) > 0


@pytest.mark.resources
@pytest.mark.regression
@allure.feature("Resources API")
@allure.story("Update Resource")
class TestUpdateResource:
    """Tests for PUT/PATCH /unknown/{id} endpoint - updating resources."""
    
    def test_update_resource_with_put(self, resources_client: ResourcesClient):
        """Test updating resource with PUT."""
        resource_id = 2
        update_data = {
            "name": "Updated Resource",
            "year": 2024,
            "color": "#FF5733",
            "pantone_value": "19-1664"
        }
        
        response = resources_client.update_resource(resource_id, **update_data)
        
        assert response.is_success()
        assert response.status_code == 200
        assert "updatedAt" in response.json
    
    def test_partial_update_resource_with_patch(self, resources_client: ResourcesClient):
        """Test partially updating resource with PATCH."""
        resource_id = 2
        patch_data = {"name": "Partially Updated"}
        
        response = resources_client.partial_update_resource(resource_id, **patch_data)
        
        assert response.is_success()
        assert response.status_code == 200
        assert "updatedAt" in response.json
    
    def test_update_timestamp_is_present(self, resources_client: ResourcesClient):
        """Test that updatedAt timestamp is present."""
        response = resources_client.update_resource(1, name="Test")
        
        assert response.is_success()
        updated_at = response.json["updatedAt"]
        assert updated_at is not None
        assert len(updated_at) > 0


@pytest.mark.resources
@pytest.mark.regression
@allure.feature("Resources API")
@allure.story("Delete Resource")
class TestDeleteResource:
    """Tests for DELETE /unknown/{id} endpoint - deleting resources."""
    
    def test_delete_resource_success(self, resources_client: ResourcesClient):
        """Test deleting a resource."""
        resource_id = 2
        response = resources_client.delete_resource(resource_id)
        
        assert response.status_code == 204
        assert response.text == ""
    
    def test_delete_non_existent_resource(
        self,
        resources_client: ResourcesClient,
        non_existent_resource_id: int
    ):
        """Test deleting non-existent resource."""
        response = resources_client.delete_resource(non_existent_resource_id)
        
        assert response.status_code == 204
    
    def test_delete_resource_response_time(
        self,
        resources_client: ResourcesClient,
        assert_performance
    ):
        """Test that deletion completes quickly."""
        response = resources_client.delete_resource(1)
        
        assert_performance(response.elapsed_time, "DELETE /unknown")


@pytest.mark.resources
@pytest.mark.regression
@allure.feature("Resources API")
@allure.story("Resource Data Integrity")
class TestResourceDataIntegrity:
    """Tests for resource data integrity and validation."""
    
    def test_resource_id_is_positive(self, resources_client: ResourcesClient):
        """Test that resource ID is positive integer."""
        response = resources_client.get_resource(1)
        
        assert response.is_success()
        resource_id = response.json["data"]["id"]
        assert isinstance(resource_id, int)
        assert resource_id > 0
    
    def test_resource_name_is_not_empty(self, resources_client: ResourcesClient):
        """Test that resource name is not empty."""
        response = resources_client.get_resource(1)
        
        assert response.is_success()
        name = response.json["data"]["name"]
        assert isinstance(name, str)
        assert len(name) > 0
    
    def test_pantone_value_format(self, resources_client: ResourcesClient):
        """Test that pantone value has expected format."""
        response = resources_client.get_resource(1)
        
        assert response.is_success()
        pantone = response.json["data"]["pantone_value"]
        assert isinstance(pantone, str)
        assert len(pantone) > 0
