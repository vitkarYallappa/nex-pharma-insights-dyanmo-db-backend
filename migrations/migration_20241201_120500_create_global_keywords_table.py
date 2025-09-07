"""
Create Global Keywords Table Migration
Created: 2024-12-01T12:05:00
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from migrations.migration_manager import BaseMigration
from app.core.database import dynamodb_client
from app.config.settings import settings
from app.config.table_configs.global_keywords_table import GlobalKeywordsTableConfig
from app.core.logging import get_logger

logger = get_logger("migration.create_global_keywords_table")

class CreateGlobalKeywordsTableMigration(BaseMigration):
    """
    Create Global Keywords Table Migration
    Creates the global_keywords table with proper indexes
    """
    
    @property
    def description(self) -> str:
        return "Create global_keywords table with primary key only"
    
    async def up(self):
        """Execute the migration"""
        logger.info("Creating global_keywords table migration")
        
        try:
            # Get global keywords table schema from configuration
            keywords_schema = GlobalKeywordsTableConfig.SCHEMA
            table_name = GlobalKeywordsTableConfig.get_table_name(settings.TABLE_ENVIRONMENT)
            
            # Create the global_keywords table using schema configuration
            table_created = dynamodb_client.create_table(
                table_name=table_name,
                key_schema=keywords_schema["key_schema"],
                attribute_definitions=keywords_schema["attribute_definitions"],
                billing_mode=keywords_schema["billing_mode"]
            )
            
            if table_created:
                logger.info(f"Successfully created global_keywords table: {table_name}")
            else:
                logger.info(f"Global_keywords table {table_name} already exists")
                
            # Add some initial data if needed
            await self._create_initial_data()
                
        except Exception as e:
            logger.error(f"Error creating global_keywords table: {str(e)}")
            raise
    
    async def down(self):
        """Rollback the migration"""
        logger.info("Rolling back global_keywords table creation")
        
        try:
            # Delete the global_keywords table
            table_name = GlobalKeywordsTableConfig.get_table_name(settings.TABLE_ENVIRONMENT)
            table_deleted = dynamodb_client.delete_table(table_name)
            
            if table_deleted:
                logger.info(f"Successfully deleted global_keywords table: {table_name}")
            else:
                logger.warning(f"Global_keywords table {table_name} did not exist")
                
        except Exception as e:
            logger.error(f"Error deleting global_keywords table: {str(e)}")
            raise
    
    async def _create_initial_data(self):
        """Create initial test data for development"""
        if not settings.is_development:
            return
            
        logger.info("Creating initial test data for global keywords")
        
        try:
            from app.repositories.global_keywords_repository import GlobalKeywordsRepository
            from app.models.global_keywords_model import GlobalKeywordsModel
            
            keywords_repo = GlobalKeywordsRepository()
            
            # Sample pharmaceutical keywords
            sample_keywords = [
                {"keyword": "oncology", "keyword_type": "therapeutic_area"},
                {"keyword": "cardiology", "keyword_type": "therapeutic_area"},
                {"keyword": "neurology", "keyword_type": "therapeutic_area"},
                {"keyword": "immunology", "keyword_type": "therapeutic_area"},
                {"keyword": "pharmacovigilance", "keyword_type": "safety"},
                {"keyword": "adverse_event", "keyword_type": "safety"},
                {"keyword": "drug_interaction", "keyword_type": "safety"},
                {"keyword": "clinical_trial", "keyword_type": "research"},
                {"keyword": "biomarker", "keyword_type": "research"},
                {"keyword": "efficacy", "keyword_type": "research"},
                {"keyword": "FDA_approval", "keyword_type": "regulatory"},
                {"keyword": "EMA_approval", "keyword_type": "regulatory"},
                {"keyword": "phase_I", "keyword_type": "clinical_phase"},
                {"keyword": "phase_II", "keyword_type": "clinical_phase"},
                {"keyword": "phase_III", "keyword_type": "clinical_phase"},
                {"keyword": "molecular_target", "keyword_type": "mechanism"},
                {"keyword": "protein_kinase", "keyword_type": "mechanism"},
                {"keyword": "receptor_antagonist", "keyword_type": "mechanism"},
                {"keyword": "market_analysis", "keyword_type": "commercial"},
                {"keyword": "competitive_landscape", "keyword_type": "commercial"}
            ]
            
            for keyword_data in sample_keywords:
                # Check if keyword already exists
                keyword_exists = await keywords_repo.exists({"keyword": keyword_data["keyword"]})
                
                if not keyword_exists:
                    keyword = GlobalKeywordsModel.create_new(
                        keyword=keyword_data["keyword"],
                        keyword_type=keyword_data["keyword_type"]
                    )
                    
                    await keywords_repo.create(keyword)
                    logger.info(f"Created global keyword: {keyword_data['keyword']} ({keyword_data['keyword_type']})")
                
        except Exception as e:
            logger.warning(f"Could not create initial global keywords data: {str(e)}") 