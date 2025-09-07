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
    
    async def create_project(self, content_id: str, primary_summary_id: Optional[str] = None,
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
    
    async def get_project_by_id(self, mapping_id: str) -> ContentAnalysisMappingModel:
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
    
    async def get_projects_by_query(self, content_id: Optional[str] = None,
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
            
            mappings = await self.mapping_repository.get_all_projects(
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
    
    async def update_project(self, mapping_id: str, update_data: Dict[str, Any]) -> ContentAnalysisMappingModel:
        """Update content analysis mapping entry by ID"""
        try:
            if not mapping_id or not mapping_id.strip():
                raise ValidationException("Mapping ID is required")
            
            # Check if mapping exists
            existing_mapping = await self.get_project_by_id(mapping_id)
            
            # Prepare update data (remove None values)
            clean_update_data = {k: v for k, v in update_data.items() if v is not None}
            
            updated_mapping = await self.mapping_repository.update_project(
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
    
    async def get_mapping_by_content(self, content_id: str, is_current: Optional[bool] = None) -> Optional[ContentAnalysisMappingModel]:
        """Get content analysis mapping by content ID"""
        try:
            if not content_id or not content_id.strip():
                raise ValidationException("Content ID is required")
            
            mappings = await self.mapping_repository.get_all_projects(
                content_id=content_id.strip(),
                is_current=is_current,
                limit=1
            )
            
            return mappings[0] if mappings else None
            
        except ValidationException:
            raise
        except Exception as e:
            self.logger.error(f"Get mapping by content failed: {str(e)}")
            raise
    
    async def get_current_mapping_by_content(self, content_id: str) -> Optional[ContentAnalysisMappingModel]:
        """Get current content analysis mapping by content ID"""
        return await self.get_mapping_by_content(content_id, is_current=True)
    
    async def mark_as_current(self, mapping_id: str) -> ContentAnalysisMappingModel:
        """Mark mapping as current"""
        try:
            mapping = await self.get_project_by_id(mapping_id)
            mapping.mark_as_current()
            
            updated_mapping = await self.mapping_repository.update_project(
                mapping_id, mapping.to_dict()
            )
            
            if not updated_mapping:
                raise ContentAnalysisMappingNotFoundException(f"Failed to mark mapping as current with ID {mapping_id}")
            
            self.logger.info(f"Mapping marked as current: {mapping_id}")
            return updated_mapping
            
        except (ContentAnalysisMappingNotFoundException, ValidationException):
            raise
        except Exception as e:
            self.logger.error(f"Mark mapping as current failed: {str(e)}")
            raise
    
    async def mark_as_outdated(self, mapping_id: str) -> ContentAnalysisMappingModel:
        """Mark mapping as outdated"""
        try:
            mapping = await self.get_project_by_id(mapping_id)
            mapping.mark_as_outdated()
            
            updated_mapping = await self.mapping_repository.update_project(
                mapping_id, mapping.to_dict()
            )
            
            if not updated_mapping:
                raise ContentAnalysisMappingNotFoundException(f"Failed to mark mapping as outdated with ID {mapping_id}")
            
            self.logger.info(f"Mapping marked as outdated: {mapping_id}")
            return updated_mapping
            
        except (ContentAnalysisMappingNotFoundException, ValidationException):
            raise
        except Exception as e:
            self.logger.error(f"Mark mapping as outdated failed: {str(e)}")
            raise
    
    async def update_primary_summary(self, mapping_id: str, summary_id: str, strategy: Optional[str] = None,
                                    context: Optional[str] = None, selected_by: Optional[str] = None) -> ContentAnalysisMappingModel:
        """Update primary summary selection"""
        try:
            if not summary_id or not summary_id.strip():
                raise ValidationException("Summary ID is required")
            
            mapping = await self.get_project_by_id(mapping_id)
            mapping.update_primary_summary(
                summary_id.strip(),
                strategy.strip() if strategy else None,
                context.strip() if context else None,
                selected_by.strip() if selected_by else None
            )
            
            updated_mapping = await self.mapping_repository.update_project(
                mapping_id, mapping.to_dict()
            )
            
            if not updated_mapping:
                raise ContentAnalysisMappingNotFoundException(f"Failed to update primary summary for mapping with ID {mapping_id}")
            
            self.logger.info(f"Primary summary updated for mapping: {mapping_id} to {summary_id}")
            return updated_mapping
            
        except (ContentAnalysisMappingNotFoundException, ValidationException):
            raise
        except Exception as e:
            self.logger.error(f"Update primary summary failed: {str(e)}")
            raise
    
    async def update_primary_insight(self, mapping_id: str, insight_id: str, strategy: Optional[str] = None,
                                    context: Optional[str] = None, selected_by: Optional[str] = None) -> ContentAnalysisMappingModel:
        """Update primary insight selection"""
        try:
            if not insight_id or not insight_id.strip():
                raise ValidationException("Insight ID is required")
            
            mapping = await self.get_project_by_id(mapping_id)
            mapping.update_primary_insight(
                insight_id.strip(),
                strategy.strip() if strategy else None,
                context.strip() if context else None,
                selected_by.strip() if selected_by else None
            )
            
            updated_mapping = await self.mapping_repository.update_project(
                mapping_id, mapping.to_dict()
            )
            
            if not updated_mapping:
                raise ContentAnalysisMappingNotFoundException(f"Failed to update primary insight for mapping with ID {mapping_id}")
            
            self.logger.info(f"Primary insight updated for mapping: {mapping_id} to {insight_id}")
            return updated_mapping
            
        except (ContentAnalysisMappingNotFoundException, ValidationException):
            raise
        except Exception as e:
            self.logger.error(f"Update primary insight failed: {str(e)}")
            raise
    
    async def update_primary_implication(self, mapping_id: str, implication_id: str, strategy: Optional[str] = None,
                                        context: Optional[str] = None, selected_by: Optional[str] = None) -> ContentAnalysisMappingModel:
        """Update primary implication selection"""
        try:
            if not implication_id or not implication_id.strip():
                raise ValidationException("Implication ID is required")
            
            mapping = await self.get_project_by_id(mapping_id)
            mapping.update_primary_implication(
                implication_id.strip(),
                strategy.strip() if strategy else None,
                context.strip() if context else None,
                selected_by.strip() if selected_by else None
            )
            
            updated_mapping = await self.mapping_repository.update_project(
                mapping_id, mapping.to_dict()
            )
            
            if not updated_mapping:
                raise ContentAnalysisMappingNotFoundException(f"Failed to update primary implication for mapping with ID {mapping_id}")
            
            self.logger.info(f"Primary implication updated for mapping: {mapping_id} to {implication_id}")
            return updated_mapping
            
        except (ContentAnalysisMappingNotFoundException, ValidationException):
            raise
        except Exception as e:
            self.logger.error(f"Update primary implication failed: {str(e)}")
            raise
    
    async def get_mappings_by_strategy(self, selection_strategy: str, is_current: Optional[bool] = None) -> List[ContentAnalysisMappingModel]:
        """Get all mappings for a specific selection strategy"""
        try:
            if not selection_strategy or not selection_strategy.strip():
                raise ValidationException("Selection strategy is required")
            
            mappings = await self.mapping_repository.get_all_projects(
                selection_strategy=selection_strategy.strip(),
                is_current=is_current
            )
            
            self.logger.info(f"Retrieved {len(mappings)} mappings for strategy {selection_strategy}")
            return mappings
            
        except ValidationException:
            raise
        except Exception as e:
            self.logger.error(f"Get mappings by strategy failed: {str(e)}")
            raise
    
    async def get_current_mappings(self) -> List[ContentAnalysisMappingModel]:
        """Get all current mappings"""
        try:
            mappings = await self.mapping_repository.get_all_projects(is_current=True)
            
            self.logger.info(f"Retrieved {len(mappings)} current mappings")
            return mappings
            
        except Exception as e:
            self.logger.error(f"Get current mappings failed: {str(e)}")
            raise 