"""
Projects Details Table Configuration
Dedicated configuration for the projects_details table schema and settings
"""

from typing import Dict, Any

class ProjectsTableConfig:
    """Configuration for the projects_details table"""
    
    # Table name (without environment suffix)
    TABLE_NAME = "projects_details"
    
    # Complete DynamoDB schema for projects_details table
    SCHEMA = {
        "table_name": TABLE_NAME,
        "key_schema": [
            {
                "AttributeName": "pk",
                "KeyType": "HASH"  # Partition key
            }
        ],
        "attribute_definitions": [
            {
                "AttributeName": "pk",
                "AttributeType": "S"
            }
        ],
        "billing_mode": "PAY_PER_REQUEST"
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
        return "Project details table with primary key only - simple and fast" 