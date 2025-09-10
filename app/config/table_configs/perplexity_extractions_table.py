"""
Perplexity Extractions Table Configuration
Dedicated configuration for the perplexity_extractions table schema and settings
Used by Stage 0 Perplexity agent for content extraction tracking
"""

from typing import Dict, Any

class PerplexityExtractionsTableConfig:
    """Configuration for the perplexity_extractions table"""
    
    # Table name (without environment suffix)
    TABLE_NAME = "perplexity_extractions"
    
    # Complete DynamoDB schema for perplexity_extractions table
    SCHEMA = {
        "table_name": TABLE_NAME,
        "key_schema": [
            {
                "AttributeName": "request_id",
                "KeyType": "HASH"  # Partition key
            }
        ],
        "attribute_definitions": [
            {
                "AttributeName": "request_id",
                "AttributeType": "S"  # String (UUID)
            }
        ],
        "billing_mode": "PAY_PER_REQUEST"
    }
    
    # Sample item structure (for reference - not used in table creation)
    SAMPLE_ITEM = {
        "request_id": "123e4567-e89b-12d3-a456-426614174000",  # Primary key (UUID)
        "total_urls": 15,  # Total URLs processed
        "successful_extractions": 12,  # Successful extractions
        "failed_extractions": 3,  # Failed extractions
        "storage_key": "perplexity/2024/12/01/123e4567-e89b-12d3-a456-426614174000.json",  # S3/MinIO storage location
        "created_at": "2024-12-01T10:00:00.000Z",  # ISO timestamp
        "updated_at": "2024-12-01T10:15:00.000Z",  # ISO timestamp
        "status": "completed"  # Extraction status
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
        return "Perplexity content extraction tracking with primary key only - simple and fast" 