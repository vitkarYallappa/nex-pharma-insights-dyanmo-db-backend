"""
Users Table Configuration
Dedicated configuration for the users table schema and settings
"""

from typing import Dict, Any

class UsersTableConfig:
    """Configuration for the users table"""
    
    # Table name (no environment suffix)
    TABLE_NAME = "users"
    
    # Complete DynamoDB schema for users table
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
        return "User management table with primary key only - simple and fast" 