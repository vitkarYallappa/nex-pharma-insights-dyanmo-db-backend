"""
Create Implication Comment Table Migration
Created: 2024-12-01T12:17:00
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from migrations.migration_manager import BaseMigration
from app.core.database import dynamodb_client
from app.config.settings import settings
from app.config.table_configs.implication_comment_table import ImplicationCommentTableConfig
from app.core.logging import get_logger

logger = get_logger("migration.create_implication_comment_table")

class CreateImplicationCommentTableMigration(BaseMigration):
    """
    Create Implication Comment Table Migration
    Creates the implication_comment table with proper indexes
    """
    
    @property
    def description(self) -> str:
        return "Create implication_comment table with primary key only"
    
    async def up(self):
        """Execute the migration"""
        logger.info("Creating implication_comment table migration")
        
        try:
            # Get implication comment table schema from configuration
            comment_schema = ImplicationCommentTableConfig.SCHEMA
            table_name = ImplicationCommentTableConfig.get_table_name()
            
            # Create the implication_comment table using schema configuration
            table_created = dynamodb_client.create_table(
                table_name=table_name,
                key_schema=comment_schema["key_schema"],
                attribute_definitions=comment_schema["attribute_definitions"],
                billing_mode=comment_schema["billing_mode"]
            )
            
            if table_created:
                logger.info(f"Successfully created implication_comment table: {table_name}")
            else:
                logger.info(f"Implication_comment table {table_name} already exists")
                
        
            # Add some initial data if needed
            # await self._create_initial_data()
                
        except Exception as e:
            logger.error(f"Error creating implication_comment table: {str(e)}")
            raise
    
    async def down(self):
        """Rollback the migration"""
        logger.info("Rolling back implication_comment table creation")
        
        try:
            # Delete the implication_comment table
            table_name = ImplicationCommentTableConfig.get_table_name()
            table_deleted = dynamodb_client.delete_table(table_name)
            
            if table_deleted:
                logger.info(f"Successfully deleted implication_comment table: {table_name}")
            else:
                logger.warning(f"Implication_comment table {table_name} did not exist")
                
        except Exception as e:
            logger.error(f"Error deleting implication_comment table: {str(e)}")
            raise
    async def _create_initial_data(self):
        """Create initial test data for development"""
        if not settings.is_development:
            return
            
        logger.info("Creating initial test data")
        
        try:
            # Placeholder for content-related tables
            # Actual implementation would depend on the specific table structure
            logger.info("Initial data creation placeholder - table ready for use")
                
        except Exception as e:
            logger.warning(f"Could not create initial data: {str(e)}") 