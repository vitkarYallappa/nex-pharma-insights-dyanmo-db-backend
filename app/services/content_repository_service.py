"""
Content Repository Service - Works with ContentRepositoryModel and ContentRepositoryRepository
Follows the same pattern as ProjectService for consistency
"""

from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timedelta
from app.repositories.content_repository_repository import ContentRepositoryRepository
from app.models.content_repository_model import ContentRepositoryModel
from app.services.content_repository_metadata_service import ContentRepositoryMetadataService
from app.services.content_relevance_service import ContentRelevanceService
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
        self.metadata_service = ContentRepositoryMetadataService()
        self.relevance_service = ContentRelevanceService()
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
    
    async def get_all_by_query(self, query_filters: Optional[Dict[str, Any]] = None, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get all content repository entries by query filters with enhanced metadata"""
        try:
            # Validate limit if provided
            if limit is not None and limit <= 0:
                raise ValidationException("Limit must be greater than 0")
            
            # Get entries from repository
            entries = await self.content_repository.find_all_by_query(query=query_filters, limit=limit)
            
            # Convert to model objects and enhance with additional metadata
            enhanced_content_list = []
            for entry in entries:
                if isinstance(entry, ContentRepositoryModel):
                    content_model = entry
                else:
                    content_model = ContentRepositoryModel.from_dict(entry)
                
                # Enhance content and convert to dict with all fields
                enhanced_content = await self._enhance_content_with_metadata(content_model)
                enhanced_content_list.append(enhanced_content)
            
            self.logger.info(f"Retrieved {len(enhanced_content_list)} content repository entries with enhanced metadata")
            return enhanced_content_list
            
        except ValidationException:
            raise
        except Exception as e:
            self.logger.error(f"Get content repository entries by query failed: {str(e)}")
            raise
    
    async def _enhance_content_with_metadata(self, content_model: ContentRepositoryModel) -> Dict[str, Any]:
        """Add three keys to existing content object and return as dict with all fields accessible"""
        try:
            # Start with all existing content model fields
            content_dict = content_model.to_dict()
            
            # Check if metadata exists for this content
            existing_metadata = await self.metadata_service.get_metadata_by_content_id(content_model.pk, limit=1)
            
            # Add publish_date (one day minus - yesterday)
            yesterday = datetime.utcnow() - timedelta(days=1)
            if existing_metadata:
                # Use existing metadata value if available
                content_dict['publish_date'] = existing_metadata[0].metadata_value
            else:
                # Use yesterday's timestamp as dummy publish date
                content_dict['publish_date'] = yesterday.isoformat()
            
            # Add source_type - use existing or dummy if not found
            if hasattr(content_model, 'source_type') and content_model.source_type:
                content_dict['source_type'] = content_model.source_type
            else:
                # Add dummy source type when not found
                content_dict['source_type'] = 'dummy_source'
            
            # Check relevance and add relevance_check
            existing_relevance = await self.relevance_service.get_relevance_by_content_id(content_model.pk)
            if existing_relevance:
                content_dict['relevance_check'] = existing_relevance.is_relevant
            else:
                # Default to True for dummy relevance check
                content_dict['relevance_check'] = True
                
            self.logger.debug(f"Enhanced content {content_model.pk} with metadata keys")
            return content_dict
                
        except Exception as e:
            self.logger.warning(f"Failed to enhance content {content_model.pk} with metadata: {str(e)}")
            # Set default values if enhancement fails - don't let this break the main flow
            try:
                content_dict = content_model.to_dict()
                yesterday = datetime.utcnow() - timedelta(days=1)
                content_dict['publish_date'] = yesterday.isoformat()
                content_dict['source_type'] = 'dummy_source'
                content_dict['relevance_check'] = True
                return content_dict
            except Exception as fallback_error:
                self.logger.warning(f"Fallback enhancement also failed for content {content_model.pk}: {str(fallback_error)}")
                # Absolute fallback with hardcoded values
                return {
                    'pk': getattr(content_model, 'pk', 'unknown'),
                    'publish_date': '2025-09-11T00:00:00',
                    'source_type': 'dummy_source',
                    'relevance_check': True
                } 