"""
Create Project Request Statistics Table Migration
Created: 2024-12-01T12:02:00
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from migrations.migration_manager import BaseMigration
from app.core.database import dynamodb_client
from app.config.settings import settings
from app.config.table_configs.project_request_statistics_table import ProjectRequestStatisticsTableConfig
from app.core.logging import get_logger

logger = get_logger("migration.create_project_request_statistics_table")

class CreateProjectRequestStatisticsTableMigration(BaseMigration):
    """
    Create Project Request Statistics Table Migration
    Creates the project_request_statistics table with proper indexes
    """
    
    @property
    def description(self) -> str:
        return "Create project_request_statistics table with primary key only"
    
    async def up(self):
        """Execute the migration"""
        logger.info("Creating project_request_statistics table migration")
        
        try:
            # Get project request statistics table schema from configuration
            statistics_schema = ProjectRequestStatisticsTableConfig.SCHEMA
            table_name = ProjectRequestStatisticsTableConfig.get_table_name(settings.TABLE_ENVIRONMENT)
            
            # Create the project_request_statistics table using schema configuration
            table_created = dynamodb_client.create_table(
                table_name=table_name,
                key_schema=statistics_schema["key_schema"],
                attribute_definitions=statistics_schema["attribute_definitions"],
                billing_mode=statistics_schema["billing_mode"]
            )
            
            if table_created:
                logger.info(f"Successfully created project_request_statistics table: {table_name}")
            else:
                logger.info(f"Project_request_statistics table {table_name} already exists")
                
            # Add some initial data if needed
            await self._create_initial_data()
                
        except Exception as e:
            logger.error(f"Error creating project_request_statistics table: {str(e)}")
            raise
    
    async def down(self):
        """Rollback the migration"""
        logger.info("Rolling back project_request_statistics table creation")
        
        try:
            # Delete the project_request_statistics table
            table_name = ProjectRequestStatisticsTableConfig.get_table_name(settings.TABLE_ENVIRONMENT)
            table_deleted = dynamodb_client.delete_table(table_name)
            
            if table_deleted:
                logger.info(f"Successfully deleted project_request_statistics table: {table_name}")
            else:
                logger.warning(f"Project_request_statistics table {table_name} did not exist")
                
        except Exception as e:
            logger.error(f"Error deleting project_request_statistics table: {str(e)}")
            raise
    
    async def _create_initial_data(self):
        """Create initial test data for development"""
        if not settings.is_development:
            return
            
        logger.info("Creating initial test data for project request statistics")
        
        try:
            from app.repositories.project_request_statistics_repository import ProjectRequestStatisticsRepository
            from app.repositories.project_repository import ProjectRepository
            from app.models.project_request_statistics_model import ProjectRequestStatisticsModel
            from datetime import datetime, timedelta
            import random
            
            stats_repo = ProjectRequestStatisticsRepository()
            project_repo = ProjectRepository()
            
            # Get existing projects to create statistics for
            projects = await project_repo.find_all_by_query()
            
            if projects:
                for project in projects:
                    # Check if statistics already exist for this project
                    stats_exist = await stats_repo.exists({"project_id": project.pk})
                    
                    if not stats_exist:
                        # Generate realistic statistics
                        total_requests = random.randint(5, 50)
                        completed_requests = random.randint(1, total_requests)
                        pending_requests = random.randint(0, total_requests - completed_requests)
                        failed_requests = total_requests - completed_requests - pending_requests
                        
                        statistics = ProjectRequestStatisticsModel.create_new(
                            project_id=project.pk,
                            total_requests=total_requests,
                            completed_requests=completed_requests,
                            pending_requests=pending_requests,
                            failed_requests=failed_requests,
                            average_processing_time=random.uniform(300, 3600),  # 5 minutes to 1 hour
                            last_activity_at=(datetime.utcnow() - timedelta(hours=random.randint(1, 72))).isoformat(),
                            statistics_metadata={
                                "success_rate": round(completed_requests / total_requests * 100, 2),
                                "peak_processing_hour": random.randint(9, 17),
                                "most_common_request_type": random.choice(["analysis", "insight", "report"])
                            }
                        )
                        
                        await stats_repo.create(statistics)
                        logger.info(f"Created statistics for project: {project.name}")
                
        except Exception as e:
            logger.warning(f"Could not create initial project request statistics data: {str(e)}") 