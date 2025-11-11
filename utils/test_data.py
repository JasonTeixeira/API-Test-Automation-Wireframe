"""
Test data generation utilities using Faker.

Provides realistic test data for API testing scenarios.
"""
from dataclasses import dataclass
from typing import Dict, List, Optional

from faker import Faker

# Initialize Faker with seed for reproducibility
fake = Faker()
Faker.seed(12345)


@dataclass
class UserData:
    """User data model for test data generation."""
    name: str
    job: str
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None


@dataclass
class AuthData:
    """Authentication data model."""
    email: str
    password: str


@dataclass
class ResourceData:
    """Resource data model for test data generation."""
    name: str
    year: int
    color: str
    pantone_value: str


class TestDataGenerator:
    """Generator for API test data."""
    
    @staticmethod
    def generate_user_data(include_email: bool = False) -> Dict[str, str]:
        """
        Generate random user data.
        
        Args:
            include_email: Whether to include email field
            
        Returns:
            Dictionary with user data
        """
        data = {
            "name": fake.name(),
            "job": fake.job()
        }
        if include_email:
            data["email"] = fake.email()
        return data
    
    @staticmethod
    def generate_user_data_full() -> Dict[str, str]:
        """
        Generate complete user profile data.
        
        Returns:
            Dictionary with full user data
        """
        return {
            "email": fake.email(),
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "name": fake.name(),
            "job": fake.job()
        }
    
    @staticmethod
    def generate_auth_data(valid: bool = True) -> Dict[str, str]:
        """
        Generate authentication data.
        
        Args:
            valid: Whether to generate valid credentials
            
        Returns:
            Dictionary with auth credentials
        """
        if valid:
            # ReqRes.in specific valid credentials
            return {
                "email": "eve.holt@reqres.in",
                "password": "pistol"
            }
        else:
            return {
                "email": fake.email(),
                "password": fake.password()
            }
    
    @staticmethod
    def generate_register_data(valid: bool = True) -> Dict[str, str]:
        """
        Generate registration data.
        
        Args:
            valid: Whether to generate valid registration data
            
        Returns:
            Dictionary with registration data
        """
        if valid:
            # ReqRes.in specific valid registration
            return {
                "email": "eve.holt@reqres.in",
                "password": "pistol"
            }
        else:
            data = {"email": fake.email()}
            # Optionally include invalid password
            if fake.boolean():
                data["password"] = fake.password(length=fake.random_int(1, 5))
            return data
    
    @staticmethod
    def generate_resource_data() -> Dict[str, any]:
        """
        Generate resource data.
        
        Returns:
            Dictionary with resource data
        """
        return {
            "name": fake.color_name(),
            "year": fake.year(),
            "color": fake.hex_color(),
            "pantone_value": f"{fake.random_int(10, 99)}-{fake.random_int(1000, 9999)}"
        }
    
    @staticmethod
    def generate_invalid_json() -> List[str]:
        """
        Generate invalid JSON payloads for negative testing.
        
        Returns:
            List of invalid JSON strings
        """
        return [
            "{invalid json}",
            '{"name": "test"',  # Missing closing brace
            '{"name": }',  # Missing value
            "",  # Empty string
            "null",
            "true",
            "123",
            '{"name": undefined}',  # Invalid value
        ]
    
    @staticmethod
    def generate_invalid_email() -> str:
        """Generate invalid email address."""
        invalid_formats = [
            "invalid.email",
            "@example.com",
            "user@",
            "user name@example.com",
            "user@.com",
            ""
        ]
        return fake.random_element(invalid_formats)
    
    @staticmethod
    def generate_sql_injection_payloads() -> List[str]:
        """
        Generate SQL injection test payloads.
        
        Returns:
            List of SQL injection strings
        """
        return [
            "' OR '1'='1",
            "'; DROP TABLE users--",
            "1' OR '1' = '1",
            "admin'--",
            "' OR 1=1--",
        ]
    
    @staticmethod
    def generate_xss_payloads() -> List[str]:
        """
        Generate XSS test payloads.
        
        Returns:
            List of XSS strings
        """
        return [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "javascript:alert('XSS')",
            "<svg onload=alert('XSS')>",
        ]
    
    @staticmethod
    def generate_long_string(length: int = 10000) -> str:
        """
        Generate extremely long string for boundary testing.
        
        Args:
            length: String length
            
        Returns:
            Long string
        """
        return "A" * length
    
    @staticmethod
    def generate_special_characters() -> List[str]:
        """
        Generate strings with special characters.
        
        Returns:
            List of special character strings
        """
        return [
            "!@#$%^&*()",
            "日本語",  # Japanese
            "Ñoño",  # Spanish with tildes
            "Москва",  # Cyrillic
            "🎉🎊🎁",  # Emojis
            "\n\r\t",  # Whitespace characters
            "\\x00\\x01\\x02",  # Null bytes
        ]
    
    @staticmethod
    def generate_boundary_values() -> Dict[str, any]:
        """
        Generate boundary values for testing.
        
        Returns:
            Dictionary with boundary test values
        """
        return {
            "empty_string": "",
            "single_char": "A",
            "very_long": "A" * 10000,
            "zero": 0,
            "negative": -1,
            "max_int": 2147483647,
            "min_int": -2147483648,
            "null": None,
            "boolean_true": True,
            "boolean_false": False,
        }
    
    @staticmethod
    def generate_bulk_users(count: int = 10) -> List[Dict[str, str]]:
        """
        Generate multiple user records for bulk testing.
        
        Args:
            count: Number of users to generate
            
        Returns:
            List of user dictionaries
        """
        return [
            {
                "name": fake.name(),
                "job": fake.job(),
                "email": fake.email()
            }
            for _ in range(count)
        ]


# Global instance
test_data = TestDataGenerator()
