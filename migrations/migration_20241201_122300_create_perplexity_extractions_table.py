"""
Create Perplexity Extractions Table Migration
Created: 2024-12-01T12:23:00
Stage 0 Agent: Perplexity content extraction tracking
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from migrations.migration_manager import BaseMigration
from app.core.database import dynamodb_client
from app.config.settings import settings
from app.config.table_configs.perplexity_extractions_table import PerplexityExtractionsTableConfig
from app.core.logging import get_logger

logger = get_logger("migration.create_perplexity_extractions_table")

class CreatePerplexityExtractionsTableMigration(BaseMigration):
    """
    Create Perplexity Extractions Table Migration
    Creates the perplexity_extractions table for Stage 0 Perplexity agent
    """
    
    @property
    def description(self) -> str:
        return "Create perplexity_extractions table for Stage 0 Perplexity agent"
    
    async def up(self):
        """Execute the migration"""
        logger.info("Creating perplexity_extractions table migration")
        
        try:
            # Get perplexity_extractions table schema from configuration
            perplexity_extractions_schema = PerplexityExtractionsTableConfig.SCHEMA
            table_name = PerplexityExtractionsTableConfig.get_table_name(settings.TABLE_ENVIRONMENT)
            
            # Create the perplexity_extractions table using schema configuration
            table_created = dynamodb_client.create_table(
                table_name=table_name,
                key_schema=perplexity_extractions_schema["key_schema"],
                attribute_definitions=perplexity_extractions_schema["attribute_definitions"],
                billing_mode=perplexity_extractions_schema["billing_mode"]
            )
            
            if table_created:
                logger.info(f"Successfully created perplexity_extractions table: {table_name}")
            else:
                logger.info(f"Perplexity extractions table {table_name} already exists")
                
        except Exception as e:
            logger.error(f"Error creating perplexity_extractions table: {str(e)}")
            raise
    
    async def down(self):
        """Rollback the migration"""
        logger.info("Rolling back perplexity_extractions table creation")
        
        try:
            # Delete the perplexity_extractions table
            table_name = PerplexityExtractionsTableConfig.get_table_name(settings.TABLE_ENVIRONMENT)
            table_deleted = dynamodb_client.delete_table(table_name)
            
            if table_deleted:
                logger.info(f"Successfully deleted perplexity_extractions table: {table_name}")
            else:
                logger.warning(f"Perplexity extractions table {table_name} did not exist")
                
        except Exception as e:
            logger.error(f"Error deleting perplexity_extractions table: {str(e)}")
            raise 