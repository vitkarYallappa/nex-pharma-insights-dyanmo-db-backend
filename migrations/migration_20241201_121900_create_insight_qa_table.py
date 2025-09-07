"""
Create Insight QA Table Migration
Created: 2024-12-01T12:19:00
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from migrations.migration_manager import BaseMigration
from app.core.database import dynamodb_client
from app.config.settings import settings
from app.config.table_configs.insight_qa_table import InsightQaTableConfig
from app.core.logging import get_logger

logger = get_logger("migration.create_insight_qa_table")

class CreateInsightQaTableMigration(BaseMigration):
    """
    Create Insight QA Table Migration
    Creates the insight_qa table with proper indexes
    """
    
    @property
    def description(self) -> str:
        return "Create insight_qa table with primary key only"
    
    async def up(self):
        """Execute the migration"""
        logger.info("Creating insight_qa table migration")
        
        try:
            # Get insight qa table schema from configuration
            qa_schema = InsightQaTableConfig.SCHEMA
            table_name = InsightQaTableConfig.get_table_name(settings.TABLE_ENVIRONMENT)
            
            # Create the insight_qa table using schema configuration
            table_created = dynamodb_client.create_table(
                table_name=table_name,
                key_schema=qa_schema["key_schema"],
                attribute_definitions=qa_schema["attribute_definitions"],
                billing_mode=qa_schema["billing_mode"]
            )
            
            if table_created:
                logger.info(f"Successfully created insight_qa table: {table_name}")
            else:
                logger.info(f"Insight_qa table {table_name} already exists")
                
        
            # Add some initial data if needed
            await self._create_initial_data()
                
        except Exception as e:
            logger.error(f"Error creating insight_qa table: {str(e)}")
            raise
    
    async def down(self):
        """Rollback the migration"""
        logger.info("Rolling back insight_qa table creation")
        
        try:
            # Delete the insight_qa table
            table_name = InsightQaTableConfig.get_table_name(settings.TABLE_ENVIRONMENT)
            table_deleted = dynamodb_client.delete_table(table_name)
            
            if table_deleted:
                logger.info(f"Successfully deleted insight_qa table: {table_name}")
            else:
                logger.warning(f"Insight_qa table {table_name} did not exist")
                
        except Exception as e:
            logger.error(f"Error deleting insight_qa table: {str(e)}")
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