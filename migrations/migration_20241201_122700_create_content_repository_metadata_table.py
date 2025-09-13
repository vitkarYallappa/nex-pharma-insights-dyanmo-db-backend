"""
Create Content Repository Metadata Table Migration
Created: 2024-12-01T12:27:00
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from migrations.migration_manager import BaseMigration
from app.core.database import dynamodb_client
from app.config.settings import settings
from app.config.table_configs.content_repository_metadata_table import ContentRepositoryMetadataTableConfig
from app.core.logging import get_logger

logger = get_logger("migration.create_content_repository_metadata_table")

class CreateContentRepositoryMetadataTableMigration(BaseMigration):
    """
    Create Content Repository Metadata Table Migration
    Creates the content_repository_metadata table with proper indexes
    """
    
    @property
    def description(self) -> str:
        return "Create content_repository_metadata table with primary key only"
    
    async def up(self):
        """Execute the migration"""
        logger.info("Creating content_repository_metadata table migration")
        
        try:
            # Get content repository metadata table schema from configuration
            metadata_schema = ContentRepositoryMetadataTableConfig.SCHEMA
            table_name = ContentRepositoryMetadataTableConfig.get_table_name()
            
            # Create the content_repository_metadata table using schema configuration
            table_created = dynamodb_client.create_table(
                table_name=table_name,
                key_schema=metadata_schema["key_schema"],
                attribute_definitions=metadata_schema["attribute_definitions"],
                billing_mode=metadata_schema["billing_mode"]
            )
            
            if table_created:
                logger.info(f"Successfully created content_repository_metadata table: {table_name}")
            else:
                logger.info(f"Content_repository_metadata table {table_name} already exists")
                
            # Add some initial data if needed
            # await self._create_initial_data()
                
        except Exception as e:
            logger.error(f"Error creating content_repository_metadata table: {str(e)}")
            raise
    
    async def down(self):
        """Rollback the migration"""
        logger.info("Rolling back content_repository_metadata table creation")
        
        try:
            # Delete the content_repository_metadata table
            table_name = ContentRepositoryMetadataTableConfig.get_table_name()
            table_deleted = dynamodb_client.delete_table(table_name)
            
            if table_deleted:
                logger.info(f"Successfully deleted content_repository_metadata table: {table_name}")
            else:
                logger.warning(f"Content_repository_metadata table {table_name} did not exist")
                
        except Exception as e:
            logger.error(f"Error deleting content_repository_metadata table: {str(e)}")
            raise
    
    async def _create_initial_data(self):
        """Create initial test data for development"""
        if not settings.is_development:
            return
            
        logger.info("Creating initial test data for content repository metadata")
        
        try:
            from app.repositories.content_repository_metadata_repository import ContentRepositoryMetadataRepository
            from app.repositories.content_repository_repository import ContentRepositoryRepository
            from app.models.content_repository_metadata_model import ContentRepositoryMetadataModel
            
            metadata_repo = ContentRepositoryMetadataRepository()
            content_repo = ContentRepositoryRepository()
            
            # Get existing content entries to create metadata for
            contents = await content_repo.find_all_by_query()
            
            if contents:
                # Sample metadata data
                sample_metadata = [
                    {
                        "metadata_type": "extraction_info",
                        "metadata_key": "word_count",
                        "metadata_value": "1250",
                        "data_type": "number",
                        "is_searchable": True
                    },
                    {
                        "metadata_type": "extraction_info",
                        "metadata_key": "language",
                        "metadata_value": "en",
                        "data_type": "string",
                        "is_searchable": True
                    },
                    {
                        "metadata_type": "processing_info",
                        "metadata_key": "extraction_method",
                        "metadata_value": "web_scraping",
                        "data_type": "string",
                        "is_searchable": False
                    },
                    {
                        "metadata_type": "quality_metrics",
                        "metadata_key": "relevance_score",
                        "metadata_value": "0.85",
                        "data_type": "number",
                        "is_searchable": True
                    }
                ]
                
                for i, content in enumerate(contents[:3]):  # Limit to first 3 contents
                    # Create 2-3 metadata items per content
                    metadata_for_content = sample_metadata[i:i+2] if i < len(sample_metadata) else sample_metadata[:2]
                    
                    for metadata_data in metadata_for_content:
                        # Check if metadata already exists
                        metadata_exists = await metadata_repo.exists({
                            "content_id": content.pk,
                            "metadata_key": metadata_data["metadata_key"]
                        })
                        
                        if not metadata_exists:
                            metadata = ContentRepositoryMetadataModel.create_new(
                                content_id=content.pk,
                                request_id=content.request_id,
                                project_id=content.project_id,
                                metadata_type=metadata_data["metadata_type"],
                                metadata_key=metadata_data["metadata_key"],
                                metadata_value=metadata_data["metadata_value"],
                                data_type=metadata_data["data_type"],
                                is_searchable=metadata_data["is_searchable"]
                            )
                            
                            await metadata_repo.create(metadata)
                            logger.info(f"Created metadata: {metadata_data['metadata_key']} for content {content.title[:50]}...")
                
        except Exception as e:
            logger.warning(f"Could not create initial content repository metadata data: {str(e)}") 