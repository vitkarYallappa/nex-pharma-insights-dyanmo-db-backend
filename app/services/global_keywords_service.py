"""
Global Keywords Service - Works with GlobalKeywordsModel and GlobalKeywordsRepository
Follows the same pattern as ProjectService for consistency
"""

from typing import List, Optional, Dict, Any
from app.repositories.global_keywords_repository import GlobalKeywordsRepository
from app.models.global_keywords_model import GlobalKeywordsModel
from app.core.logging import get_logger
from app.core.exceptions import (
    ValidationException
)

logger = get_logger("global_keywords_service")

class GlobalKeywordsNotFoundException(Exception):
    """Exception raised when global keyword is not found"""
    pass

class GlobalKeywordsAlreadyExistsException(Exception):
    """Exception raised when global keyword already exists"""
    pass

class GlobalKeywordsService:
    """Global keywords service with essential operations"""
    
    def __init__(self):
        self.keywords_repository = GlobalKeywordsRepository()
        self.logger = logger
    
    async def create_global_keyword(self, keyword: str, keyword_type: Optional[str] = None) -> GlobalKeywordsModel:
        """Create a new global keyword"""
        try:
            # Validate required fields
            if not keyword or not keyword.strip():
                raise ValidationException("Keyword is required")
            
            # Create keyword model
            keyword_model = GlobalKeywordsModel.create_new(
                keyword=keyword.strip(),
                keyword_type=keyword_type.strip() if keyword_type else None
            )
            
            # Save to database
            created_keyword = await self.keywords_repository.create(keyword_model)
            self.logger.info(f"Global keyword created: {keyword}")
            return created_keyword
            
        except ValidationException:
            raise
        except Exception as e:
            self.logger.error(f"Create global keyword failed: {str(e)}")
            raise
    
    async def get_global_keyword_by_id(self, keyword_id: str) -> GlobalKeywordsModel:
        """Get global keyword by ID"""
        try:
            if not keyword_id or not keyword_id.strip():
                raise ValidationException("Keyword ID is required")
            
            keyword = await self.keywords_repository.find_one_by_query({"pk": keyword_id.strip()})
            if not keyword:
                raise GlobalKeywordsNotFoundException(f"Global keyword with ID {keyword_id} not found")
            
            return keyword
            
        except (GlobalKeywordsNotFoundException, ValidationException):
            raise
        except Exception as e:
            self.logger.error(f"Get global keyword by ID failed: {str(e)}")
            raise
    
    async def get_all_global_keyword(self, keyword_type: Optional[str] = None,
                                   limit: Optional[int] = None) -> List[GlobalKeywordsModel]:
        """Get global keywords with optional filters"""
        try:
            # Validate limit
            if limit is not None and limit <= 0:
                raise ValidationException("Limit must be a positive number")
            
            keywords = await self.keywords_repository.get_all_global_keyword(
                keyword_type=keyword_type.strip() if keyword_type else None,
                limit=limit
            )
            
            self.logger.info(f"Retrieved {len(keywords)} global keywords with filters: keyword_type={keyword_type}")
            return keywords
            
        except ValidationException:
            raise
        except Exception as e:
            self.logger.error(f"Get global keywords by query failed: {str(e)}")
            raise
    
    async def update_global_keyword(self, keyword_id: str, update_data: Dict[str, Any]) -> GlobalKeywordsModel:
        """Update global keyword by ID"""
        try:
            if not keyword_id or not keyword_id.strip():
                raise ValidationException("Keyword ID is required")
            
            # Check if keyword exists
            existing_keyword = await self.get_global_keyword_by_id(keyword_id)
            
            # Prepare update data (remove None values and add updated_at)
            clean_update_data = {k: v for k, v in update_data.items() if v is not None}
            if clean_update_data:
                from datetime import datetime
                clean_update_data["updated_at"] = datetime.utcnow().isoformat()
            
            updated_keyword = await self.keywords_repository.update_global_keyword(
                keyword_id.strip(), clean_update_data
            )
            
            if not updated_keyword:
                raise GlobalKeywordsNotFoundException(f"Failed to update global keyword with ID {keyword_id}")
            
            self.logger.info(f"Global keyword updated: {keyword_id}")
            return updated_keyword
            
        except (GlobalKeywordsNotFoundException, ValidationException):
            raise
        except Exception as e:
            self.logger.error(f"Update global keyword failed: {str(e)}")
            raise 