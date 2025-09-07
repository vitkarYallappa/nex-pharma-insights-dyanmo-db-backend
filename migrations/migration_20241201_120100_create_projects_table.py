"""
Create Projects Details Table Migration
Created: 2024-12-01T12:01:00
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from migrations.migration_manager import BaseMigration
from app.core.database import dynamodb_client
from app.config.settings import settings
from app.config.table_configs.projects_table import ProjectsTableConfig
from app.core.logging import get_logger

logger = get_logger("migration.create_projects_table")

class CreateProjectsTableMigration(BaseMigration):
    """
    Create Projects Details Table Migration
    Creates the projects_details table with proper indexes
    """
    
    @property
    def description(self) -> str:
        return "Create projects_details table with primary key only"
    
    async def up(self):
        """Execute the migration"""
        logger.info("Creating projects_details table migration")
        
        try:
            # Get projects table schema from configuration
            projects_schema = ProjectsTableConfig.SCHEMA
            table_name = ProjectsTableConfig.get_table_name(settings.TABLE_ENVIRONMENT)
            
            # Create the projects_details table using schema configuration
            table_created = dynamodb_client.create_table(
                table_name=table_name,
                key_schema=projects_schema["key_schema"],
                attribute_definitions=projects_schema["attribute_definitions"],
                billing_mode=projects_schema["billing_mode"]
            )
            
            if table_created:
                logger.info(f"Successfully created projects_details table: {table_name}")
            else:
                logger.info(f"Projects_details table {table_name} already exists")
                
            # Add some initial data if needed
            await self._create_initial_data()
                
        except Exception as e:
            logger.error(f"Error creating projects_details table: {str(e)}")
            raise
    
    async def down(self):
        """Rollback the migration"""
        logger.info("Rolling back projects_details table creation")
        
        try:
            # Delete the projects_details table
            table_name = ProjectsTableConfig.get_table_name(settings.TABLE_ENVIRONMENT)
            table_deleted = dynamodb_client.delete_table(table_name)
            
            if table_deleted:
                logger.info(f"Successfully deleted projects_details table: {table_name}")
            else:
                logger.warning(f"Projects_details table {table_name} did not exist")
                
        except Exception as e:
            logger.error(f"Error deleting projects_details table: {str(e)}")
            raise
    
    async def _create_initial_data(self):
        """Create initial test data for development"""
        if not settings.is_development:
            return
            
        logger.info("Creating initial test data for projects")
        
        try:
            from app.repositories.project_repository import ProjectRepository
            from app.models.project_model import ProjectModel
            
            project_repo = ProjectRepository()
            
            # Sample projects data
            sample_projects = [
                {
                    "name": "Pharma Research Project Alpha",
                    "description": "Research project focused on drug discovery and analysis",
                    "created_by": "admin@example.com",  # Will be replaced with actual user ID
                    "status": "active",
                    "project_metadata": {
                        "research_area": "oncology",
                        "priority": "high",
                        "budget": 500000
                    },
                    "module_config": {
                        "content_analysis": True,
                        "insight_generation": True,
                        "implication_analysis": True
                    }
                },
                {
                    "name": "Clinical Trial Data Analysis",
                    "description": "Analysis of clinical trial data for new pharmaceutical compounds",
                    "created_by": "test@example.com",  # Will be replaced with actual user ID
                    "status": "active",
                    "project_metadata": {
                        "research_area": "cardiology",
                        "priority": "medium",
                        "budget": 300000
                    },
                    "module_config": {
                        "content_analysis": True,
                        "insight_generation": False,
                        "implication_analysis": True
                    }
                },
                {
                    "name": "Drug Safety Monitoring",
                    "description": "Monitoring and analysis of drug safety data from multiple sources",
                    "created_by": "admin@example.com",
                    "status": "planning",
                    "project_metadata": {
                        "research_area": "pharmacovigilance",
                        "priority": "high",
                        "budget": 750000
                    },
                    "module_config": {
                        "content_analysis": True,
                        "insight_generation": True,
                        "implication_analysis": True
                    }
                }
            ]
            
            for project_data in sample_projects:
                # Check if project already exists (by name)
                existing_projects = await project_repo.scan({"name": project_data["name"]})
                
                if not existing_projects:
                    project = ProjectModel.create_new(
                        name=project_data["name"],
                        description=project_data["description"],
                        created_by=project_data["created_by"],
                        status=project_data["status"],
                        project_metadata=project_data["project_metadata"],
                        module_config=project_data["module_config"]
                    )
                    
                    await project_repo.create(project)
                    logger.info(f"Created sample project: {project_data['name']}")
                
        except Exception as e:
            logger.warning(f"Could not create initial project data: {str(e)}") 