"""
Create Pipeline Executions Table Migration
Created: 2024-12-01T12:26:00
Stage 0 Agent: Pipeline execution history and analytics
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from migrations.migration_manager import BaseMigration
from app.core.database import dynamodb_client
from app.config.settings import settings
from app.config.table_configs.pipeline_executions_table import PipelineExecutionsTableConfig
from app.core.logging import get_logger

logger = get_logger("migration.create_pipeline_executions_table")

class CreatePipelineExecutionsTableMigration(BaseMigration):
    """
    Create Pipeline Executions Table Migration
    Creates the pipeline_executions table for Stage 0 Orchestrator agent
    """
    
    @property
    def description(self) -> str:
        return "Create pipeline_executions table for Stage 0 Orchestrator agent"
    
    async def up(self):
        """Execute the migration"""
        logger.info("Creating pipeline_executions table migration")
        
        try:
            # Get pipeline_executions table schema from configuration
            pipeline_executions_schema = PipelineExecutionsTableConfig.SCHEMA
            table_name = PipelineExecutionsTableConfig.get_table_name()
            
            # Create the pipeline_executions table using schema configuration
            table_created = dynamodb_client.create_table(
                table_name=table_name,
                key_schema=pipeline_executions_schema["key_schema"],
                attribute_definitions=pipeline_executions_schema["attribute_definitions"],
                billing_mode=pipeline_executions_schema["billing_mode"]
            )
            
            if table_created:
                logger.info(f"Successfully created pipeline_executions table: {table_name}")
            else:
                logger.info(f"Pipeline executions table {table_name} already exists")
                
        except Exception as e:
            logger.error(f"Error creating pipeline_executions table: {str(e)}")
            raise
    
    async def down(self):
        """Rollback the migration"""
        logger.info("Rolling back pipeline_executions table creation")
        
        try:
            # Delete the pipeline_executions table
            table_name = PipelineExecutionsTableConfig.get_table_name()
            table_deleted = dynamodb_client.delete_table(table_name)
            
            if table_deleted:
                logger.info(f"Successfully deleted pipeline_executions table: {table_name}")
            else:
                logger.warning(f"Pipeline executions table {table_name} did not exist")
                
        except Exception as e:
            logger.error(f"Error deleting pipeline_executions table: {str(e)}")
            raise 