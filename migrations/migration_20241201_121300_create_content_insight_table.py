"""
Create Content Insight Table Migration
Created: 2024-12-01T12:13:00
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from migrations.migration_manager import BaseMigration
from app.core.database import dynamodb_client
from app.config.settings import settings
from app.config.table_configs.content_insight_table import ContentInsightTableConfig
from app.core.logging import get_logger

logger = get_logger("migration.create_content_insight_table")

class CreateContentInsightTableMigration(BaseMigration):
    """
    Create Content Insight Table Migration
    Creates the content_insight table with proper indexes
    """
    
    @property
    def description(self) -> str:
        return "Create content_insight table with primary key only"
    
    async def up(self):
        """Execute the migration"""
        logger.info("Creating content_insight table migration")
        
        try:
            # Get content insight table schema from configuration
            insight_schema = ContentInsightTableConfig.SCHEMA
            table_name = ContentInsightTableConfig.get_table_name(settings.TABLE_ENVIRONMENT)
            
            # Create the content_insight table using schema configuration
            table_created = dynamodb_client.create_table(
                table_name=table_name,
                key_schema=insight_schema["key_schema"],
                attribute_definitions=insight_schema["attribute_definitions"],
                billing_mode=insight_schema["billing_mode"]
            )
            
            if table_created:
                logger.info(f"Successfully created content_insight table: {table_name}")
            else:
                logger.info(f"Content_insight table {table_name} already exists")
                
        except Exception as e:
            logger.error(f"Error creating content_insight table: {str(e)}")
            raise
    
    async def down(self):
        """Rollback the migration"""
        logger.info("Rolling back content_insight table creation")
        
        try:
            # Delete the content_insight table
            table_name = ContentInsightTableConfig.get_table_name(settings.TABLE_ENVIRONMENT)
            table_deleted = dynamodb_client.delete_table(table_name)
            
            if table_deleted:
                logger.info(f"Successfully deleted content_insight table: {table_name}")
            else:
                logger.warning(f"Content_insight table {table_name} did not exist")
                
        except Exception as e:
            logger.error(f"Error deleting content_insight table: {str(e)}")
            raise 