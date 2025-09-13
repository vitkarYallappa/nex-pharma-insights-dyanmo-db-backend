"""
Create Market Intelligence Requests Table Migration
Created: 2024-12-01T12:20:00
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from migrations.migration_manager import BaseMigration
from app.core.database import dynamodb_client
from app.config.settings import settings
from app.config.table_configs.market_intelligence_requests_table import MarketIntelligenceRequestsTableConfig
from app.core.logging import get_logger

logger = get_logger("migration.create_market_intelligence_requests_table")

class CreateMarketIntelligenceRequestsTableMigration(BaseMigration):
    """
    Create Market Intelligence Requests Table Migration
    Creates the main market intelligence requests table for the Root Orchestrator
    """
    
    @property
    def description(self) -> str:
        return "Create market intelligence requests table for Root Orchestrator"
    
    async def up(self):
        """Execute the migration"""
        logger.info("Creating market intelligence requests table migration")
        
        try:
            # Get table schema from configuration
            table_schema = MarketIntelligenceRequestsTableConfig.SCHEMA
            table_name = MarketIntelligenceRequestsTableConfig.get_table_name()
            
            # Create the table
            table_created = dynamodb_client.create_table(
                table_name=table_name,
                key_schema=table_schema["key_schema"],
                attribute_definitions=table_schema["attribute_definitions"],
                billing_mode=table_schema["billing_mode"]
            )
            
            if table_created:
                logger.info(f"Successfully created market intelligence requests table: {table_name}")
            else:
                logger.info(f"Market intelligence requests table {table_name} already exists")
                
            # Add some initial test data if in development
            await self._create_initial_data()
            
        except Exception as e:
            logger.error(f"Error creating market intelligence requests table: {str(e)}")
            raise
    
    async def down(self):
        """Rollback the migration"""
        logger.info("Rolling back market intelligence requests table creation")
        
        try:
            # Delete the table
            table_name = MarketIntelligenceRequestsTableConfig.get_table_name()
            table_deleted = dynamodb_client.delete_table(table_name)
            
            if table_deleted:
                logger.info(f"Successfully deleted market intelligence requests table: {table_name}")
            else:
                logger.warning(f"Market intelligence requests table {table_name} did not exist")
                
        except Exception as e:
            logger.error(f"Error deleting market intelligence requests table: {str(e)}")
            raise
    
    async def _create_initial_data(self):
        """Create initial test data for development"""
        if not settings.is_development:
            return
            
        logger.info("Creating initial test data for market intelligence requests")
        
        try:
            from datetime import datetime
            import uuid
            
            table_name = MarketIntelligenceRequestsTableConfig.get_table_name()
            table = dynamodb_client.get_table(table_name)
            
            # Create a sample request
            sample_request = {
                "request_id": f"req_{int(datetime.now().timestamp() * 1000)}_{str(uuid.uuid4())[:8]}",
                "project_id": "test-project-001",
                "user_id": "test-user-123",
                "request_type": "semaglutide_intelligence",
                "status": "pending",
                "status_message": None,
                "priority": "high",
                "processing_strategy": "table",
                "config": {
                    "keywords": [
                        "semaglutide",
                        "tirzepatide", 
                        "wegovy",
                        "obesity drug",
                        "weight loss medication",
                        "GLP-1 receptor agonist",
                        "diabetes treatment",
                        "clinical trials obesity"
                    ],
                    "sources": [
                        {
                            "name": "FDA",
                            "base_url": "https://www.fda.gov",
                            "source_type": "government"
                        },
                        {
                            "name": "NIH", 
                            "base_url": "https://www.nih.gov",
                            "source_type": "academic"
                        },
                        {
                            "name": "ClinicalTrials.gov",
                            "base_url": "https://clinicaltrials.gov", 
                            "source_type": "clinical"
                        }
                    ],
                    "extraction_mode": "summary",
                    "quality_threshold": 0.7,
                    "batch_size": 5,
                    "max_retries": 2,
                    "custom_params": {}
                },
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "started_at": None,
                "completed_at": None,
                "progress": {
                    "current_stage": "initialization",
                    "percentage": 0.0,
                    "urls_found": 0,
                    "content_extracted": 0,
                    "processing_errors": 0,
                    "estimated_completion": None,
                    "last_updated": datetime.now().isoformat()
                },
                "results": {},
                "errors": [],
                "warnings": [],
                "processing_metadata": {
                    "test_run": True,
                    "timestamp": datetime.now().isoformat(),
                    "status_history": [
                        {
                            "timestamp": datetime.now().isoformat(),
                            "old_status": None,
                            "new_status": "pending",
                            "message": "Request created"
                        }
                    ]
                }
            }
            
            # Check if sample data already exists
            try:
                existing = table.get_item(Key={'request_id': sample_request['request_id']})
                if 'Item' not in existing:
                    table.put_item(Item=sample_request)
                    logger.info(f"Created sample request: {sample_request['request_id']}")
                else:
                    logger.info("Sample request data already exists")
            except Exception as e:
                logger.warning(f"Could not create sample data: {str(e)}")
                
        except Exception as e:
            logger.warning(f"Could not create initial data (this is normal if running for the first time): {str(e)}") 