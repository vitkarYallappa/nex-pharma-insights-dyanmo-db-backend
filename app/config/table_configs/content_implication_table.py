"""
Content Implication Table Configuration
Dedicated configuration for the content_implication table schema and settings
Matches SQLAlchemy schema structure with DynamoDB NoSQL approach
"""

from typing import Dict, Any

class ContentImplicationTableConfig:
    """Configuration for the content_implication table"""
    
    # Table name (without environment suffix)
    TABLE_NAME = "content_implication"
    
    # Field mapping from SQLAlchemy to DynamoDB
    # SQLAlchemy -> DynamoDB mapping:
    # implication_id (UUID) -> pk (String) - Primary key
    # url_id (UUID) -> url_id (String) - URL ID reference
    # content_id (UUID) -> content_id (String) - Content ID reference
    # implication_text (String) -> implication_text (String) - Implication text
    # implication_content_file_path (String) -> implication_content_file_path (String) - File path
    # implication_type (String) -> implication_type (String) - Implication type
    # priority_level (String) -> priority_level (String) - Priority level
    # confidence_score (Numeric) -> confidence_score (Number) - Confidence score
    # version (Integer) -> version (Number) - Version number
    # is_canonical (Boolean) -> is_canonical (Boolean) - Canonical flag
    # preferred_choice (Boolean) -> preferred_choice (Boolean) - Preferred choice flag
    # created_at (DateTime) -> created_at (String) - ISO timestamp
    # created_by (String) -> created_by (String) - Creator identifier
    
    # Complete DynamoDB schema for content_implication table
    SCHEMA = {
        "table_name": TABLE_NAME,
        "key_schema": [
            {
                "AttributeName": "pk",  # Maps to SQLAlchemy 'implication_id' field
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
        "url_id": "987fcdeb-51a2-43d7-8f9e-123456789abc",  # URL ID reference
        "content_id": "456e7890-f12a-34b5-c678-901234567def",  # Content ID reference
        "implication_text": "The increased R&D investment in oncology drugs suggests potential market consolidation and higher drug prices, which may impact healthcare accessibility and insurance coverage policies.",  # Implication text
        "implication_content_file_path": "/content/implications/2024/pharma-market-implications.txt",  # File path
        "implication_type": "business_impact",  # Implication type
        "priority_level": "high",  # Priority level
        "confidence_score": 0.87,  # Confidence score (0.00-1.00)
        "version": 1,  # Version number
        "is_canonical": True,  # Canonical flag
        "preferred_choice": True,  # Preferred choice flag
        "created_at": "2024-12-01T10:00:00Z",  # ISO timestamp
        "created_by": "ai-implication-analyzer-v2"  # Creator identifier
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
        return "Content implication table with primary key only - simple and fast" 