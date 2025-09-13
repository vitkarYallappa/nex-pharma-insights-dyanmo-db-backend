"""
SERP Requests Table Configuration
Dedicated configuration for the serp_requests table schema and settings
Used by Stage 0 SERP agent for search request tracking and metadata
"""

from typing import Dict, Any

class SerpRequestsTableConfig:
    """Configuration for the serp_requests table"""
    
    # Table name (without environment suffix)
    TABLE_NAME = "serp_requests"
    
    # Complete DynamoDB schema for serp_requests table
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
        "query": "pharmaceutical market trends 2024",  # Search query text
        "num_results": 10,  # Number of results requested
        "total_results": 8,  # Total results found
        "successful_results": 7,  # Successfully retrieved results
        "failed_results": 1,  # Failed results
        "search_engine": "google",  # Search engine used
        "language": "en",  # Search language
        "country": "US",  # Search country
        "storage_key": "serp/2024/12/01/123e4567-e89b-12d3-a456-426614174000.json",  # S3/MinIO storage location
        "created_at": "2024-12-01T10:00:00.000Z",  # ISO timestamp
        "updated_at": "2024-12-01T10:05:00.000Z",  # ISO timestamp
        "status": "completed"  # Request status
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
        return "SERP search request tracking and metadata with primary key only - simple and fast" 