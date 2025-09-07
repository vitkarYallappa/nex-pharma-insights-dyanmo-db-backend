"""
Create Content Repository Table Migration
Created: 2024-12-01T12:09:00
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from migrations.migration_manager import BaseMigration
from app.core.database import dynamodb_client
from app.config.settings import settings
from app.config.table_configs.content_repository_table import ContentRepositoryTableConfig
from app.core.logging import get_logger

logger = get_logger("migration.create_content_repository_table")

class CreateContentRepositoryTableMigration(BaseMigration):
    """
    Create Content Repository Table Migration
    Creates the content_repository table with proper indexes
    """
    
    @property
    def description(self) -> str:
        return "Create content_repository table with primary key only"
    
    async def up(self):
        """Execute the migration"""
        logger.info("Creating content_repository table migration")
        
        try:
            # Get content repository table schema from configuration
            content_schema = ContentRepositoryTableConfig.SCHEMA
            table_name = ContentRepositoryTableConfig.get_table_name(settings.TABLE_ENVIRONMENT)
            
            # Create the content_repository table using schema configuration
            table_created = dynamodb_client.create_table(
                table_name=table_name,
                key_schema=content_schema["key_schema"],
                attribute_definitions=content_schema["attribute_definitions"],
                billing_mode=content_schema["billing_mode"]
            )
            
            if table_created:
                logger.info(f"Successfully created content_repository table: {table_name}")
            else:
                logger.info(f"Content_repository table {table_name} already exists")
                
            # Add some initial data if needed
            await self._create_initial_data()
                
        except Exception as e:
            logger.error(f"Error creating content_repository table: {str(e)}")
            raise
    
    async def down(self):
        """Rollback the migration"""
        logger.info("Rolling back content_repository table creation")
        
        try:
            # Delete the content_repository table
            table_name = ContentRepositoryTableConfig.get_table_name(settings.TABLE_ENVIRONMENT)
            table_deleted = dynamodb_client.delete_table(table_name)
            
            if table_deleted:
                logger.info(f"Successfully deleted content_repository table: {table_name}")
            else:
                logger.warning(f"Content_repository table {table_name} did not exist")
                
        except Exception as e:
            logger.error(f"Error deleting content_repository table: {str(e)}")
            raise
    
    async def _create_initial_data(self):
        """Create initial test data for development"""
        if not settings.is_development:
            return
            
        logger.info("Creating initial test data for content repository")
        
        try:
            from app.repositories.content_repository_repository import ContentRepositoryRepository
            from app.repositories.requests_repository import RequestsRepository
            from app.models.content_repository_model import ContentRepositoryModel
            import hashlib
            import random
            
            content_repo = ContentRepositoryRepository()
            requests_repo = RequestsRepository()
            
            # Get existing requests to create content for
            requests = await requests_repo.scan({})
            
            if requests:
                # Sample content data
                sample_contents = [
                    {
                        "canonical_url": "https://pubmed.ncbi.nlm.nih.gov/12345678/",
                        "title": "Efficacy and Safety of Novel Oncology Drug in Phase III Clinical Trial",
                        "source_type": "medical_literature",
                        "relevance_type": "high_relevance"
                    },
                    {
                        "canonical_url": "https://clinicaltrials.gov/ct2/show/NCT12345678",
                        "title": "Randomized Controlled Trial of Cardiovascular Drug Safety",
                        "source_type": "clinical_trial",
                        "relevance_type": "medium_relevance"
                    },
                    {
                        "canonical_url": "https://www.fda.gov/drugs/drug-safety-and-availability/fda-drug-safety-communication",
                        "title": "FDA Drug Safety Communication: New Safety Information",
                        "source_type": "regulatory_document",
                        "relevance_type": "high_relevance"
                    },
                    {
                        "canonical_url": "https://www.ema.europa.eu/en/medicines/human/EPAR/example-drug",
                        "title": "European Public Assessment Report for Example Drug",
                        "source_type": "regulatory_document",
                        "relevance_type": "medium_relevance"
                    }
                ]
                
                for i, request in enumerate(requests[:3]):  # Limit to first 3 requests
                    # Create 2-3 content items per request
                    contents_for_request = sample_contents[i:i+2] if i < len(sample_contents) else sample_contents[:2]
                    
                    for content_data in contents_for_request:
                        # Generate content hash
                        content_hash = hashlib.md5(
                            f"{content_data['canonical_url']}{content_data['title']}".encode()
                        ).hexdigest()
                        
                        # Check if content already exists
                        existing_content = await content_repo.scan({
                            "canonical_url": content_data["canonical_url"],
                            "request_id": request.pk
                        })
                        
                        if not existing_content:
                            content = ContentRepositoryModel.create_new(
                                request_id=request.pk,
                                project_id=request.project_id,
                                canonical_url=content_data["canonical_url"],
                                title=content_data["title"],
                                content_hash=content_hash,
                                source_type=content_data["source_type"],
                                relevance_type=content_data["relevance_type"],
                                version=1,
                                is_canonical=True
                            )
                            
                            await content_repo.create(content)
                            logger.info(f"Created content: {content_data['title'][:50]}... for request {request.title}")
                
        except Exception as e:
            logger.warning(f"Could not create initial content repository data: {str(e)}") 