"""
Create Process Handling Table Migration
Created: 2024-12-01T12:10:00
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from migrations.migration_manager import BaseMigration
from app.core.database import dynamodb_client
from app.config.settings import settings
from app.config.table_configs.process_handling_table import ProcessHandlingTableConfig
from app.core.logging import get_logger

logger = get_logger("migration.create_process_handling_table")

class CreateProcessHandlingTableMigration(BaseMigration):
    """
    Create Process Handling Table Migration
    Creates the process_handling table with proper indexes
    """
    
    @property
    def description(self) -> str:
        return "Create process_handling table with primary key only"
    
    async def up(self):
        """Execute the migration"""
        logger.info("Creating process_handling table migration")
        
        try:
            # Get process handling table schema from configuration
            process_schema = ProcessHandlingTableConfig.SCHEMA
            table_name = ProcessHandlingTableConfig.get_table_name(settings.TABLE_ENVIRONMENT)
            
            # Create the process_handling table using schema configuration
            table_created = dynamodb_client.create_table(
                table_name=table_name,
                key_schema=process_schema["key_schema"],
                attribute_definitions=process_schema["attribute_definitions"],
                billing_mode=process_schema["billing_mode"]
            )
            
            if table_created:
                logger.info(f"Successfully created process_handling table: {table_name}")
            else:
                logger.info(f"Process_handling table {table_name} already exists")
                
            # Add some initial data if needed
            # await self._create_initial_data()
                
        except Exception as e:
            logger.error(f"Error creating process_handling table: {str(e)}")
            raise
    
    async def down(self):
        """Rollback the migration"""
        logger.info("Rolling back process_handling table creation")
        
        try:
            # Delete the process_handling table
            table_name = ProcessHandlingTableConfig.get_table_name(settings.TABLE_ENVIRONMENT)
            table_deleted = dynamodb_client.delete_table(table_name)
            
            if table_deleted:
                logger.info(f"Successfully deleted process_handling table: {table_name}")
            else:
                logger.warning(f"Process_handling table {table_name} did not exist")
                
        except Exception as e:
            logger.error(f"Error deleting process_handling table: {str(e)}")
            raise
    
    async def _create_initial_data(self):
        """Create initial test data for development"""
        if not settings.is_development:
            return
            
        logger.info("Creating initial test data for process handling")
        
        try:
            from app.repositories.process_handling_repository import ProcessHandlingRepository
            from app.repositories.requests_repository import RequestsRepository
            from app.models.process_handling_model import ProcessHandlingModel
            from datetime import datetime, timedelta
            import random
            
            process_repo = ProcessHandlingRepository()
            requests_repo = RequestsRepository()
            
            # Get existing requests to create process handling records for
            requests = await requests_repo.find_all_by_query()
            
            if requests:
                for request in requests[:3]:  # Limit to first 3 requests
                    # Check if process handling already exists for this request
                    process_exists = await process_repo.exists({"request_id": request.pk})
                    
                    if not process_exists:
                        process = ProcessHandlingModel.create_new(
                            request_id=request.pk,
                            project_id=request.project_id,
                            process_type=random.choice(["content_analysis", "insight_generation", "implication_analysis"]),
                            process_status=random.choice(["pending", "running", "completed", "failed"]),
                            priority_level=random.choice(["low", "medium", "high"]),
                            estimated_completion_time=(datetime.utcnow() + timedelta(hours=random.randint(1, 24))).isoformat(),
                            process_metadata={
                                "worker_id": f"worker_{random.randint(1, 10)}",
                                "retry_count": random.randint(0, 3),
                                "resource_usage": {
                                    "cpu_percent": random.uniform(10, 80),
                                    "memory_mb": random.randint(100, 2000)
                                }
                            }
                        )
                        
                        await process_repo.create(process)
                        logger.info(f"Created process handling record for request: {request.title}")
                
        except Exception as e:
            logger.warning(f"Could not create initial process handling data: {str(e)}") 