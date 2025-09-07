"""
Create Keywords Table Migration
Created: 2024-12-01T12:07:00
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from migrations.migration_manager import BaseMigration
from app.core.database import dynamodb_client
from app.config.settings import settings
from app.config.table_configs.keywords_table import KeywordsTableConfig
from app.core.logging import get_logger

logger = get_logger("migration.create_keywords_table")

class CreateKeywordsTableMigration(BaseMigration):
    """
    Create Keywords Table Migration
    Creates the keywords table with proper indexes
    """
    
    @property
    def description(self) -> str:
        return "Create keywords table with primary key only"
    
    async def up(self):
        """Execute the migration"""
        logger.info("Creating keywords table migration")
        
        try:
            # Get keywords table schema from configuration
            keywords_schema = KeywordsTableConfig.SCHEMA
            table_name = KeywordsTableConfig.get_table_name(settings.TABLE_ENVIRONMENT)
            
            # Create the keywords table using schema configuration
            table_created = dynamodb_client.create_table(
                table_name=table_name,
                key_schema=keywords_schema["key_schema"],
                attribute_definitions=keywords_schema["attribute_definitions"],
                billing_mode=keywords_schema["billing_mode"]
            )
            
            if table_created:
                logger.info(f"Successfully created keywords table: {table_name}")
            else:
                logger.info(f"Keywords table {table_name} already exists")
                
            # Add some initial data if needed
            await self._create_initial_data()
                
        except Exception as e:
            logger.error(f"Error creating keywords table: {str(e)}")
            raise
    
    async def down(self):
        """Rollback the migration"""
        logger.info("Rolling back keywords table creation")
        
        try:
            # Delete the keywords table
            table_name = KeywordsTableConfig.get_table_name(settings.TABLE_ENVIRONMENT)
            table_deleted = dynamodb_client.delete_table(table_name)
            
            if table_deleted:
                logger.info(f"Successfully deleted keywords table: {table_name}")
            else:
                logger.warning(f"Keywords table {table_name} did not exist")
                
        except Exception as e:
            logger.error(f"Error deleting keywords table: {str(e)}")
            raise
    
    async def _create_initial_data(self):
        """Create initial test data for development"""
        if not settings.is_development:
            return
            
        logger.info("Creating initial test data for keywords")
        
        try:
            from app.repositories.keywords_repository import KeywordsRepository
            from app.repositories.requests_repository import RequestsRepository
            from app.models.keywords_model import KeywordsModel
            
            keywords_repo = KeywordsRepository()
            requests_repo = RequestsRepository()
            
            # Get existing requests to create keywords for
            requests = await requests_repo.find_all_by_query()
            
            if requests:
                # Sample keywords for different request types
                sample_keywords_by_type = {
                    "drug_interaction": ["drug-drug interaction", "pharmacokinetics", "CYP450", "metabolism", "contraindication"],
                    "safety": ["adverse event", "side effect", "toxicity", "safety profile", "pharmacovigilance"],
                    "efficacy": ["clinical efficacy", "therapeutic effect", "biomarker", "endpoint", "response rate"],
                    "market": ["market share", "competitive analysis", "pricing", "commercial strategy", "launch"]
                }
                
                for i, request in enumerate(requests[:3]):  # Limit to first 3 requests
                    # Determine keyword type based on request title
                    if "interaction" in request.title.lower():
                        keyword_type = "drug_interaction"
                    elif "safety" in request.title.lower() or "insight" in request.title.lower():
                        keyword_type = "safety"
                    elif "market" in request.title.lower() or "analysis" in request.title.lower():
                        keyword_type = "market"
                    else:
                        keyword_type = "efficacy"
                    
                    keywords_list = sample_keywords_by_type.get(keyword_type, sample_keywords_by_type["efficacy"])
                    
                    for keyword_text in keywords_list:
                        # Check if keyword already exists for this request
                        keyword_exists = await keywords_repo.exists({
                            "keyword": keyword_text,
                            "request_id": request.pk
                        })
                        
                        if not keyword_exists:
                            keyword = KeywordsModel.create_new(
                                keyword=keyword_text,
                                request_id=request.pk,
                                keyword_type=keyword_type
                            )
                            
                            await keywords_repo.create(keyword)
                            logger.info(f"Created keyword: {keyword_text} for request {request.title}")
                
        except Exception as e:
            logger.warning(f"Could not create initial keywords data: {str(e)}") 