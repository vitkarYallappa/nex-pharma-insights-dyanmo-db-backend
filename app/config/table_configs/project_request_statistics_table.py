"""
Project Request Statistics Table Configuration
Dedicated configuration for the project_request_statistics table schema and settings
Matches SQLAlchemy schema structure with DynamoDB NoSQL approach
"""

from typing import Dict, Any

class ProjectRequestStatisticsTableConfig:
    """Configuration for the project_request_statistics table"""
    
    # Table name (without environment suffix)
    TABLE_NAME = "project_request_statistics"
    
    # Field mapping from SQLAlchemy to DynamoDB
    # SQLAlchemy -> DynamoDB mapping:
    # id (UUID) -> pk (String) - Primary key
    # project_id (UUID) -> project_id (String) - Project ID reference
    # total_requests (Integer) -> total_requests (Number) - Total request count
    # completed_requests (Integer) -> completed_requests (Number) - Completed request count
    # pending_requests (Integer) -> pending_requests (Number) - Pending request count
    # failed_requests (Integer) -> failed_requests (Number) - Failed request count
    # average_processing_time (str) -> average_processing_time (Number) - Average processing time
    # last_activity_at (DateTime) -> last_activity_at (String) - ISO timestamp
    # statistics_metadata (JSON) -> statistics_metadata (Map) - Statistics metadata
    # created_at (DateTime) -> created_at (String) - ISO timestamp
    # updated_at (DateTime) -> updated_at (String) - ISO timestamp
    
    # Complete DynamoDB schema for project_request_statistics table
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
        "total_requests": 150,  # Total request count
        "completed_requests": 120,  # Completed request count
        "pending_requests": 20,  # Pending request count
        "failed_requests": 10,  # Failed request count
        "average_processing_time": 45.5,  # Average processing time in seconds
        "last_activity_at": "2024-12-01T12:00:00Z",  # ISO timestamp
        "statistics_metadata": {  # Statistics metadata as Map
            "peak_hour": "14:00",
            "success_rate": 0.93,
            "performance_metrics": {
                "min_time": 5.2,
                "max_time": 120.8
            }
        },
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
        return "Project request statistics table with primary key only - simple and fast" 