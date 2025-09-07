"""
Create Project Request Statistics Table Migration
Created: 2024-12-01T12:02:00
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from migrations.migration_manager import BaseMigration
from app.core.database import dynamodb_client
from app.config.settings import settings
from app.config.table_configs.project_request_statistics_table import ProjectRequestStatisticsTableConfig
from app.core.logging import get_logger

logger = get_logger("migration.create_project_request_statistics_table")

class CreateProjectRequestStatisticsTableMigration(BaseMigration):
    """
    Create Project Request Statistics Table Migration
    Creates the project_request_statistics table with proper indexes
    """
    
    @property
    def description(self) -> str:
        return "Create project_request_statistics table with primary key only"
    
    async def up(self):
        """Execute the migration"""
        logger.info("Creating project_request_statistics table migration")
        
        try:
            # Get project request statistics table schema from configuration
            statistics_schema = ProjectRequestStatisticsTableConfig.SCHEMA
            table_name = ProjectRequestStatisticsTableConfig.get_table_name(settings.TABLE_ENVIRONMENT)
            
            # Create the project_request_statistics table using schema configuration
            table_created = dynamodb_client.create_table(
                table_name=table_name,
                key_schema=statistics_schema["key_schema"],
                attribute_definitions=statistics_schema["attribute_definitions"],
                billing_mode=statistics_schema["billing_mode"]
            )
            
            if table_created:
                logger.info(f"Successfully created project_request_statistics table: {table_name}")
            else:
                logger.info(f"Project_request_statistics table {table_name} already exists")
                
        except Exception as e:
            logger.error(f"Error creating project_request_statistics table: {str(e)}")
            raise
    
    async def down(self):
        """Rollback the migration"""
        logger.info("Rolling back project_request_statistics table creation")
        
        try:
            # Delete the project_request_statistics table
            table_name = ProjectRequestStatisticsTableConfig.get_table_name(settings.TABLE_ENVIRONMENT)
            table_deleted = dynamodb_client.delete_table(table_name)
            
            if table_deleted:
                logger.info(f"Successfully deleted project_request_statistics table: {table_name}")
            else:
                logger.warning(f"Project_request_statistics table {table_name} did not exist")
                
        except Exception as e:
            logger.error(f"Error deleting project_request_statistics table: {str(e)}")
            raise 