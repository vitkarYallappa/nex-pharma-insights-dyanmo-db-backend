"""
Content Relevance Table Configuration
Dedicated configuration for the content_relevance table schema and settings
Stores relevance analysis and scoring for content entries
"""

from typing import Dict, Any

class ContentRelevanceTableConfig:
    """Configuration for the content_relevance table"""
    
    # Table name (without environment suffix)
    TABLE_NAME = "content_relevance"
    
    # Field mapping for DynamoDB:
    # relevance_id (UUID) -> pk (String) - Primary key
    # url_id (UUID) -> url_id (String) - URL ID reference (same as content_id)
    # content_id (UUID) -> content_id (String) - Content repository reference
    # relevance_text (String) -> relevance_text (String) - Relevance analysis text
    # relevance_score (str) -> relevance_score (Number) - Relevance score
    # is_relevant (Boolean) -> is_relevant (Boolean) - Whether content is relevant
    # relevance_content_file_path (String) -> relevance_content_file_path (String) - File path
    # relevance_category (String) -> relevance_category (String) - Relevance category
    # confidence_score (str) -> confidence_score (Number) - Confidence score
    # version (Integer) -> version (Number) - Version number
    # is_canonical (Boolean) -> is_canonical (Boolean) - Canonical status
    # preferred_choice (Boolean) -> preferred_choice (Boolean) - Preferred choice flag
    # created_at (DateTime) -> created_at (String) - ISO timestamp
    # created_by (String) -> created_by (String) - Creator identifier
    
    # Complete DynamoDB schema for content_relevance table
    SCHEMA = {
        "table_name": TABLE_NAME,
        "key_schema": [
            {
                "AttributeName": "pk",  # Maps to 'relevance_id' field
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
        "content_id": "987fcdeb-51a2-43d7-8f9e-123456789abc",  # Content repository reference
        "relevance_text": "This content is highly relevant to the pharmaceutical research topic...",  # Relevance analysis
        "relevance_score": 0.85,  # Relevance score (0.0 to 1.0)
        "is_relevant": True,  # Whether content is relevant
        "relevance_content_file_path": "/storage/relevance/content_123.json",  # File path
        "relevance_category": "high_relevance",  # Relevance category
        "confidence_score": 0.92,  # Confidence score (0.0 to 1.0)
        "version": 1,  # Version number
        "is_canonical": True,  # Canonical status
        "preferred_choice": True,  # Preferred choice flag
        "created_at": "2024-12-01T10:00:00Z",  # ISO timestamp
        "created_by": "relevance_check_service"  # Creator identifier
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
        return "Content relevance table for storing relevance analysis and scoring data" 