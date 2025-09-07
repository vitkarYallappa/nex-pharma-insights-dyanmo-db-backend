"""
Content Analysis Mapping Service - Works with ContentAnalysisMappingModel and ContentAnalysisMappingRepository
Follows the same pattern as ProjectService for consistency
"""

from typing import List, Optional, Dict, Any
from app.repositories.content_analysis_mapping_repository import ContentAnalysisMappingRepository
from app.models.content_analysis_mapping_model import ContentAnalysisMappingModel
from app.core.logging import get_logger
from app.core.exceptions import (
    ValidationException
)

logger = get_logger("content_analysis_mapping_service")

class ContentAnalysisMappingNotFoundException(Exception):
    """Exception raised when content analysis mapping entry is not found"""
    pass

class ContentAnalysisMappingAlreadyExistsException(Exception):
    """Exception raised when content analysis mapping entry already exists"""
    pass

class ContentAnalysisMappingService:
    """Content analysis mapping service with essential operations"""
    
    def __init__(self):
        self.mapping_repository = ContentAnalysisMappingRepository()
        self.logger = logger
    
    async def create_analysis_mapping(self, content_id: str, primary_summary_id: Optional[str] = None,
                            primary_insight_id: Optional[str] = None, primary_implication_id: Optional[str] = None,
                            selection_strategy: Optional[str] = None, selection_context: Optional[str] = None,
                            selected_by: Optional[str] = None, version: Optional[int] = None,
                            is_current: Optional[bool] = None) -> ContentAnalysisMappingModel:
        """Create a new content analysis mapping entry"""
        try:
            # Validate required fields
            if not content_id or not content_id.strip():
                raise ValidationException("Content ID is required")
            
            # Validate that at least one primary ID is provided
            if not any([primary_summary_id, primary_insight_id, primary_implication_id]):
                raise ValidationException("At least one primary ID (summary, insight, or implication) is required")
            
            # Create mapping model
            mapping_model = ContentAnalysisMappingModel.create_new(
                content_id=content_id.strip(),
                primary_summary_id=primary_summary_id.strip() if primary_summary_id else None,
                primary_insight_id=primary_insight_id.strip() if primary_insight_id else None,
                primary_implication_id=primary_implication_id.strip() if primary_implication_id else None,
                selection_strategy=selection_strategy.strip() if selection_strategy else None,
                selection_context=selection_context.strip() if selection_context else None,
                selected_by=selected_by.strip() if selected_by else None,
                version=version,
                is_current=is_current
            )
            
            # Save to database
            created_mapping = await self.mapping_repository.create(mapping_model)
            self.logger.info(f"Content analysis mapping entry created for content {content_id}")
            return created_mapping
            
        except ValidationException:
            raise
        except Exception as e:
            self.logger.error(f"Create content analysis mapping entry failed: {str(e)}")
            raise
    
    async def get_analysis_mapping_by_id(self, mapping_id: str) -> ContentAnalysisMappingModel:
        """Get content analysis mapping entry by ID"""
        try:
            if not mapping_id or not mapping_id.strip():
                raise ValidationException("Mapping ID is required")
            
            mapping = await self.mapping_repository.find_one_by_query({"pk": mapping_id.strip()})
            if not mapping:
                raise ContentAnalysisMappingNotFoundException(f"Content analysis mapping entry with ID {mapping_id} not found")
            
            return mapping
            
        except (ContentAnalysisMappingNotFoundException, ValidationException):
            raise
        except Exception as e:
            self.logger.error(f"Get content analysis mapping entry by ID failed: {str(e)}")
            raise
    
    async def get_analysis_mapping_by_query(self, content_id: Optional[str] = None,
                                   primary_summary_id: Optional[str] = None,
                                   primary_insight_id: Optional[str] = None,
                                   primary_implication_id: Optional[str] = None,
                                   selection_strategy: Optional[str] = None,
                                   selection_context: Optional[str] = None,
                                   selected_by: Optional[str] = None,
                                   version: Optional[int] = None,
                                   is_current: Optional[bool] = None,
                                   limit: Optional[int] = None) -> List[ContentAnalysisMappingModel]:
        """Get content analysis mapping entries with optional filters"""
        try:
            # Validate limit
            if limit is not None and limit <= 0:
                raise ValidationException("Limit must be a positive number")
            
            mappings = await self.mapping_repository.get_all_analysis_mapping(
                content_id=content_id.strip() if content_id else None,
                primary_summary_id=primary_summary_id.strip() if primary_summary_id else None,
                primary_insight_id=primary_insight_id.strip() if primary_insight_id else None,
                primary_implication_id=primary_implication_id.strip() if primary_implication_id else None,
                selection_strategy=selection_strategy.strip() if selection_strategy else None,
                selection_context=selection_context.strip() if selection_context else None,
                selected_by=selected_by.strip() if selected_by else None,
                version=version,
                is_current=is_current,
                limit=limit
            )
            
            self.logger.info(f"Retrieved {len(mappings)} content analysis mapping entries with filters: content_id={content_id}, primary_summary_id={primary_summary_id}, primary_insight_id={primary_insight_id}, primary_implication_id={primary_implication_id}, selection_strategy={selection_strategy}, selection_context={selection_context}, selected_by={selected_by}, version={version}, is_current={is_current}")
            return mappings
            
        except ValidationException:
            raise
        except Exception as e:
            self.logger.error(f"Get content analysis mapping entries by query failed: {str(e)}")
            raise
    
    async def update_analysis_mapping(self, mapping_id: str, update_data: Dict[str, Any]) -> ContentAnalysisMappingModel:
        """Update content analysis mapping entry by ID"""
        try:
            if not mapping_id or not mapping_id.strip():
                raise ValidationException("Mapping ID is required")
            
            # Check if mapping exists
            existing_mapping = await self.get_analysis_mapping_by_id(mapping_id)
            
            # Prepare update data (remove None values)
            clean_update_data = {k: v for k, v in update_data.items() if v is not None}
            
            updated_mapping = await self.mapping_repository.update_analysis_mapping(
                mapping_id.strip(), clean_update_data
            )
            
            if not updated_mapping:
                raise ContentAnalysisMappingNotFoundException(f"Failed to update content analysis mapping entry with ID {mapping_id}")
            
            self.logger.info(f"Content analysis mapping entry updated: {mapping_id}")
            return updated_mapping
            
        except (ContentAnalysisMappingNotFoundException, ValidationException):
            raise
        except Exception as e:
            self.logger.error(f"Update content analysis mapping entry failed: {str(e)}")
            raise
