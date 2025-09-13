"""
Create Source URLs Table Migration
Created: 2024-12-01T12:08:00
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from migrations.migration_manager import BaseMigration
from app.core.database import dynamodb_client
from app.config.settings import settings
from app.config.table_configs.source_urls_table import SourceUrlsTableConfig
from app.core.logging import get_logger

logger = get_logger("migration.create_source_urls_table")

class CreateSourceUrlsTableMigration(BaseMigration):
    """
    Create Source URLs Table Migration
    Creates the source_urls table with proper indexes
    """
    
    @property
    def description(self) -> str:
        return "Create source_urls table with primary key only"
    
    async def up(self):
        """Execute the migration"""
        logger.info("Creating source_urls table migration")
        
        try:
            # Get source URLs table schema from configuration
            urls_schema = SourceUrlsTableConfig.SCHEMA
            table_name = SourceUrlsTableConfig.get_table_name()
            
            # Create the source_urls table using schema configuration
            table_created = dynamodb_client.create_table(
                table_name=table_name,
                key_schema=urls_schema["key_schema"],
                attribute_definitions=urls_schema["attribute_definitions"],
                billing_mode=urls_schema["billing_mode"]
            )
            
            if table_created:
                logger.info(f"Successfully created source_urls table: {table_name}")
            else:
                logger.info(f"Source_urls table {table_name} already exists")
                
            # Add some initial data if needed
            # await self._create_initial_data()
                
        except Exception as e:
            logger.error(f"Error creating source_urls table: {str(e)}")
            raise
    
    async def down(self):
        """Rollback the migration"""
        logger.info("Rolling back source_urls table creation")
        
        try:
            # Delete the source_urls table
            table_name = SourceUrlsTableConfig.get_table_name()
            table_deleted = dynamodb_client.delete_table(table_name)
            
            if table_deleted:
                logger.info(f"Successfully deleted source_urls table: {table_name}")
            else:
                logger.warning(f"Source_urls table {table_name} did not exist")
                
        except Exception as e:
            logger.error(f"Error deleting source_urls table: {str(e)}")
            raise
    
    async def _create_initial_data(self):
        """Create initial test data for development"""
        if not settings.is_development:
            return
            
        logger.info("Creating initial test data for source URLs")
        
        try:
            from app.repositories.source_urls_repository import SourceUrlsRepository
            from app.repositories.requests_repository import RequestsRepository
            from app.models.source_urls_model import SourceUrlsModel
            
            source_urls_repo = SourceUrlsRepository()
            requests_repo = RequestsRepository()
            
            # Get existing requests to create source URLs for
            requests = await requests_repo.find_all_by_query()
            
            if requests:
                # Sample source URLs for different types of research
                sample_source_urls = [
                    {
                        "url": "https://pubmed.ncbi.nlm.nih.gov/search/",
                        "source_name": "PubMed Search",
                        "source_type": "medical_literature",
                        "country_region": "US",
                        "url_metadata": {
                            "search_type": "literature_review",
                            "data_format": "xml",
                            "access_method": "api"
                        }
                    },
                    {
                        "url": "https://clinicaltrials.gov/api/query/",
                        "source_name": "ClinicalTrials API",
                        "source_type": "clinical_trials",
                        "country_region": "US",
                        "url_metadata": {
                            "search_type": "clinical_data",
                            "data_format": "json",
                            "access_method": "api"
                        }
                    },
                    {
                        "url": "https://www.fda.gov/drugs/drug-approvals-and-databases/",
                        "source_name": "FDA Drug Database",
                        "source_type": "regulatory",
                        "country_region": "US",
                        "url_metadata": {
                            "search_type": "regulatory_data",
                            "data_format": "html",
                            "access_method": "web_scraping"
                        }
                    },
                    {
                        "url": "https://www.ema.europa.eu/en/medicines/",
                        "source_name": "EMA Medicine Database",
                        "source_type": "regulatory",
                        "country_region": "EU",
                        "url_metadata": {
                            "search_type": "regulatory_data",
                            "data_format": "html",
                            "access_method": "web_scraping"
                        }
                    }
                ]
                
                for i, request in enumerate(requests[:3]):  # Limit to first 3 requests
                    # Assign 2-3 source URLs per request
                    urls_for_request = sample_source_urls[i:i+2] if i < len(sample_source_urls) else sample_source_urls[:2]
                    
                    for url_data in urls_for_request:
                        # Check if source URL already exists for this request
                        url_exists = await source_urls_repo.exists({
                            "url": url_data["url"],
                            "request_id": request.pk
                        })
                        
                        if not url_exists:
                            source_url = SourceUrlsModel.create_new(
                                request_id=request.pk,
                                url=url_data["url"],
                                source_name=url_data["source_name"],
                                source_type=url_data["source_type"],
                                country_region=url_data["country_region"],
                                is_active=True,
                                url_metadata=url_data["url_metadata"]
                            )
                            
                            await source_urls_repo.create(source_url)
                            logger.info(f"Created source URL: {url_data['source_name']} for request {request.title}")
                
        except Exception as e:
            logger.warning(f"Could not create initial source URLs data: {str(e)}") 