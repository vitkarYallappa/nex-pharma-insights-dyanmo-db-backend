"""
Content URL Mapping Service - Works with ContentUrlMappingModel and ContentUrlMappingRepository
Follows the same pattern as ProjectService for consistency
"""

from typing import List, Optional, Dict, Any
from app.repositories.content_url_mapping_repository import ContentUrlMappingRepository
from app.models.content_url_mapping_model import ContentUrlMappingModel
from app.core.logging import get_logger
from app.core.exceptions import (
    ValidationException
)

logger = get_logger("content_url_mapping_service")

class ContentUrlMappingNotFoundException(Exception):
    """Exception raised when content URL mapping entry is not found"""
    pass

class ContentUrlMappingAlreadyExistsException(Exception):
    """Exception raised when content URL mapping entry already exists"""
    pass

class ContentUrlMappingService:
    """Content URL mapping service with essential operations"""
    
    def __init__(self):
        self.mapping_repository = ContentUrlMappingRepository()
        self.logger = logger
    
    async def create_content_url_mapping(self, discovered_url: str, title: str, content_id: str,
                            source_domain: Optional[str] = None, is_canonical: Optional[bool] = None,
                            dedup_confidence: Optional[str] = None, dedup_method: Optional[str] = None) -> ContentUrlMappingModel:
        """Create a new content URL mapping entry"""
        try:
            # Validate required fields
            if not discovered_url or not discovered_url.strip():
                raise ValidationException("Discovered URL is required")
            
            if not title or not title.strip():
                raise ValidationException("Title is required")
            
            if not content_id or not content_id.strip():
                raise ValidationException("Content ID is required")
            
            # Validate dedup_confidence range if provided
            if dedup_confidence is not None and (dedup_confidence < 0.0 or dedup_confidence > 1.0):
                raise ValidationException("Deduplication confidence must be between 0.0 and 1.0")
            
            # Create mapping model
            mapping_model = ContentUrlMappingModel.create_new(
                discovered_url=discovered_url.strip(),
                title=title.strip(),
                content_id=content_id.strip(),
                source_domain=source_domain.strip() if source_domain else None,
                is_canonical=is_canonical,
                dedup_confidence=dedup_confidence,
                dedup_method=dedup_method.strip() if dedup_method else None
            )
            
            # Save to database
            created_mapping = await self.mapping_repository.create(mapping_model)
            self.logger.info(f"Content URL mapping entry created: {discovered_url} for content {content_id}")
            return created_mapping
            
        except ValidationException:
            raise
        except Exception as e:
            self.logger.error(f"Create content URL mapping entry failed: {str(e)}")
            raise
    
    async def get_content_url_mapping_by_id(self, url_id: str) -> ContentUrlMappingModel:
        """Get content URL mapping entry by ID"""
        try:
            if not url_id or not url_id.strip():
                raise ValidationException("URL ID is required")
            
            mapping = await self.mapping_repository.find_one_by_query({"pk": url_id.strip()})
            if not mapping:
                raise ContentUrlMappingNotFoundException(f"Content URL mapping entry with ID {url_id} not found")
            
            return mapping
            
        except (ContentUrlMappingNotFoundException, ValidationException):
            raise
        except Exception as e:
            self.logger.error(f"Get content URL mapping entry by ID failed: {str(e)}")
            raise
    
    async def get_content_url_mapping_by_query(self, content_id: Optional[str] = None,
                                   source_domain: Optional[str] = None,
                                   is_canonical: Optional[bool] = None,
                                   dedup_method: Optional[str] = None,
                                   limit: Optional[int] = None) -> List[ContentUrlMappingModel]:
        """Get content URL mapping entries with optional filters"""
        try:
            # Validate limit
            if limit is not None and limit <= 0:
                raise ValidationException("Limit must be a positive number")
            
            mappings = await self.mapping_repository.get_all_content_url_mapping(
                content_id=content_id.strip() if content_id else None,
                source_domain=source_domain.strip() if source_domain else None,
                is_canonical=is_canonical,
                dedup_method=dedup_method.strip() if dedup_method else None,
                limit=limit
            )
            
            self.logger.info(f"Retrieved {len(mappings)} content URL mapping entries with filters: content_id={content_id}, source_domain={source_domain}, is_canonical={is_canonical}, dedup_method={dedup_method}")
            return mappings
            
        except ValidationException:
            raise
        except Exception as e:
            self.logger.error(f"Get content URL mapping entries by query failed: {str(e)}")
            raise
    
    async def update_content_url_mapping(self, url_id: str, update_data: Dict[str, Any]) -> ContentUrlMappingModel:
        """Update content URL mapping entry by ID"""
        try:
            if not url_id or not url_id.strip():
                raise ValidationException("URL ID is required")
            
            # Check if mapping exists
            existing_mapping = await self.get_content_url_mapping_by_id(url_id)
            
            # Validate dedup_confidence if being updated
            if "dedup_confidence" in update_data and update_data["dedup_confidence"] is not None:
                confidence = update_data["dedup_confidence"]
                if confidence < 0.0 or confidence > 1.0:
                    raise ValidationException("Deduplication confidence must be between 0.0 and 1.0")
            
            # Prepare update data (remove None values)
            clean_update_data = {k: v for k, v in update_data.items() if v is not None}
            
            updated_mapping = await self.mapping_repository.update_content_url_mapping(
                url_id.strip(), clean_update_data
            )
            
            if not updated_mapping:
                raise ContentUrlMappingNotFoundException(f"Failed to update content URL mapping entry with ID {url_id}")
            
            self.logger.info(f"Content URL mapping entry updated: {url_id}")
            return updated_mapping
            
        except (ContentUrlMappingNotFoundException, ValidationException):
            raise
        except Exception as e:
            self.logger.error(f"Update content URL mapping entry failed: {str(e)}")
            raise
