"""
Create Content Summary Table Migration
Created: 2024-12-01T12:12:00
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from migrations.migration_manager import BaseMigration
from app.core.database import dynamodb_client
from app.config.settings import settings
from app.config.table_configs.content_summary_table import ContentSummaryTableConfig
from app.core.logging import get_logger

logger = get_logger("migration.create_content_summary_table")

class CreateContentSummaryTableMigration(BaseMigration):
    """
    Create Content Summary Table Migration
    Creates the content_summary table with proper indexes
    """
    
    @property
    def description(self) -> str:
        return "Create content_summary table with primary key only"
    
    async def up(self):
        """Execute the migration"""
        logger.info("Creating content_summary table migration")
        
        try:
            # Get content summary table schema from configuration
            summary_schema = ContentSummaryTableConfig.SCHEMA
            table_name = ContentSummaryTableConfig.get_table_name(settings.TABLE_ENVIRONMENT)
            
            # Create the content_summary table using schema configuration
            table_created = dynamodb_client.create_table(
                table_name=table_name,
                key_schema=summary_schema["key_schema"],
                attribute_definitions=summary_schema["attribute_definitions"],
                billing_mode=summary_schema["billing_mode"]
            )
            
            if table_created:
                logger.info(f"Successfully created content_summary table: {table_name}")
            else:
                logger.info(f"Content_summary table {table_name} already exists")
                
            # Add some initial data if needed
            # await self._create_initial_data()
                
        except Exception as e:
            logger.error(f"Error creating content_summary table: {str(e)}")
            raise
    
    async def down(self):
        """Rollback the migration"""
        logger.info("Rolling back content_summary table creation")
        
        try:
            # Delete the content_summary table
            table_name = ContentSummaryTableConfig.get_table_name(settings.TABLE_ENVIRONMENT)
            table_deleted = dynamodb_client.delete_table(table_name)
            
            if table_deleted:
                logger.info(f"Successfully deleted content_summary table: {table_name}")
            else:
                logger.warning(f"Content_summary table {table_name} did not exist")
                
        except Exception as e:
            logger.error(f"Error deleting content_summary table: {str(e)}")
            raise
    
    async def _create_initial_data(self):
        """Create initial test data for development"""
        if not settings.is_development:
            return
            
        logger.info("Creating initial test data for content summary")
        
        try:
            from app.repositories.content_summary_repository import ContentSummaryRepository
            from app.repositories.content_repository_repository import ContentRepositoryRepository
            from app.models.content_summary_model import ContentSummaryModel
            import random
            
            summary_repo = ContentSummaryRepository()
            content_repo = ContentRepositoryRepository()
            
            # Get existing content to create summaries for
            contents = await content_repo.find_all_by_query()
            
            if contents:
                sample_summaries = [
                    "This study demonstrates significant efficacy in treating oncology patients with novel therapeutic approach.",
                    "Clinical trial results show improved safety profile compared to existing treatments in cardiovascular disease.",
                    "Regulatory analysis indicates potential for accelerated approval pathway based on breakthrough therapy designation.",
                    "Market research suggests strong commercial potential with competitive advantages in target therapeutic area."
                ]
                
                for i, content in enumerate(contents[:4]):  # Limit to first 4 content items
                    # Check if summary already exists for this content
                    summary_exists = await summary_repo.exists({"content_id": content.pk})
                    
                    if not summary_exists:
                        summary = ContentSummaryModel.create_new(
                            content_id=content.pk,
                            request_id=content.request_id,
                            project_id=content.project_id,
                            summary_text=sample_summaries[i % len(sample_summaries)],
                            summary_type=random.choice(["executive", "technical", "regulatory"]),
                            confidence_score=random.uniform(0.7, 0.95),
                            word_count=random.randint(50, 300),
                            summary_metadata={
                                "extraction_method": random.choice(["ai_generated", "manual_review", "hybrid"]),
                                "key_topics": random.sample(["efficacy", "safety", "regulatory", "market", "clinical"], 3),
                                "relevance_score": random.uniform(0.6, 0.9)
                            }
                        )
                        
                        await summary_repo.create(summary)
                        logger.info(f"Created summary for content: {content.title[:50]}...")
                
        except Exception as e:
            logger.warning(f"Could not create initial content summary data: {str(e)}") 