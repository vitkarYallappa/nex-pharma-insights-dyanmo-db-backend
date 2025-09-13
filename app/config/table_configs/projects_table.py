"""
Projects Details Table Configuration
Dedicated configuration for the projects_details table schema and settings
Matches SQLAlchemy schema structure with DynamoDB NoSQL approach
"""

from typing import Dict, Any

class ProjectsTableConfig:
    """Configuration for the projects_details table"""
    
    # Table name (without environment suffix)
    TABLE_NAME = "projects_details"
    
    # Field mapping from SQLAlchemy to DynamoDB
    # SQLAlchemy -> DynamoDB mapping:
    # id (UUID) -> pk (String) - Primary key
    # name (String) -> name (String) - Project name
    # description (Text) -> description (String) - Project description
    # created_by (UUID) -> created_by (String) - Creator user ID
    # status (String) -> status (String) - Project status
    # project_metadata (JSON) -> project_metadata (Map) - Project metadata
    # module_config (JSON) -> module_config (Map) - Module configuration
    # created_at (DateTime) -> created_at (String) - ISO timestamp
    # updated_at (DateTime) -> updated_at (String) - ISO timestamp
    
    # Complete DynamoDB schema for projects_details table
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
    SAMPLE_ITEM_STRUCTURE = {
        "pk": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",  # Primary key (maps to SQLAlchemy 'id')
        "name": "Project Name",  # Required field
        "description": "Project description text",  # Optional field
        "created_by": "user-uuid-string",  # Required - creator user ID
        "status": "active",  # Optional - project status (active, inactive, completed, etc.)
        "project_metadata": {  # Optional - JSON object for project metadata
            "tags": ["tag1", "tag2"],
            "priority": "high",
            "category": "research"
        },
        "module_config": {  # Optional - JSON object for module configuration
            "enabled_modules": ["module1", "module2"],
            "settings": {"key": "value"}
        },
        "created_at": "2024-12-01T12:00:00Z",  # ISO timestamp string
        "updated_at": "2024-12-01T12:00:00Z"   # ISO timestamp string
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
        return "Project details table matching SQLAlchemy schema - stores project info, metadata, and configuration" 