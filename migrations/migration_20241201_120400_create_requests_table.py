"""
Create Requests Table Migration
Created: 2024-12-01T12:04:00
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from migrations.migration_manager import BaseMigration
from app.core.database import dynamodb_client
from app.config.settings import settings
from app.config.table_configs.requests_table import RequestsTableConfig
from app.core.logging import get_logger

logger = get_logger("migration.create_requests_table")

class CreateRequestsTableMigration(BaseMigration):
    """
    Create Requests Table Migration
    Creates the requests table with proper indexes
    """
    
    @property
    def description(self) -> str:
        return "Create requests table with primary key only"
    
    async def up(self):
        """Execute the migration"""
        logger.info("Creating requests table migration")
        
        try:
            # Get requests table schema from configuration
            requests_schema = RequestsTableConfig.SCHEMA
            table_name = RequestsTableConfig.get_table_name(settings.TABLE_ENVIRONMENT)
            
            # Create the requests table using schema configuration
            table_created = dynamodb_client.create_table(
                table_name=table_name,
                key_schema=requests_schema["key_schema"],
                attribute_definitions=requests_schema["attribute_definitions"],
                billing_mode=requests_schema["billing_mode"]
            )
            
            if table_created:
                logger.info(f"Successfully created requests table: {table_name}")
            else:
                logger.info(f"Requests table {table_name} already exists")
                
            # Add some initial data if needed
            await self._create_initial_data()
                
        except Exception as e:
            logger.error(f"Error creating requests table: {str(e)}")
            raise
    
    async def down(self):
        """Rollback the migration"""
        logger.info("Rolling back requests table creation")
        
        try:
            # Delete the requests table
            table_name = RequestsTableConfig.get_table_name(settings.TABLE_ENVIRONMENT)
            table_deleted = dynamodb_client.delete_table(table_name)
            
            if table_deleted:
                logger.info(f"Successfully deleted requests table: {table_name}")
            else:
                logger.warning(f"Requests table {table_name} did not exist")
                
        except Exception as e:
            logger.error(f"Error deleting requests table: {str(e)}")
            raise
    
    async def _create_initial_data(self):
        """Create initial test data for development"""
        if not settings.is_development:
            return
            
        logger.info("Creating initial test data for requests")
        
        try:
            from app.repositories.requests_repository import RequestsRepository
            from app.repositories.project_repository import ProjectRepository
            from app.models.requests_model import RequestsModel
            from datetime import datetime, timedelta
            
            requests_repo = RequestsRepository()
            project_repo = ProjectRepository()
            
            # Get existing projects to create requests for
            projects = await project_repo.scan({})
            
            if projects:
                sample_requests = [
                    {
                        "title": "Analyze Drug Interaction Data",
                        "description": "Comprehensive analysis of drug interaction patterns from clinical databases",
                        "priority": "high",
                        "status": "pending",
                        "time_range": {
                            "start_date": "2024-01-01",
                            "end_date": "2024-12-31"
                        },
                        "estimated_completion": (datetime.utcnow() + timedelta(days=30)).isoformat()
                    },
                    {
                        "title": "Generate Safety Insights Report",
                        "description": "Generate comprehensive safety insights from adverse event reports",
                        "priority": "medium",
                        "status": "in_progress",
                        "time_range": {
                            "start_date": "2024-06-01",
                            "end_date": "2024-12-31"
                        },
                        "estimated_completion": (datetime.utcnow() + timedelta(days=15)).isoformat()
                    },
                    {
                        "title": "Market Analysis for New Compound",
                        "description": "Market analysis and competitive landscape for new pharmaceutical compound",
                        "priority": "low",
                        "status": "completed",
                        "time_range": {
                            "start_date": "2024-03-01",
                            "end_date": "2024-09-30"
                        },
                        "estimated_completion": (datetime.utcnow() - timedelta(days=5)).isoformat()
                    }
                ]
                
                for i, request_data in enumerate(sample_requests):
                    # Use different projects for different requests
                    project = projects[i % len(projects)]
                    
                    # Check if request already exists
                    existing_requests = await requests_repo.scan({"title": request_data["title"]})
                    
                    if not existing_requests:
                        request = RequestsModel.create_new(
                            project_id=project.pk,
                            title=request_data["title"],
                            description=request_data["description"],
                            created_by=project.created_by,  # Use project creator as request creator
                            priority=request_data["priority"],
                            status=request_data["status"],
                            time_range=request_data["time_range"],
                            estimated_completion=request_data["estimated_completion"]
                        )
                        
                        await requests_repo.create(request)
                        logger.info(f"Created sample request: {request_data['title']}")
                
        except Exception as e:
            logger.warning(f"Could not create initial requests data: {str(e)}") 