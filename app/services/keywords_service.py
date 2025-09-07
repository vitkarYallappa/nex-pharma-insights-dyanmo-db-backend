"""
Keywords Service - Works with KeywordsModel and KeywordsRepository
Follows the same pattern as ProjectService for consistency
"""

from typing import List, Optional, Dict, Any
from app.repositories.keywords_repository import KeywordsRepository
from app.models.keywords_model import KeywordsModel
from app.core.logging import get_logger
from app.core.exceptions import (
    ValidationException
)

logger = get_logger("keywords_service")

class KeywordsNotFoundException(Exception):
    """Exception raised when keyword is not found"""
    pass

class KeywordsAlreadyExistsException(Exception):
    """Exception raised when keyword already exists"""
    pass

class KeywordsService:
    """Keywords service with essential operations"""
    
    def __init__(self):
        self.keywords_repository = KeywordsRepository()
        self.logger = logger
    
    async def create_keyword(self, keyword: str, request_id: str, keyword_type: Optional[str] = None) -> KeywordsModel:
        """Create a new keyword"""
        try:
            # Validate required fields
            if not keyword or not keyword.strip():
                raise ValidationException("Keyword is required")
            
            if not request_id or not request_id.strip():
                raise ValidationException("Request ID is required")
            
            # Create keyword model
            keyword_model = KeywordsModel.create_new(
                keyword=keyword.strip(),
                request_id=request_id.strip(),
                keyword_type=keyword_type.strip() if keyword_type else None
            )
            
            # Save to database
            created_keyword = await self.keywords_repository.create(keyword_model)
            self.logger.info(f"Keyword created: {keyword} for request {request_id}")
            return created_keyword
            
        except ValidationException:
            raise
        except Exception as e:
            self.logger.error(f"Create keyword failed: {str(e)}")
            raise
    
    async def get_keyword_by_id(self, keyword_id: str) -> KeywordsModel:
        """Get keyword by ID"""
        try:
            if not keyword_id or not keyword_id.strip():
                raise ValidationException("Keyword ID is required")
            
            keyword = await self.keywords_repository.find_one_by_query({"pk": keyword_id.strip()})
            if not keyword:
                raise KeywordsNotFoundException(f"Keyword with ID {keyword_id} not found")
            
            return keyword
            
        except (KeywordsNotFoundException, ValidationException):
            raise
        except Exception as e:
            self.logger.error(f"Get keyword by ID failed: {str(e)}")
            raise
    
    async def get_keyword_by_query(self, request_id: Optional[str] = None,
                                   keyword_type: Optional[str] = None,
                                   limit: Optional[int] = None) -> List[KeywordsModel]:
        """Get keywords with optional filters"""
        try:
            # Validate limit
            if limit is not None and limit <= 0:
                raise ValidationException("Limit must be a positive number")
            
            keywords = await self.keywords_repository.get_all_keyword(
                request_id=request_id.strip() if request_id else None,
                keyword_type=keyword_type.strip() if keyword_type else None,
                limit=limit
            )
            
            self.logger.info(f"Retrieved {len(keywords)} keywords with filters: request_id={request_id}, keyword_type={keyword_type}")
            return keywords
            
        except ValidationException:
            raise
        except Exception as e:
            self.logger.error(f"Get keywords by query failed: {str(e)}")
            raise
    
    async def update_keyword(self, keyword_id: str, update_data: Dict[str, Any]) -> KeywordsModel:
        """Update keyword by ID"""
        try:
            if not keyword_id or not keyword_id.strip():
                raise ValidationException("Keyword ID is required")
            
            # Check if keyword exists
            existing_keyword = await self.get_keyword_by_id(keyword_id)
            
            # Prepare update data (remove None values and add updated_at)
            clean_update_data = {k: v for k, v in update_data.items() if v is not None}
            if clean_update_data:
                from datetime import datetime
                clean_update_data["updated_at"] = datetime.utcnow().isoformat()
            
            updated_keyword = await self.keywords_repository.update_keyword(
                keyword_id.strip(), clean_update_data
            )
            
            if not updated_keyword:
                raise KeywordsNotFoundException(f"Failed to update keyword with ID {keyword_id}")
            
            self.logger.info(f"Keyword updated: {keyword_id}")
            return updated_keyword
            
        except (KeywordsNotFoundException, ValidationException):
            raise
        except Exception as e:
            self.logger.error(f"Update keyword failed: {str(e)}")
            raise 