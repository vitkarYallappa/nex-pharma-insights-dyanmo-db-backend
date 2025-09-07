"""
Content Repository Service - Works with ContentRepositoryModel and ContentRepositoryRepository
Follows the same pattern as ProjectService for consistency
"""

from typing import List, Optional, Dict, Any
from app.repositories.content_repository_repository import ContentRepositoryRepository
from app.models.content_repository_model import ContentRepositoryModel
from app.core.logging import get_logger
from app.core.exceptions import (
    ValidationException
)

logger = get_logger("content_repository_service")

class ContentRepositoryNotFoundException(Exception):
    """Exception raised when content repository entry is not found"""
    pass

class ContentRepositoryAlreadyExistsException(Exception):
    """Exception raised when content repository entry already exists"""
    pass

class ContentRepositoryService:
    """Content repository service with essential operations"""
    
    def __init__(self):
        self.content_repository = ContentRepositoryRepository()
        self.logger = logger
    
    async def create_content_repository(self, request_id: str, project_id: str, canonical_url: str, title: str,
                            content_hash: str, source_type: str, relevance_type: str,
                            version: Optional[int] = None, is_canonical: Optional[bool] = None) -> ContentRepositoryModel:
        """Create a new content repository entry"""
        try:
            # Validate required fields
            if not request_id or not request_id.strip():
                raise ValidationException("Request ID is required")
            
            if not project_id or not project_id.strip():
                raise ValidationException("Project ID is required")
            
            if not canonical_url or not canonical_url.strip():
                raise ValidationException("Canonical URL is required")
            
            if not title or not title.strip():
                raise ValidationException("Title is required")
            
            if not content_hash or not content_hash.strip():
                raise ValidationException("Content hash is required")
            
            if not source_type or not source_type.strip():
                raise ValidationException("Source type is required")
            
            if not relevance_type or not relevance_type.strip():
                raise ValidationException("Relevance type is required")
            
            # Create content model
            content_model = ContentRepositoryModel.create_new(
                request_id=request_id.strip(),
                project_id=project_id.strip(),
                canonical_url=canonical_url.strip(),
                title=title.strip(),
                content_hash=content_hash.strip(),
                source_type=source_type.strip(),
                relevance_type=relevance_type.strip(),
                version=version,
                is_canonical=is_canonical
            )
            
            # Save to database
            created_content = await self.content_repository.create(content_model)
            self.logger.info(f"Content repository entry created: {title} for request {request_id}")
            return created_content
            
        except ValidationException:
            raise
        except Exception as e:
            self.logger.error(f"Create content repository entry failed: {str(e)}")
            raise
    
    async def get_content_repository_by_id(self, content_id: str) -> ContentRepositoryModel:
        """Get content repository entry by ID"""
        try:
            if not content_id or not content_id.strip():
                raise ValidationException("Content ID is required")
            
            content = await self.content_repository.find_one_by_query({"pk": content_id.strip()})
            if not content:
                raise ContentRepositoryNotFoundException(f"Content repository entry with ID {content_id} not found")
            
            return content
            
        except (ContentRepositoryNotFoundException, ValidationException):
            raise
        except Exception as e:
            self.logger.error(f"Get content repository entry by ID failed: {str(e)}")
            raise
    
    async def get_all_content_repository(self, request_id: Optional[str] = None,
                                   project_id: Optional[str] = None,
                                   source_type: Optional[str] = None,
                                   relevance_type: Optional[str] = None,
                                   is_canonical: Optional[bool] = None,
                                   limit: Optional[int] = None) -> List[ContentRepositoryModel]:
        """Get content repository entries with optional filters"""
        try:
            # Validate limit
            if limit is not None and limit <= 0:
                raise ValidationException("Limit must be a positive number")
            
            contents = await self.content_repository.get_all_content_repository(
                request_id=request_id.strip() if request_id else None,
                project_id=project_id.strip() if project_id else None,
                source_type=source_type.strip() if source_type else None,
                relevance_type=relevance_type.strip() if relevance_type else None,
                is_canonical=is_canonical,
                limit=limit
            )
            
            self.logger.info(f"Retrieved {len(contents)} content repository entries with filters: request_id={request_id}, project_id={project_id}, source_type={source_type}, relevance_type={relevance_type}, is_canonical={is_canonical}")
            return contents
            
        except ValidationException:
            raise
        except Exception as e:
            self.logger.error(f"Get content repository entries by query failed: {str(e)}")
            raise
    
    async def update_content_repository(self, content_id: str, update_data: Dict[str, Any]) -> ContentRepositoryModel:
        """Update content repository entry by ID"""
        try:
            if not content_id or not content_id.strip():
                raise ValidationException("Content ID is required")
            
            # Check if content exists
            existing_content = await self.get_content_repository_by_id(content_id)
            
            # Prepare update data (remove None values and add updated_at)
            clean_update_data = {k: v for k, v in update_data.items() if v is not None}
            if clean_update_data:
                from datetime import datetime
                clean_update_data["updated_at"] = datetime.utcnow().isoformat()
            
            updated_content = await self.content_repository.update_content_repository(
                content_id.strip(), clean_update_data
            )
            
            if not updated_content:
                raise ContentRepositoryNotFoundException(f"Failed to update content repository entry with ID {content_id}")
            
            self.logger.info(f"Content repository entry updated: {content_id}")
            return updated_content
            
        except (ContentRepositoryNotFoundException, ValidationException):
            raise
        except Exception as e:
            self.logger.error(f"Update content repository entry failed: {str(e)}")
            raise 