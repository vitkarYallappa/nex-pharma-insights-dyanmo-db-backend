"""
Project Modules Statistics Table Configuration
Dedicated configuration for the project_modules_statistics table schema and settings
Matches SQLAlchemy schema structure with DynamoDB NoSQL approach
"""

from typing import Dict, Any

class ProjectModulesStatisticsTableConfig:
    """Configuration for the project_modules_statistics table"""
    
    # Table name (without environment suffix)
    TABLE_NAME = "project_modules_statistics"
    
    # Field mapping from SQLAlchemy to DynamoDB
    # SQLAlchemy -> DynamoDB mapping:
    # id (UUID) -> pk (String) - Primary key
    # project_id (UUID) -> project_id (String) - Project ID reference
    # total_insights (Integer) -> total_insights (Number) - Total insights count
    # total_implication (Integer) -> total_implication (Number) - Total implication count
    # created_at (DateTime) -> created_at (String) - ISO timestamp
    # updated_at (DateTime) -> updated_at (String) - ISO timestamp
    
    # Complete DynamoDB schema for project_modules_statistics table
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
        "total_insights": 25,  # Total insights count
        "total_implication": 18,  # Total implication count
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
        return "Project modules statistics table with primary key only - simple and fast" 