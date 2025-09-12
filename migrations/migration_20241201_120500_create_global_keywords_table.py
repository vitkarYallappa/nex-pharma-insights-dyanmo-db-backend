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
            
            # Obesity and metabolic keywords
            sample_keywords = [
                # Obesity and metabolic therapeutic area
                {"keyword": "Obesity", "keyword_type": "therapeutic_area"},
                {"keyword": "Overweight", "keyword_type": "therapeutic_area"},
                {"keyword": "Weight loss", "keyword_type": "therapeutic_area"},
                {"keyword": "Obese", "keyword_type": "therapeutic_area"},
                
                # Obesity drug compounds and investigational drugs
                {"keyword": "Retatrutide", "keyword_type": "drug_compound"},
                {"keyword": "LY-3437943", "keyword_type": "drug_compound"},
                {"keyword": "LY-3502970", "keyword_type": "drug_compound"},
                {"keyword": "Orforglipron", "keyword_type": "drug_compound"},
                {"keyword": "OWL833", "keyword_type": "drug_compound"},
                {"keyword": "AZD5004", "keyword_type": "drug_compound"},
                {"keyword": "Pemvidutide", "keyword_type": "drug_compound"},
                {"keyword": "ALT-801", "keyword_type": "drug_compound"},
                {"keyword": "AMG133", "keyword_type": "drug_compound"},
                {"keyword": "BI456906", "keyword_type": "drug_compound"},
                {"keyword": "AZD9550", "keyword_type": "drug_compound"},
                {"keyword": "TG103", "keyword_type": "drug_compound"},
                {"keyword": "GLY200", "keyword_type": "drug_compound"},
                {"keyword": "NEX22", "keyword_type": "drug_compound"},
                {"keyword": "Cagrisema", "keyword_type": "drug_compound"},
                {"keyword": "Mazdutide", "keyword_type": "drug_compound"},
                {"keyword": "LY3841136", "keyword_type": "drug_compound"},
                {"keyword": "MBL949", "keyword_type": "drug_compound"},
                {"keyword": "NNC0165-1875", "keyword_type": "drug_compound"},
                {"keyword": "LY3457263", "keyword_type": "drug_compound"},
                {"keyword": "S-309309", "keyword_type": "drug_compound"},
                
                # Approved obesity/diabetes drugs
                {"keyword": "Wegovy", "keyword_type": "approved_drug"},
                {"keyword": "Ozempic", "keyword_type": "approved_drug"},
                {"keyword": "Rybelsus", "keyword_type": "approved_drug"},
                {"keyword": "Mounjaro", "keyword_type": "approved_drug"},
                {"keyword": "Trulicity", "keyword_type": "approved_drug"},
                {"keyword": "Saxenda", "keyword_type": "approved_drug"},
                {"keyword": "Victoza", "keyword_type": "approved_drug"},
                {"keyword": "Exenatide", "keyword_type": "approved_drug"},
                {"keyword": "Liraglutide", "keyword_type": "approved_drug"},
                {"keyword": "Bydureon", "keyword_type": "approved_drug"},
                {"keyword": "Byetta", "keyword_type": "approved_drug"},
                
                # Metabolic hormone mechanisms
                {"keyword": "GLP-1", "keyword_type": "mechanism"},
                {"keyword": "GIP", "keyword_type": "mechanism"},
                {"keyword": "Amylin", "keyword_type": "mechanism"},
                {"keyword": "GCG", "keyword_type": "mechanism"}
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