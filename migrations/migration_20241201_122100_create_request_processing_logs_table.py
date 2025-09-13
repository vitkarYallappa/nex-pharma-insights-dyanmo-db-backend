"""
Create Request Processing Logs Table Migration
Created: 2024-12-01T12:21:00
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from migrations.migration_manager import BaseMigration
from app.core.database import dynamodb_client
from app.config.settings import settings
from app.config.table_configs.request_processing_logs_table import RequestProcessingLogsTableConfig
from app.core.logging import get_logger

logger = get_logger("migration.create_request_processing_logs_table")

class CreateRequestProcessingLogsTableMigration(BaseMigration):
    """
    Create Request Processing Logs Table Migration
    Creates the request processing logs table for the Root Orchestrator
    """
    
    @property
    def description(self) -> str:
        return "Create request processing logs table for Root Orchestrator audit trail"
    
    async def up(self):
        """Execute the migration"""
        logger.info("Creating request processing logs table migration")
        
        try:
            # Get table schema from configuration
            table_schema = RequestProcessingLogsTableConfig.SCHEMA
            table_name = RequestProcessingLogsTableConfig.get_table_name()
            
            # Create the table
            table_created = dynamodb_client.create_table(
                table_name=table_name,
                key_schema=table_schema["key_schema"],
                attribute_definitions=table_schema["attribute_definitions"],
                billing_mode=table_schema["billing_mode"]
            )
            
            if table_created:
                logger.info(f"Successfully created request processing logs table: {table_name}")
            else:
                logger.info(f"Request processing logs table {table_name} already exists")
                
            # Add some initial test data if in development
            await self._create_initial_data()
            
        except Exception as e:
            logger.error(f"Error creating request processing logs table: {str(e)}")
            raise
    
    async def down(self):
        """Rollback the migration"""
        logger.info("Rolling back request processing logs table creation")
        
        try:
            # Delete the table
            table_name = RequestProcessingLogsTableConfig.get_table_name()
            table_deleted = dynamodb_client.delete_table(table_name)
            
            if table_deleted:
                logger.info(f"Successfully deleted request processing logs table: {table_name}")
            else:
                logger.warning(f"Request processing logs table {table_name} did not exist")
                
        except Exception as e:
            logger.error(f"Error deleting request processing logs table: {str(e)}")
            raise
    
    async def _create_initial_data(self):
        """Create initial test data for development"""
        if not settings.is_development:
            return
            
        logger.info("Creating initial test data for request processing logs")
        
        try:
            from datetime import datetime
            import uuid
            
            table_name = RequestProcessingLogsTableConfig.get_table_name()
            table = dynamodb_client.get_table(table_name)
            
            # Create sample log entries
            sample_logs = [
                {
                    "log_id": f"log_{int(datetime.now().timestamp() * 1000)}_001",
                    "request_id": "req_sample_test_001",
                    "timestamp": datetime.now().isoformat(),
                    "log_level": "INFO",
                    "message": "Request processing initialized",
                    "stage": "initialization",
                    "metadata": {
                        "worker_id": "table_processor_001",
                        "processing_node": "node-1",
                        "test_data": True
                    }
                },
                {
                    "log_id": f"log_{int(datetime.now().timestamp() * 1000)}_002",
                    "request_id": "req_sample_test_001",
                    "timestamp": datetime.now().isoformat(),
                    "log_level": "INFO",
                    "message": "Starting content extraction phase",
                    "stage": "content_extraction",
                    "metadata": {
                        "worker_id": "table_processor_001",
                        "processing_node": "node-1",
                        "urls_to_process": 15,
                        "test_data": True
                    }
                },
                {
                    "log_id": f"log_{int(datetime.now().timestamp() * 1000)}_003",
                    "request_id": "req_sample_test_001",
                    "timestamp": datetime.now().isoformat(),
                    "log_level": "WARNING",
                    "message": "Low confidence score detected for source",
                    "stage": "content_extraction",
                    "metadata": {
                        "worker_id": "table_processor_001",
                        "processing_node": "node-1",
                        "source_url": "https://example.com/test",
                        "confidence_score": 0.45,
                        "test_data": True
                    }
                }
            ]
            
            # Insert sample log entries
            for log_entry in sample_logs:
                try:
                    # Check if log entry already exists
                    existing = table.get_item(Key={'log_id': log_entry['log_id']})
                    if 'Item' not in existing:
                        table.put_item(Item=log_entry)
                        logger.info(f"Created sample log entry: {log_entry['log_id']}")
                    else:
                        logger.info(f"Sample log entry {log_entry['log_id']} already exists")
                except Exception as e:
                    logger.warning(f"Could not create sample log entry {log_entry['log_id']}: {str(e)}")
                
        except Exception as e:
            logger.warning(f"Could not create initial data (this is normal if running for the first time): {str(e)}") 