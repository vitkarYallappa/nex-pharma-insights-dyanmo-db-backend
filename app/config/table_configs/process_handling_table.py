"""
Process Handling Table Configuration
Dedicated configuration for the process_handling table schema and settings
Matches SQLAlchemy schema structure with DynamoDB NoSQL approach
"""

from typing import Dict, Any

class ProcessHandlingTableConfig:
    """Configuration for the process_handling table"""
    
    # Table name (without environment suffix)
    TABLE_NAME = "process_handling"
    
    # Field mapping from SQLAlchemy to DynamoDB
    # SQLAlchemy -> DynamoDB mapping:
    # process_id (UUID) -> pk (String) - Primary key
    # request_id (UUID) -> request_id (String) - Request ID reference
    # project_id (UUID) -> project_id (String) - Project ID reference
    # status (String) -> status (String) - Process status
    # priority (Integer) -> priority (Number) - Process priority
    # total_records_expected (Integer) -> total_records_expected (Number) - Expected records count
    # records_processed (Integer) -> records_processed (Number) - Processed records count
    # records_successful (Integer) -> records_successful (Number) - Successful records count
    # records_failed (Integer) -> records_failed (Number) - Failed records count
    # processing_notes (Text) -> processing_notes (String) - Processing notes
    # assigned_worker (String) -> assigned_worker (String) - Assigned worker
    # created_at (DateTime) -> created_at (String) - ISO timestamp
    # started_at (DateTime) -> started_at (String) - ISO timestamp
    # completed_at (DateTime) -> completed_at (String) - ISO timestamp
    # updated_at (DateTime) -> updated_at (String) - ISO timestamp
    
    # Complete DynamoDB schema for process_handling table
    SCHEMA = {
        "table_name": TABLE_NAME,
        "key_schema": [
            {
                "AttributeName": "pk",  # Maps to SQLAlchemy 'process_id' field
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
        "request_id": "987fcdeb-51a2-43d7-8f9e-123456789abc",  # Request ID reference
        "project_id": "456e7890-f12a-34b5-c678-901234567def",  # Project ID reference
        "status": "processing",  # Process status
        "priority": 1,  # Process priority
        "total_records_expected": 1000,  # Expected records count
        "records_processed": 750,  # Processed records count
        "records_successful": 720,  # Successful records count
        "records_failed": 30,  # Failed records count
        "processing_notes": "Processing batch 3 of 5. Some validation errors encountered.",  # Processing notes
        "assigned_worker": "worker-node-01",  # Assigned worker
        "created_at": "2024-12-01T10:00:00Z",  # ISO timestamp
        "started_at": "2024-12-01T10:05:00Z",  # ISO timestamp
        "completed_at": None,  # ISO timestamp (null when not completed)
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
        return "Process handling table with primary key only - simple and fast" 