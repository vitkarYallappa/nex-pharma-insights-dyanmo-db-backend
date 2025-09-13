"""
DynamoDB Table Configuration
Simplified configuration for only required tables: users and projects_details
"""

from typing import Dict, List, Any
from enum import Enum
from .table_configs.users_table import UsersTableConfig
from .table_configs.projects_table import ProjectsTableConfig

class TableEnvironment(str, Enum):
    """Table environment suffixes - DEPRECATED: No longer used"""
    LOCAL = "local"
    DEVELOPMENT = "dev" 
    PRODUCTION = "prod"

class TableNames:
    """Centralized table name management for required tables only"""
    
    # Base table names
    USERS = "users"
    PROJECTS_DETAILS = "projects_details"
    
    @classmethod
    def get_table_name(cls, base_name: str, environment: str = None) -> str:
        """Get table name without environment suffix"""
        return base_name
    
    @classmethod
    def get_users_table(cls, environment: str = None) -> str:
        """Get users table name"""
        return UsersTableConfig.get_table_name()
    
    @classmethod
    def get_projects_table(cls, environment: str = None) -> str:
        """Get projects_details table name"""
        return ProjectsTableConfig.get_table_name()

class TableConfig:
    """Main table configuration class for required tables only"""
    
    def __init__(self, environment: str = None):
        # Environment parameter kept for backward compatibility but not used
        self.environment = environment
    
    def get_table_name(self, base_name: str) -> str:
        """Get table name without environment suffix"""
        return base_name
    
    def get_schema(self, table_name: str) -> Dict[str, Any]:
        """Get table schema by name"""
        if table_name == TableNames.USERS:
            return UsersTableConfig.get_schema()
        elif table_name == TableNames.PROJECTS_DETAILS:
            return ProjectsTableConfig.get_schema()
        else:
            raise ValueError(f"Schema not found for table: {table_name}. Available tables: {self.list_available_tables()}")
    
    def get_all_schemas(self) -> Dict[str, Dict[str, Any]]:
        """Get all table schemas without environment-specific names"""
        return {
            UsersTableConfig.get_table_name(): UsersTableConfig.get_schema(),
            ProjectsTableConfig.get_table_name(): ProjectsTableConfig.get_schema()
        }
    
    def list_table_names(self) -> List[str]:
        """List all table names without environment suffixes"""
        return [
            UsersTableConfig.get_table_name(),
            ProjectsTableConfig.get_table_name()
        ]
    
    def list_available_tables(self) -> List[str]:
        """List available base table names"""
        return [TableNames.USERS, TableNames.PROJECTS_DETAILS]
    
    def get_table_info(self) -> Dict[str, Dict[str, Any]]:
        """Get information about all available tables"""
        return {
            "users": {
                "table_name": UsersTableConfig.get_table_name(),
                "description": UsersTableConfig.get_description(),
                "schema": UsersTableConfig.get_schema()
            },
            "projects_details": {
                "table_name": ProjectsTableConfig.get_table_name(),
                "description": ProjectsTableConfig.get_description(),
                "schema": ProjectsTableConfig.get_schema()
            }
        }

# Default table configuration instance
table_config = TableConfig()

# Backward compatibility exports
TableSchemas = type('TableSchemas', (), {
    'USERS_SCHEMA': UsersTableConfig.SCHEMA,
    'PROJECTS_SCHEMA': ProjectsTableConfig.SCHEMA
}) 