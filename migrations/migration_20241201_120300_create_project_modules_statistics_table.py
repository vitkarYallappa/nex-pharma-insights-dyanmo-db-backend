"""
Create Project Modules Statistics Table Migration
Created: 2024-12-01T12:03:00
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from migrations.migration_manager import BaseMigration
from app.core.database import dynamodb_client
from app.config.settings import settings
from app.config.table_configs.project_modules_statistics_table import ProjectModulesStatisticsTableConfig
from app.core.logging import get_logger

logger = get_logger("migration.create_project_modules_statistics_table")

class CreateProjectModulesStatisticsTableMigration(BaseMigration):
    """
    Create Project Modules Statistics Table Migration
    Creates the project_modules_statistics table with proper indexes
    """
    
    @property
    def description(self) -> str:
        return "Create project_modules_statistics table with primary key only"
    
    async def up(self):
        """Execute the migration"""
        logger.info("Creating project_modules_statistics table migration")
        
        try:
            # Get project modules statistics table schema from configuration
            modules_schema = ProjectModulesStatisticsTableConfig.SCHEMA
            table_name = ProjectModulesStatisticsTableConfig.get_table_name(settings.TABLE_ENVIRONMENT)
            
            # Create the project_modules_statistics table using schema configuration
            table_created = dynamodb_client.create_table(
                table_name=table_name,
                key_schema=modules_schema["key_schema"],
                attribute_definitions=modules_schema["attribute_definitions"],
                billing_mode=modules_schema["billing_mode"]
            )
            
            if table_created:
                logger.info(f"Successfully created project_modules_statistics table: {table_name}")
            else:
                logger.info(f"Project_modules_statistics table {table_name} already exists")
                
            # Add some initial data if needed
            await self._create_initial_data()
                
        except Exception as e:
            logger.error(f"Error creating project_modules_statistics table: {str(e)}")
            raise
    
    async def down(self):
        """Rollback the migration"""
        logger.info("Rolling back project_modules_statistics table creation")
        
        try:
            # Delete the project_modules_statistics table
            table_name = ProjectModulesStatisticsTableConfig.get_table_name(settings.TABLE_ENVIRONMENT)
            table_deleted = dynamodb_client.delete_table(table_name)
            
            if table_deleted:
                logger.info(f"Successfully deleted project_modules_statistics table: {table_name}")
            else:
                logger.warning(f"Project_modules_statistics table {table_name} did not exist")
                
        except Exception as e:
            logger.error(f"Error deleting project_modules_statistics table: {str(e)}")
            raise
    
    async def _create_initial_data(self):
        """Create initial test data for development"""
        if not settings.is_development:
            return
            
        logger.info("Creating initial test data for project modules statistics")
        
        try:
            from app.repositories.project_modules_statistics_repository import ProjectModulesStatisticsRepository
            from app.repositories.project_repository import ProjectRepository
            from app.models.project_modules_statistics_model import ProjectModulesStatisticsModel
            import random
            
            stats_repo = ProjectModulesStatisticsRepository()
            project_repo = ProjectRepository()
            
            # Get existing projects to create statistics for
            projects = await project_repo.scan({})
            
            if projects:
                for project in projects:
                    # Check if statistics already exist for this project
                    existing_stats = await stats_repo.scan({"project_id": project.pk})
                    
                    if not existing_stats:
                        statistics = ProjectModulesStatisticsModel.create_new(
                            project_id=project.pk,
                            content_analysis_count=random.randint(10, 100),
                            insight_generation_count=random.randint(5, 50),
                            implication_analysis_count=random.randint(3, 30),
                            total_processing_time=random.uniform(1800, 18000),  # 30 minutes to 5 hours
                            statistics_metadata={
                                "most_active_module": random.choice(["content_analysis", "insight_generation", "implication_analysis"]),
                                "average_content_per_request": random.randint(5, 25),
                                "success_rate": random.uniform(85.0, 99.0)
                            }
                        )
                        
                        await stats_repo.create(statistics)
                        logger.info(f"Created module statistics for project: {project.name}")
                
        except Exception as e:
            logger.warning(f"Could not create initial project modules statistics data: {str(e)}") 