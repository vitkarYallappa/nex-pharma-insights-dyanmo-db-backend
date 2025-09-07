"""
Global Base URLs Table Configuration
Dedicated configuration for the global_base_urls table schema and settings
Matches SQLAlchemy schema structure with DynamoDB NoSQL approach
"""

from typing import Dict, Any

class GlobalBaseUrlsTableConfig:
    """Configuration for the global_base_urls table"""
    
    # Table name (without environment suffix)
    TABLE_NAME = "global_base_urls"
    
    # Field mapping from SQLAlchemy to DynamoDB
    # SQLAlchemy -> DynamoDB mapping:
    # id (UUID) -> pk (String) - Primary key
    # url (String) -> url (String) - Base URL
    # source_name (String) -> source_name (String) - Source name
    # source_type (String) -> source_type (String) - Source type
    # country_region (String) -> country_region (String) - Country/region
    # is_active (Boolean) -> is_active (Boolean) - Active status
    # url_metadata (JSON) -> url_metadata (Map) - URL metadata JSON
    # created_at (DateTime) -> created_at (String) - ISO timestamp
    # updated_at (DateTime) -> updated_at (String) - ISO timestamp
    
    # Complete DynamoDB schema for global_base_urls table
    SCHEMA = {
        "table_name": TABLE_NAME,
        "key_schema": [
            {
                "AttributeName": "pk",  # Maps to SQLAlchemy 'id' field
                "KeyType": "HASH"  # Partition key
            }
        ],
        "attribute_definitions": [
            {
                "AttributeName": "pk",
                "AttributeType": "S"  # String (UUID as string)
            }
        ],
        "billing_mode": "PAY_PER_REQUEST"
    }
    
    # Sample item structure (for reference - not used in table creation)
    SAMPLE_ITEM = {
        "pk": "123e4567-e89b-12d3-a456-426614174000",  # Primary key (UUID as string)
        "url": "https://api.example.com/v1",  # Base URL
        "source_name": "Example API",  # Source name
        "source_type": "rest_api",  # Source type
        "country_region": "US",  # Country/region
        "is_active": True,  # Active status
        "url_metadata": {  # URL metadata as Map
            "rate_limit": 1000,
            "auth_type": "bearer",
            "version": "v1",
            "documentation": "https://docs.example.com"
        },
        "created_at": "2024-12-01T10:00:00Z",  # ISO timestamp
        "updated_at": "2024-12-01T12:00:00Z"   # ISO timestamp
    }
    
    @classmethod
    def get_table_name(cls, environment: str = "local") -> str:
        """Get full table name with environment suffix"""
        return f"{cls.TABLE_NAME}-{environment}"
    
    @classmethod
    def get_schema(cls, environment: str = "local") -> Dict[str, Any]:
        """Get complete schema with environment-specific table name"""
        schema = cls.SCHEMA.copy()
        schema["table_name"] = cls.get_table_name(environment)
        return schema
    
    @classmethod
    def get_description(cls) -> str:
        """Get table description"""
        return "Global base URLs table with primary key only - simple and fast" 