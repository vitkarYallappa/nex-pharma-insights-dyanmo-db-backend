"""
Source URLs Table Configuration
Dedicated configuration for the source_urls table schema and settings
Matches SQLAlchemy schema structure with DynamoDB NoSQL approach
"""

from typing import Dict, Any

class SourceUrlsTableConfig:
    """Configuration for the source_urls table"""
    
    # Table name (without environment suffix)
    TABLE_NAME = "source_urls"
    
    # Field mapping from SQLAlchemy to DynamoDB
    # SQLAlchemy -> DynamoDB mapping:
    # id (UUID) -> pk (String) - Primary key
    # request_id (UUID) -> request_id (String) - Request ID reference
    # url (String) -> url (String) - Source URL
    # source_name (String) -> source_name (String) - Source name
    # source_type (String) -> source_type (String) - Source type
    # country_region (String) -> country_region (String) - Country/region
    # is_active (Boolean) -> is_active (Boolean) - Active status
    # url_metadata (JSON) -> url_metadata (Map) - URL metadata JSON
    # created_at (DateTime) -> created_at (String) - ISO timestamp
    # updated_at (DateTime) -> updated_at (String) - ISO timestamp
    
    # Complete DynamoDB schema for source_urls table
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
        "request_id": "987fcdeb-51a2-43d7-8f9e-123456789abc",  # Request ID reference
        "url": "https://api.example.com/data/endpoint",  # Source URL
        "source_name": "Example Data API",  # Source name
        "source_type": "rest_api",  # Source type
        "country_region": "US",  # Country/region
        "is_active": True,  # Active status
        "url_metadata": {  # URL metadata as Map
            "rate_limit": 100,
            "auth_required": True,
            "data_format": "json",
            "last_accessed": "2024-12-01T11:00:00Z"
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
        return "Source URLs table with primary key only - simple and fast" 