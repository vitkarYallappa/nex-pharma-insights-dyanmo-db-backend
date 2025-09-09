"""
Create Pipeline States Table Migration
Created: 2024-12-01T12:25:00
Stage 0 Agent: Pipeline orchestration state tracking
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from migrations.migration_manager import BaseMigration
from app.core.database import dynamodb_client
from app.config.settings import settings
from app.config.table_configs.pipeline_states_table import PipelineStatesTableConfig
from app.core.logging import get_logger

logger = get_logger("migration.create_pipeline_states_table")

class CreatePipelineStatesTableMigration(BaseMigration):
    """
    Create Pipeline States Table Migration
    Creates the pipeline_states table for Stage 0 Orchestrator agent
    """
    
    @property
    def description(self) -> str:
        return "Create pipeline_states table for Stage 0 Orchestrator agent"
    
    async def up(self):
        """Execute the migration"""
        logger.info("Creating pipeline_states table migration")
        
        try:
            # Get pipeline_states table schema from configuration
            pipeline_states_schema = PipelineStatesTableConfig.SCHEMA
            table_name = PipelineStatesTableConfig.get_table_name(settings.TABLE_ENVIRONMENT)
            
            # Create the pipeline_states table using schema configuration
            table_created = dynamodb_client.create_table(
                table_name=table_name,
                key_schema=pipeline_states_schema["key_schema"],
                attribute_definitions=pipeline_states_schema["attribute_definitions"],
                billing_mode=pipeline_states_schema["billing_mode"]
            )
            
            if table_created:
                logger.info(f"Successfully created pipeline_states table: {table_name}")
            else:
                logger.info(f"Pipeline states table {table_name} already exists")
                
        except Exception as e:
            logger.error(f"Error creating pipeline_states table: {str(e)}")
            raise
    
    async def down(self):
        """Rollback the migration"""
        logger.info("Rolling back pipeline_states table creation")
        
        try:
            # Delete the pipeline_states table
            table_name = PipelineStatesTableConfig.get_table_name(settings.TABLE_ENVIRONMENT)
            table_deleted = dynamodb_client.delete_table(table_name)
            
            if table_deleted:
                logger.info(f"Successfully deleted pipeline_states table: {table_name}")
            else:
                logger.warning(f"Pipeline states table {table_name} did not exist")
                
        except Exception as e:
            logger.error(f"Error deleting pipeline_states table: {str(e)}")
            raise 