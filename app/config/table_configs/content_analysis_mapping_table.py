"""
Content Analysis Mapping Table Configuration
Dedicated configuration for the content_analysis_mapping table schema and settings
Matches SQLAlchemy schema structure with DynamoDB NoSQL approach
"""

from typing import Dict, Any

class ContentAnalysisMappingTableConfig:
    """Configuration for the content_analysis_mapping table"""
    
    # Table name (without environment suffix)
    TABLE_NAME = "content_analysis_mapping"
    
    # Field mapping from SQLAlchemy to DynamoDB
    # SQLAlchemy -> DynamoDB mapping:
    # mapping_id (UUID) -> pk (String) - Primary key
    # content_id (UUID) -> content_id (String) - Content ID reference
    # primary_summary_id (UUID) -> primary_summary_id (String) - Primary summary ID reference
    # primary_insight_id (UUID) -> primary_insight_id (String) - Primary insight ID reference
    # primary_implication_id (UUID) -> primary_implication_id (String) - Primary implication ID reference
    # selection_strategy (String) -> selection_strategy (String) - Selection strategy
    # selection_context (String) -> selection_context (String) - Selection context
    # selected_by (String) -> selected_by (String) - Selected by identifier
    # selected_at (DateTime) -> selected_at (String) - ISO timestamp
    # version (Integer) -> version (Number) - Version number
    # is_current (Boolean) -> is_current (Boolean) - Current flag
    
    # Complete DynamoDB schema for content_analysis_mapping table
    SCHEMA = {
        "table_name": TABLE_NAME,
        "key_schema": [
            {
                "AttributeName": "pk",  # Maps to SQLAlchemy 'mapping_id' field
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
        "content_id": "987fcdeb-51a2-43d7-8f9e-123456789abc",  # Content ID reference
        "primary_summary_id": "456e7890-f12a-34b5-c678-901234567def",  # Primary summary ID reference
        "primary_insight_id": "789abcde-f123-45g6-h789-012345678901",  # Primary insight ID reference
        "primary_implication_id": "012fghij-k456-78l9-m012-345678901234",  # Primary implication ID reference
        "selection_strategy": "highest_confidence",  # Selection strategy
        "selection_context": "automated_analysis_v2",  # Selection context
        "selected_by": "ai-content-analyzer-v3",  # Selected by identifier
        "selected_at": "2024-12-01T10:00:00Z",  # ISO timestamp
        "version": 1,  # Version number
        "is_current": True  # Current flag
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
        return "Content analysis mapping table with primary key only - simple and fast" 