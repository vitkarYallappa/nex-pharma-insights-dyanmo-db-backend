"""
Content Implication Service - Works with ContentImplicationModel and ContentImplicationRepository
Follows the same pattern as ProjectService for consistency
"""

from typing import List, Optional, Dict, Any
from app.repositories.content_implication_repository import ContentImplicationRepository
from app.models.content_implication_model import ContentImplicationModel
from app.core.logging import get_logger
from app.core.exceptions import (
    ValidationException
)

logger = get_logger("content_implication_service")

class ContentImplicationNotFoundException(Exception):
    """Exception raised when content implication entry is not found"""
    pass

class ContentImplicationAlreadyExistsException(Exception):
    """Exception raised when content implication entry already exists"""
    pass

class ContentImplicationService:
    """Content implication service with essential operations"""
    
    def __init__(self):
        self.implication_repository = ContentImplicationRepository()
        self.logger = logger
    
    async def create_content_implication(self, url_id: str, content_id: str, implication_text: str,
                            implication_content_file_path: Optional[str] = None, implication_type: Optional[str] = None,
                            priority_level: Optional[str] = None, confidence_score: Optional[float] = None,
                            version: Optional[int] = None, is_canonical: Optional[bool] = None,
                            preferred_choice: Optional[bool] = None, created_by: Optional[str] = None) -> ContentImplicationModel:
        """Create a new content implication entry"""
        try:
            # Validate required fields
            if not url_id or not url_id.strip():
                raise ValidationException("URL ID is required")
            
            if not content_id or not content_id.strip():
                raise ValidationException("Content ID is required")
            
            if not implication_text or not implication_text.strip():
                raise ValidationException("Implication text is required")
            
            # Validate confidence_score range if provided
            if confidence_score is not None and (confidence_score < 0.0 or confidence_score > 1.0):
                raise ValidationException("Confidence score must be between 0.0 and 1.0")
            
            # Create implication model
            implication_model = ContentImplicationModel.create_new(
                url_id=url_id.strip(),
                content_id=content_id.strip(),
                implication_text=implication_text.strip(),
                implication_content_file_path=implication_content_file_path.strip() if implication_content_file_path else None,
                implication_type=implication_type.strip() if implication_type else None,
                priority_level=priority_level.strip() if priority_level else None,
                confidence_score=confidence_score,
                version=version,
                is_canonical=is_canonical,
                preferred_choice=preferred_choice,
                created_by=created_by.strip() if created_by else None
            )
            
            # Save to database
            created_implication = await self.implication_repository.create(implication_model)
            self.logger.info(f"Content implication entry created for content {content_id} and URL {url_id}")
            return created_implication
            
        except ValidationException:
            raise
        except Exception as e:
            self.logger.error(f"Create content implication entry failed: {str(e)}")
            raise
    
    async def get_content_implication_by_id(self, implication_id: str) -> ContentImplicationModel:
        """Get content implication entry by ID"""
        try:
            if not implication_id or not implication_id.strip():
                raise ValidationException("Implication ID is required")
            
            implication = await self.implication_repository.find_one_by_query({"pk": implication_id.strip()})
            if not implication:
                raise ContentImplicationNotFoundException(f"Content implication entry with ID {implication_id} not found")
            
            return implication
            
        except (ContentImplicationNotFoundException, ValidationException):
            raise
        except Exception as e:
            self.logger.error(f"Get content implication entry by ID failed: {str(e)}")
            raise
    
    async def get_content_implication_by_query(self, url_id: Optional[str] = None,
                                   content_id: Optional[str] = None,
                                   implication_type: Optional[str] = None,
                                   priority_level: Optional[str] = None,
                                   is_canonical: Optional[bool] = None,
                                   preferred_choice: Optional[bool] = None,
                                   version: Optional[int] = None,
                                   created_by: Optional[str] = None,
                                   limit: Optional[int] = None) -> List[ContentImplicationModel]:
        """Get content implication entries with optional filters"""
        try:
            # Validate limit
            if limit is not None and limit <= 0:
                raise ValidationException("Limit must be a positive number")
            
            implications = await self.implication_repository.get_all_content_implication(
                url_id=url_id.strip() if url_id else None,
                content_id=content_id.strip() if content_id else None,
                implication_type=implication_type.strip() if implication_type else None,
                priority_level=priority_level.strip() if priority_level else None,
                is_canonical=is_canonical,
                preferred_choice=preferred_choice,
                version=version,
                created_by=created_by.strip() if created_by else None,
                limit=limit
            )
            
            self.logger.info(f"Retrieved {len(implications)} content implication entries with filters: url_id={url_id}, content_id={content_id}, implication_type={implication_type}, priority_level={priority_level}, is_canonical={is_canonical}, preferred_choice={preferred_choice}, version={version}, created_by={created_by}")
            return implications
            
        except ValidationException:
            raise
        except Exception as e:
            self.logger.error(f"Get content implication entries by query failed: {str(e)}")
            raise
    
    async def update_content_implication(self, implication_id: str, update_data: Dict[str, Any]) -> ContentImplicationModel:
        """Update content implication entry by ID"""
        try:
            if not implication_id or not implication_id.strip():
                raise ValidationException("Implication ID is required")
            
            # Check if implication exists
            existing_implication = await self.get_content_implication_by_id(implication_id)
            
            # Validate confidence_score if being updated
            if "confidence_score" in update_data and update_data["confidence_score"] is not None:
                confidence = update_data["confidence_score"]
                if confidence < 0.0 or confidence > 1.0:
                    raise ValidationException("Confidence score must be between 0.0 and 1.0")
            
            # Prepare update data (remove None values)
            clean_update_data = {k: v for k, v in update_data.items() if v is not None}
            
            updated_implication = await self.implication_repository.update_content_implication(
                implication_id.strip(), clean_update_data
            )
            
            if not updated_implication:
                raise ContentImplicationNotFoundException(f"Failed to update content implication entry with ID {implication_id}")
            
            self.logger.info(f"Content implication entry updated: {implication_id}")
            return updated_implication
            
        except (ContentImplicationNotFoundException, ValidationException):
            raise
        except Exception as e:
            self.logger.error(f"Update content implication entry failed: {str(e)}")
            raise
    
