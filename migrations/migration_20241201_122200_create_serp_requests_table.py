"""
Create SERP Requests Table Migration
Created: 2024-12-01T12:22:00
Stage 0 Agent: SERP search request tracking and metadata
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from migrations.migration_manager import BaseMigration
from app.core.database import dynamodb_client
from app.config.settings import settings
from app.config.table_configs.serp_requests_table import SerpRequestsTableConfig
from app.core.logging import get_logger

logger = get_logger("migration.create_serp_requests_table")

class CreateSerpRequestsTableMigration(BaseMigration):
    """
    Create SERP Requests Table Migration
    Creates the serp_requests table for Stage 0 SERP agent
    """
    
    @property
    def description(self) -> str:
        return "Create serp_requests table for Stage 0 SERP agent"
    
    async def up(self):
        """Execute the migration"""
        logger.info("Creating serp_requests table migration")
        
        try:
            # Get serp_requests table schema from configuration
            serp_requests_schema = SerpRequestsTableConfig.SCHEMA
            table_name = SerpRequestsTableConfig.get_table_name()
            
            # Create the serp_requests table using schema configuration
            table_created = dynamodb_client.create_table(
                table_name=table_name,
                key_schema=serp_requests_schema["key_schema"],
                attribute_definitions=serp_requests_schema["attribute_definitions"],
                billing_mode=serp_requests_schema["billing_mode"]
            )
            
            if table_created:
                logger.info(f"Successfully created serp_requests table: {table_name}")
            else:
                logger.info(f"SERP requests table {table_name} already exists")
                
        except Exception as e:
            logger.error(f"Error creating serp_requests table: {str(e)}")
            raise
    
    async def down(self):
        """Rollback the migration"""
        logger.info("Rolling back serp_requests table creation")
        
        try:
            # Delete the serp_requests table
            table_name = SerpRequestsTableConfig.get_table_name()
            table_deleted = dynamodb_client.delete_table(table_name)
            
            if table_deleted:
                logger.info(f"Successfully deleted serp_requests table: {table_name}")
            else:
                logger.warning(f"SERP requests table {table_name} did not exist")
                
        except Exception as e:
            logger.error(f"Error deleting serp_requests table: {str(e)}")
            raise 