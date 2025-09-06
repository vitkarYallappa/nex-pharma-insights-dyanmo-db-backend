"""
Create Projects Details Table Migration
Created: 2024-12-01T12:01:00
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from migrations.migration_manager import BaseMigration
from app.core.database import dynamodb_client
from app.config.settings import settings
from app.config.table_configs.projects_table import ProjectsTableConfig
from app.core.logging import get_logger

logger = get_logger("migration.create_projects_table")

class CreateProjectsTableMigration(BaseMigration):
    """
    Create Projects Details Table Migration
    Creates the projects_details table with proper indexes
    """
    
    @property
    def description(self) -> str:
        return "Create projects_details table with primary key only"
    
    async def up(self):
        """Execute the migration"""
        logger.info("Creating projects_details table migration")
        
        try:
            # Get projects table schema from configuration
            projects_schema = ProjectsTableConfig.SCHEMA
            table_name = ProjectsTableConfig.get_table_name(settings.TABLE_ENVIRONMENT)
            
            # Create the projects_details table using schema configuration
            table_created = dynamodb_client.create_table(
                table_name=table_name,
                key_schema=projects_schema["key_schema"],
                attribute_definitions=projects_schema["attribute_definitions"],
                billing_mode=projects_schema["billing_mode"]
            )
            
            if table_created:
                logger.info(f"Successfully created projects_details table: {table_name}")
            else:
                logger.info(f"Projects_details table {table_name} already exists")
                
        except Exception as e:
            logger.error(f"Error creating projects_details table: {str(e)}")
            raise
    
    async def down(self):
        """Rollback the migration"""
        logger.info("Rolling back projects_details table creation")
        
        try:
            # Delete the projects_details table
            table_name = ProjectsTableConfig.get_table_name(settings.TABLE_ENVIRONMENT)
            table_deleted = dynamodb_client.delete_table(table_name)
            
            if table_deleted:
                logger.info(f"Successfully deleted projects_details table: {table_name}")
            else:
                logger.warning(f"Projects_details table {table_name} did not exist")
                
        except Exception as e:
            logger.error(f"Error deleting projects_details table: {str(e)}")
            raise 