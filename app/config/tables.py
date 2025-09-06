"""
DynamoDB Table Configuration
Simplified configuration for only required tables: users and projects_details
"""

from typing import Dict, List, Any
from enum import Enum
from .table_configs.users_table import UsersTableConfig
from .table_configs.projects_table import ProjectsTableConfig

class TableEnvironment(str, Enum):
    """Table environment suffixes"""
    LOCAL = "local"
    DEVELOPMENT = "dev" 
    STAGING = "staging"
    PRODUCTION = "prod"

class TableNames:
    """Centralized table name management for required tables only"""
    
    # Base table names
    USERS = "users"
    PROJECTS_DETAILS = "projects_details"
    
    @classmethod
    def get_table_name(cls, base_name: str, environment: str = "local") -> str:
        """Get full table name with environment suffix"""
        return f"{base_name}-{environment}"
    
    @classmethod
    def get_users_table(cls, environment: str = "local") -> str:
        """Get users table name for environment"""
        return UsersTableConfig.get_table_name(environment)
    
    @classmethod
    def get_projects_table(cls, environment: str = "local") -> str:
        """Get projects_details table name for environment"""
        return ProjectsTableConfig.get_table_name(environment)

class TableConfig:
    """Main table configuration class for required tables only"""
    
    def __init__(self, environment: str = "local"):
        self.environment = environment
    
    def get_table_name(self, base_name: str) -> str:
        """Get full table name with environment suffix"""
        return TableNames.get_table_name(base_name, self.environment)
    
    def get_schema(self, table_name: str) -> Dict[str, Any]:
        """Get table schema by name"""
        if table_name == TableNames.USERS:
            return UsersTableConfig.get_schema(self.environment)
        elif table_name == TableNames.PROJECTS_DETAILS:
            return ProjectsTableConfig.get_schema(self.environment)
        else:
            raise ValueError(f"Schema not found for table: {table_name}. Available tables: {self.list_available_tables()}")
    
    def get_all_schemas(self) -> Dict[str, Dict[str, Any]]:
        """Get all table schemas with environment-specific names"""
        return {
            UsersTableConfig.get_table_name(self.environment): UsersTableConfig.get_schema(self.environment),
            ProjectsTableConfig.get_table_name(self.environment): ProjectsTableConfig.get_schema(self.environment)
        }
    
    def list_table_names(self) -> List[str]:
        """List all table names for current environment"""
        return [
            UsersTableConfig.get_table_name(self.environment),
            ProjectsTableConfig.get_table_name(self.environment)
        ]
    
    def list_available_tables(self) -> List[str]:
        """List available base table names"""
        return [TableNames.USERS, TableNames.PROJECTS_DETAILS]
    
    def get_table_info(self) -> Dict[str, Dict[str, Any]]:
        """Get information about all available tables"""
        return {
            TableNames.USERS: {
                "name": UsersTableConfig.get_table_name(self.environment),
                "description": UsersTableConfig.get_description(),
                "indexes": 0  # No GSIs - primary key only
            },
            TableNames.PROJECTS_DETAILS: {
                "name": ProjectsTableConfig.get_table_name(self.environment),
                "description": ProjectsTableConfig.get_description(),
                "indexes": 0  # No GSIs - primary key only
            }
        }

# Default table configuration instance
table_config = TableConfig()

# Backward compatibility exports
TableSchemas = type('TableSchemas', (), {
    'USERS_SCHEMA': UsersTableConfig.SCHEMA,
    'PROJECTS_SCHEMA': ProjectsTableConfig.SCHEMA
}) 