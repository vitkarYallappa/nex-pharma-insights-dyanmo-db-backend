"""
Insight Comment Table Configuration
Dedicated configuration for the insight_comment table schema and settings
Matches SQLAlchemy schema structure with DynamoDB NoSQL approach
"""

from typing import Dict, Any

class InsightCommentTableConfig:
    """Configuration for the insight_comment table"""
    
    # Table name (without environment suffix)
    TABLE_NAME = "insight_comment"
    
    # Field mapping from SQLAlchemy to DynamoDB
    # SQLAlchemy -> DynamoDB mapping:
    # id (UUID) -> pk (String) - Primary key
    # insight_id (UUID) -> insight_id (String) - Insight ID reference
    # comment_text (Text) -> comment_text (String) - Comment text
    # comment_type (String) -> comment_type (String) - Comment type
    # created_at (DateTime) -> created_at (String) - ISO timestamp
    # updated_at (DateTime) -> updated_at (String) - ISO timestamp
    
    # Complete DynamoDB schema for insight_comment table
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
        "insight_id": "987fcdeb-51a2-43d7-8f9e-123456789abc",  # Insight ID reference
        "comment_text": "This insight provides valuable market intelligence that could significantly impact our strategic planning for Q2 2024. The analysis methodology appears robust and the conclusions are well-supported by the data.",  # Comment text
        "comment_type": "analysis_feedback",  # Comment type
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
        return "Insight comment table with primary key only - simple and fast" 