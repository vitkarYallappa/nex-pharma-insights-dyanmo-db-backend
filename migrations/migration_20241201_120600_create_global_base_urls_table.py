"""
Create Global Base URLs Table Migration
Created: 2024-12-01T12:06:00
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from migrations.migration_manager import BaseMigration
from app.core.database import dynamodb_client
from app.config.settings import settings
from app.config.table_configs.global_base_urls_table import GlobalBaseUrlsTableConfig
from app.core.logging import get_logger

logger = get_logger("migration.create_global_base_urls_table")

class CreateGlobalBaseUrlsTableMigration(BaseMigration):
    """
    Create Global Base URLs Table Migration
    Creates the global_base_urls table with proper indexes
    """
    
    @property
    def description(self) -> str:
        return "Create global_base_urls table with primary key only"
    
    async def up(self):
        """Execute the migration"""
        logger.info("Creating global_base_urls table migration")
        
        try:
            # Get global base URLs table schema from configuration
            urls_schema = GlobalBaseUrlsTableConfig.SCHEMA
            table_name = GlobalBaseUrlsTableConfig.get_table_name(settings.TABLE_ENVIRONMENT)
            
            # Create the global_base_urls table using schema configuration
            table_created = dynamodb_client.create_table(
                table_name=table_name,
                key_schema=urls_schema["key_schema"],
                attribute_definitions=urls_schema["attribute_definitions"],
                billing_mode=urls_schema["billing_mode"]
            )
            
            if table_created:
                logger.info(f"Successfully created global_base_urls table: {table_name}")
            else:
                logger.info(f"Global_base_urls table {table_name} already exists")
                
            # Add some initial data if needed
            await self._create_initial_data()
                
        except Exception as e:
            logger.error(f"Error creating global_base_urls table: {str(e)}")
            raise
    
    async def down(self):
        """Rollback the migration"""
        logger.info("Rolling back global_base_urls table creation")
        
        try:
            # Delete the global_base_urls table
            table_name = GlobalBaseUrlsTableConfig.get_table_name(settings.TABLE_ENVIRONMENT)
            table_deleted = dynamodb_client.delete_table(table_name)
            
            if table_deleted:
                logger.info(f"Successfully deleted global_base_urls table: {table_name}")
            else:
                logger.warning(f"Global_base_urls table {table_name} did not exist")
                
        except Exception as e:
            logger.error(f"Error deleting global_base_urls table: {str(e)}")
            raise
    
    async def _create_initial_data(self):
        """Create initial test data for development"""
        if not settings.is_development:
            return
            
        logger.info("Creating initial test data for global base URLs")
        
        try:
            from app.repositories.global_base_urls_repository import GlobalBaseUrlsRepository
            from app.models.global_base_urls_model import GlobalBaseUrlsModel
            
            base_urls_repo = GlobalBaseUrlsRepository()
            
            # Sample pharmaceutical and medical data sources
            sample_base_urls = [
                {
                    "url": "https://firstwordpharma.com/",
                    "source_name": "FirstWord Pharma",
                    "source_type": "pharma_news",
                    "country_region": "Global",
                    "url_metadata": {
                        "description": "Pharmaceutical industry news and insights",
                        "access_type": "public",
                        "data_format": "html"
                    }
                },
                {
                    "url": "https://www.bloomberg.com/",
                    "source_name": "Bloomberg",
                    "source_type": "financial_news",
                    "country_region": "Global",
                    "url_metadata": {
                        "description": "Financial news and market data",
                        "access_type": "public",
                        "data_format": "html"
                    }
                },
                {
                    "url": "https://www.fiercepharma.com/",
                    "source_name": "FiercePharma",
                    "source_type": "pharma_news",
                    "country_region": "US",
                    "url_metadata": {
                        "description": "Pharmaceutical industry news and analysis",
                        "access_type": "public",
                        "data_format": "html"
                    }
                },
                {
                    "url": "https://www.investing.com/",
                    "source_name": "Investing.com",
                    "source_type": "financial_news",
                    "country_region": "Global",
                    "url_metadata": {
                        "description": "Financial markets and investment news",
                        "access_type": "public",
                        "data_format": "html"
                    }
                },
                {
                    "url": "https://www.usatoday.com/",
                    "source_name": "USA Today",
                    "source_type": "general_news",
                    "country_region": "US",
                    "url_metadata": {
                        "description": "General news and current events",
                        "access_type": "public",
                        "data_format": "html"
                    }
                },
                {
                    "url": "https://www.washingtonpost.com/",
                    "source_name": "The Washington Post",
                    "source_type": "general_news",
                    "country_region": "US",
                    "url_metadata": {
                        "description": "News and political coverage",
                        "access_type": "public",
                        "data_format": "html"
                    }
                },
                {
                    "url": "https://www.cafepharma.com/",
                    "source_name": "CafePharma",
                    "source_type": "pharma_forum",
                    "country_region": "Global",
                    "url_metadata": {
                        "description": "Pharmaceutical industry discussion forum",
                        "access_type": "public",
                        "data_format": "html"
                    }
                },
                {
                    "url": "https://www.thepharmaletter.com/",
                    "source_name": "The Pharma Letter",
                    "source_type": "pharma_news",
                    "country_region": "Global",
                    "url_metadata": {
                        "description": "Pharmaceutical industry news and updates",
                        "access_type": "public",
                        "data_format": "html"
                    }
                },
                {
                    "url": "https://pharmaphorum.com/",
                    "source_name": "Pharmaphorum",
                    "source_type": "pharma_news",
                    "country_region": "Global",
                    "url_metadata": {
                        "description": "Pharmaceutical industry insights and news",
                        "access_type": "public",
                        "data_format": "html"
                    }
                },
                {
                    "url": "https://www.google.com/",
                    "source_name": "Google",
                    "source_type": "search_engine",
                    "country_region": "Global",
                    "url_metadata": {
                        "description": "Search engine and web services",
                        "access_type": "public",
                        "data_format": "html"
                    }
                }
            ]
            
            for url_data in sample_base_urls:
                # Check if URL already exists
                url_exists = await base_urls_repo.exists({"url": url_data["url"]})
                
                if not url_exists:
                    base_url = GlobalBaseUrlsModel.create_new(
                        url=url_data["url"],
                        source_name=url_data["source_name"],
                        source_type=url_data["source_type"],
                        country_region=url_data["country_region"],
                        is_active=True,
                        url_metadata=url_data["url_metadata"]
                    )
                    
                    await base_urls_repo.create(base_url)
                    logger.info(f"Created global base URL: {url_data['source_name']} - {url_data['url']}")
                
        except Exception as e:
            logger.warning(f"Could not create initial global base URLs data: {str(e)}") 