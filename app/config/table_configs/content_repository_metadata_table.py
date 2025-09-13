"""
Content Repository Metadata Table Configuration
Dedicated configuration for the content_repository_metadata table schema and settings
Stores metadata information for content repository entries
"""

from typing import Dict, Any

class ContentRepositoryMetadataTableConfig:
    """Configuration for the content_repository_metadata table"""
    
    # Table name (without environment suffix)
    TABLE_NAME = "content_repository_metadata"
    
    # Field mapping for DynamoDB:
    # metadata_id (UUID) -> pk (String) - Primary key
    # content_id (UUID) -> content_id (String) - Content repository reference
    # request_id (UUID) -> request_id (String) - Request ID reference
    # project_id (UUID) -> project_id (String) - Project ID reference
    # metadata_type (String) -> metadata_type (String) - Type of metadata
    # metadata_key (String) -> metadata_key (String) - Metadata key
    # metadata_value (String) -> metadata_value (String) - Metadata value
    # data_type (String) -> data_type (String) - Data type (string, number, boolean, json)
    # is_searchable (Boolean) -> is_searchable (Boolean) - Whether metadata is searchable
    # created_at (DateTime) -> created_at (String) - ISO timestamp
    # updated_at (DateTime) -> updated_at (String) - ISO timestamp
    
    # Complete DynamoDB schema for content_repository_metadata table
    SCHEMA = {
        "table_name": TABLE_NAME,
        "key_schema": [
            {
                "AttributeName": "pk",  # Maps to 'metadata_id' field
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
        "content_id": "987fcdeb-51a2-43d7-8f9e-123456789abc",  # Content repository reference
        "request_id": "456e7890-f12a-34b5-c678-901234567def",  # Request ID reference
        "project_id": "789abcde-f012-3456-7890-123456789abc",  # Project ID reference
        "metadata_type": "extraction_info",  # Type of metadata
        "metadata_key": "word_count",  # Metadata key
        "metadata_value": "1250",  # Metadata value
        "data_type": "number",  # Data type
        "is_searchable": True,  # Whether metadata is searchable
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
        return "Content repository metadata table for storing additional metadata information" 