"""
Implication Comment Table Configuration
Dedicated configuration for the implication_comment table schema and settings
Matches SQLAlchemy schema structure with DynamoDB NoSQL approach
"""

from typing import Dict, Any

class ImplicationCommentTableConfig:
    """Configuration for the implication_comment table"""
    
    # Table name (without environment suffix)
    TABLE_NAME = "implication_comment"
    
    # Field mapping from SQLAlchemy to DynamoDB
    # SQLAlchemy -> DynamoDB mapping:
    # id (UUID) -> pk (String) - Primary key
    # implication_id (UUID) -> implication_id (String) - Implication ID reference
    # comment_text (Text) -> comment_text (String) - Comment text
    # comment_type (String) -> comment_type (String) - Comment type
    # created_at (DateTime) -> created_at (String) - ISO timestamp
    # updated_at (DateTime) -> updated_at (String) - ISO timestamp
    
    # Complete DynamoDB schema for implication_comment table
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
        "implication_id": "987fcdeb-51a2-43d7-8f9e-123456789abc",  # Implication ID reference
        "comment_text": "This implication highlights critical regulatory considerations that could significantly impact our market entry strategy. The analysis suggests we need to adjust our compliance framework before proceeding with the product launch.",  # Comment text
        "comment_type": "regulatory_feedback",  # Comment type
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
        return "Implication comment table with primary key only - simple and fast" 