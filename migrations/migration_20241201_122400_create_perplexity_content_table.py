"""
Create Perplexity Content Table Migration
Created: 2024-12-01T12:24:00
Stage 0 Agent: Individual content extraction results
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from migrations.migration_manager import BaseMigration
from app.core.database import dynamodb_client
from app.config.settings import settings
from app.config.table_configs.perplexity_content_table import PerplexityContentTableConfig
from app.core.logging import get_logger

logger = get_logger("migration.create_perplexity_content_table")

class CreatePerplexityContentTableMigration(BaseMigration):
    """
    Create Perplexity Content Table Migration
    Creates the perplexity_content table for Stage 0 Perplexity agent
    """
    
    @property
    def description(self) -> str:
        return "Create perplexity_content table for Stage 0 Perplexity agent"
    
    async def up(self):
        """Execute the migration"""
        logger.info("Creating perplexity_content table migration")
        
        try:
            # Get perplexity_content table schema from configuration
            perplexity_content_schema = PerplexityContentTableConfig.SCHEMA
            table_name = PerplexityContentTableConfig.get_table_name(settings.TABLE_ENVIRONMENT)
            
            # Create the perplexity_content table using schema configuration
            table_created = dynamodb_client.create_table(
                table_name=table_name,
                key_schema=perplexity_content_schema["key_schema"],
                attribute_definitions=perplexity_content_schema["attribute_definitions"],
                billing_mode=perplexity_content_schema["billing_mode"]
            )
            
            if table_created:
                logger.info(f"Successfully created perplexity_content table: {table_name}")
            else:
                logger.info(f"Perplexity content table {table_name} already exists")
                
        except Exception as e:
            logger.error(f"Error creating perplexity_content table: {str(e)}")
            raise
    
    async def down(self):
        """Rollback the migration"""
        logger.info("Rolling back perplexity_content table creation")
        
        try:
            # Delete the perplexity_content table
            table_name = PerplexityContentTableConfig.get_table_name(settings.TABLE_ENVIRONMENT)
            table_deleted = dynamodb_client.delete_table(table_name)
            
            if table_deleted:
                logger.info(f"Successfully deleted perplexity_content table: {table_name}")
            else:
                logger.warning(f"Perplexity content table {table_name} did not exist")
                
        except Exception as e:
            logger.error(f"Error deleting perplexity_content table: {str(e)}")
            raise 