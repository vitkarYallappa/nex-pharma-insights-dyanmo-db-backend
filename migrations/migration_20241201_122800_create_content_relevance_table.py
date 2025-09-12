"""
Create Content Relevance Table Migration
Created: 2024-12-01T12:28:00
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from migrations.migration_manager import BaseMigration
from app.core.database import dynamodb_client
from app.config.settings import settings
from app.config.table_configs.content_relevance_table import ContentRelevanceTableConfig
from app.core.logging import get_logger

logger = get_logger("migration.create_content_relevance_table")

class CreateContentRelevanceTableMigration(BaseMigration):
    """
    Create Content Relevance Table Migration
    Creates the content_relevance table with proper indexes
    """
    
    @property
    def description(self) -> str:
        return "Create content_relevance table with primary key only"
    
    async def up(self):
        """Execute the migration"""
        logger.info("Creating content_relevance table migration")
        
        try:
            # Get content relevance table schema from configuration
            relevance_schema = ContentRelevanceTableConfig.SCHEMA
            table_name = ContentRelevanceTableConfig.get_table_name(settings.TABLE_ENVIRONMENT)
            
            # Create the content_relevance table using schema configuration
            table_created = dynamodb_client.create_table(
                table_name=table_name,
                key_schema=relevance_schema["key_schema"],
                attribute_definitions=relevance_schema["attribute_definitions"],
                billing_mode=relevance_schema["billing_mode"]
            )
            
            if table_created:
                logger.info(f"Successfully created content_relevance table: {table_name}")
            else:
                logger.info(f"Content_relevance table {table_name} already exists")
                
            # Add some initial data if needed
            # await self._create_initial_data()
                
        except Exception as e:
            logger.error(f"Error creating content_relevance table: {str(e)}")
            raise
    
    async def down(self):
        """Rollback the migration"""
        logger.info("Rolling back content_relevance table creation")
        
        try:
            # Delete the content_relevance table
            table_name = ContentRelevanceTableConfig.get_table_name(settings.TABLE_ENVIRONMENT)
            table_deleted = dynamodb_client.delete_table(table_name)
            
            if table_deleted:
                logger.info(f"Successfully deleted content_relevance table: {table_name}")
            else:
                logger.warning(f"Content_relevance table {table_name} did not exist")
                
        except Exception as e:
            logger.error(f"Error deleting content_relevance table: {str(e)}")
            raise
    
    async def _create_initial_data(self):
        """Create initial test data for development"""
        if not settings.is_development:
            return
            
        logger.info("Creating initial test data for content relevance")
        
        try:
            from app.repositories.content_relevance_repository import ContentRelevanceRepository
            from app.repositories.content_repository_repository import ContentRepositoryRepository
            from app.models.content_relevance_model import ContentRelevanceModel
            
            relevance_repo = ContentRelevanceRepository()
            content_repo = ContentRepositoryRepository()
            
            # Get existing content entries to create relevance data for
            contents = await content_repo.find_all_by_query()
            
            if contents:
                # Sample relevance data
                sample_relevance = [
                    {
                        "relevance_text": "This content is highly relevant to pharmaceutical research and drug development processes.",
                        "relevance_score": 0.85,
                        "is_relevant": True,
                        "relevance_category": "high_relevance",
                        "confidence_score": 0.92
                    },
                    {
                        "relevance_text": "Content shows moderate relevance to clinical trial methodologies and regulatory compliance.",
                        "relevance_score": 0.65,
                        "is_relevant": True,
                        "relevance_category": "medium_relevance",
                        "confidence_score": 0.78
                    },
                    {
                        "relevance_text": "Limited relevance to the specified pharmaceutical domain and research objectives.",
                        "relevance_score": 0.35,
                        "is_relevant": False,
                        "relevance_category": "low_relevance",
                        "confidence_score": 0.82
                    }
                ]
                
                for i, content in enumerate(contents[:3]):  # Limit to first 3 contents
                    relevance_data = sample_relevance[i] if i < len(sample_relevance) else sample_relevance[0]
                    
                    # Check if relevance already exists for this content
                    relevance_exists = await relevance_repo.exists({
                        "content_id": content.pk
                    })
                    
                    if not relevance_exists:
                        relevance = ContentRelevanceModel.create_new(
                            url_id=content.pk,
                            content_id=content.pk,
                            relevance_text=relevance_data["relevance_text"],
                            relevance_score=relevance_data["relevance_score"],
                            is_relevant=relevance_data["is_relevant"],
                            relevance_category=relevance_data["relevance_category"],
                            confidence_score=relevance_data["confidence_score"],
                            relevance_content_file_path=f"/storage/relevance/{content.pk}.json",
                            created_by="migration_seeder"
                        )
                        
                        await relevance_repo.create(relevance)
                        logger.info(f"Created relevance data for content: {content.title[:50]}...")
                
        except Exception as e:
            logger.warning(f"Could not create initial content relevance data: {str(e)}") 