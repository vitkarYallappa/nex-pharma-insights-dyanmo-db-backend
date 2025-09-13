"""
Keywords Table Configuration
Dedicated configuration for the keywords table schema and settings
Matches SQLAlchemy schema structure with DynamoDB NoSQL approach
"""

from typing import Dict, Any

class KeywordsTableConfig:
    """Configuration for the keywords table"""
    
    # Table name (without environment suffix)
    TABLE_NAME = "keywords"
    
    # Field mapping from SQLAlchemy to DynamoDB
    # SQLAlchemy -> DynamoDB mapping:
    # id (UUID) -> pk (String) - Primary key
    # keyword (String) -> keyword (String) - Keyword text
    # request_id (UUID) -> request_id (String) - Request ID reference
    # keyword_type (String) -> keyword_type (String) - Keyword type/category
    # created_at (DateTime) -> created_at (String) - ISO timestamp
    # updated_at (DateTime) -> updated_at (String) - ISO timestamp
    
    # Complete DynamoDB schema for keywords table
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
        "keyword": "machine learning",  # Keyword text
        "request_id": "987fcdeb-51a2-43d7-8f9e-123456789abc",  # Request ID reference
        "keyword_type": "technology",  # Keyword type/category
        "created_at": "2024-12-01T10:00:00Z",  # ISO timestamp
        "updated_at": "2024-12-01T12:00:00Z"   # ISO timestamp
    }
    
    @classmethod
    def get_table_name(cls, environment: str = None) -> str:
        """Get table name without environment suffix"""
        return cls.TABLE_NAME
    
    @classmethod
    def get_schema(cls, environment: str = None) -> Dict[str, Any]:
        """Get complete schema with table name"""
        schema = cls.SCHEMA.copy()
        schema["table_name"] = cls.get_table_name()
        return schema
    
    @classmethod
    def get_description(cls) -> str:
        """Get table description"""
        return "Keywords table with primary key only - simple and fast" 