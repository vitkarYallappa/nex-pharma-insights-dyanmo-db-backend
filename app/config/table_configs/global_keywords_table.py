"""
Global Keywords Table Configuration
Dedicated configuration for the global_keywords table schema and settings
Matches SQLAlchemy schema structure with DynamoDB NoSQL approach
"""

from typing import Dict, Any

class GlobalKeywordsTableConfig:
    """Configuration for the global_keywords table"""
    
    # Table name (without environment suffix)
    TABLE_NAME = "global_keywords"
    
    # Field mapping from SQLAlchemy to DynamoDB
    # SQLAlchemy -> DynamoDB mapping:
    # id (UUID) -> pk (String) - Primary key
    # keyword (String) -> keyword (String) - Keyword text
    # keyword_type (String) -> keyword_type (String) - Keyword type/category
    # created_at (DateTime) -> created_at (String) - ISO timestamp
    # updated_at (DateTime) -> updated_at (String) - ISO timestamp
    
    # Complete DynamoDB schema for global_keywords table
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
        "keyword": "artificial intelligence",  # Keyword text
        "keyword_type": "technology",  # Keyword type/category
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
        return "Global keywords table with primary key only - simple and fast" 