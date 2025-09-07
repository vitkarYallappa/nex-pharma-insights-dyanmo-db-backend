"""
Requests Table Configuration
Dedicated configuration for the requests table schema and settings
Matches SQLAlchemy schema structure with DynamoDB NoSQL approach
"""

from typing import Dict, Any

class RequestsTableConfig:
    """Configuration for the requests table"""
    
    # Table name (without environment suffix)
    TABLE_NAME = "requests"
    
    # Field mapping from SQLAlchemy to DynamoDB
    # SQLAlchemy -> DynamoDB mapping:
    # id (UUID) -> pk (String) - Primary key
    # project_id (UUID) -> project_id (String) - Project ID reference
    # title (String) -> title (String) - Request title
    # description (Text) -> description (String) - Request description
    # time_range (JSON) -> time_range (Map) - Time range JSON
    # priority (String) -> priority (String) - Request priority
    # status (String) -> status (String) - Request status
    # estimated_completion (DateTime) -> estimated_completion (String) - ISO timestamp
    # created_by (UUID) -> created_by (String) - Creator user ID
    # created_at (DateTime) -> created_at (String) - ISO timestamp
    # updated_at (DateTime) -> updated_at (String) - ISO timestamp
    
    # Complete DynamoDB schema for requests table
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
        "project_id": "987fcdeb-51a2-43d7-8f9e-123456789abc",  # Project ID reference
        "title": "Analyze Q4 Sales Data",  # Request title
        "description": "Comprehensive analysis of Q4 sales performance across all regions",  # Request description
        "time_range": {  # Time range as Map
            "start_date": "2024-01-01",
            "end_date": "2024-03-31",
            "timezone": "UTC"
        },
        "priority": "high",  # Request priority
        "status": "pending",  # Request status
        "estimated_completion": "2024-12-15T18:00:00Z",  # ISO timestamp
        "created_by": "456e7890-f12a-34b5-c678-901234567def",  # Creator user ID
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
        return "Requests table with primary key only - simple and fast" 