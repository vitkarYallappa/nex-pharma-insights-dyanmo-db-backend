"""
Content Insight Service - Works with ContentInsightModel and ContentInsightRepository
Follows the same pattern as ProjectService for consistency
"""

from typing import List, Optional, Dict, Any
from app.repositories.content_insight_repository import ContentInsightRepository
from app.models.content_insight_model import ContentInsightModel
from app.core.logging import get_logger
from app.core.exceptions import (
    ValidationException
)

logger = get_logger("content_insight_service")

class ContentInsightNotFoundException(Exception):
    """Exception raised when content insight entry is not found"""
    pass

class ContentInsightAlreadyExistsException(Exception):
    """Exception raised when content insight entry already exists"""
    pass

class ContentInsightService:
    """Content insight service with essential operations"""
    
    def __init__(self):
        self.insight_repository = ContentInsightRepository()
        self.logger = logger
    
    async def create_content_insight(self, url_id: str, content_id: str, insight_text: str, insight_content_file_path: str,
                            insight_category: Optional[str] = None, confidence_score: Optional[str] = None,
                            version: Optional[int] = None, is_canonical: Optional[bool] = None,
                            preferred_choice: Optional[bool] = None, created_by: Optional[str] = None) -> ContentInsightModel:
        """Create a new content insight entry"""
        try:
            # Validate required fields
            if not url_id or not url_id.strip():
                raise ValidationException("URL ID is required")
            
            if not content_id or not content_id.strip():
                raise ValidationException("Content ID is required")
            
            if not insight_text or not insight_text.strip():
                raise ValidationException("Insight text is required")
            
            if not insight_content_file_path or not insight_content_file_path.strip():
                raise ValidationException("Insight content file path is required")
            
            # Validate confidence_score range if provided
            if confidence_score is not None and (confidence_score < 0.0 or confidence_score > 1.0):
                raise ValidationException("Confidence score must be between 0.0 and 1.0")
            
            # Create insight model
            insight_model = ContentInsightModel.create_new(
                url_id=url_id.strip(),
                content_id=content_id.strip(),
                insight_text=insight_text.strip(),
                insight_content_file_path=insight_content_file_path.strip(),
                insight_category=insight_category.strip() if insight_category else None,
                confidence_score=confidence_score,
                version=version,
                is_canonical=is_canonical,
                preferred_choice=preferred_choice,
                created_by=created_by.strip() if created_by else None
            )
            
            # Save to database
            created_insight = await self.insight_repository.create(insight_model)
            self.logger.info(f"Content insight entry created for content {content_id} and URL {url_id}")
            return created_insight
            
        except ValidationException:
            raise
        except Exception as e:
            self.logger.error(f"Create content insight entry failed: {str(e)}")
            raise
    
    async def get_content_insight_by_id(self, insight_id: str) -> ContentInsightModel:
        """Get content insight entry by ID"""
        try:
            if not insight_id or not insight_id.strip():
                raise ValidationException("Insight ID is required")
            
            insight = await self.insight_repository.find_one_by_query({"pk": insight_id.strip()})
            if not insight:
                raise ContentInsightNotFoundException(f"Content insight entry with ID {insight_id} not found")
            
            return insight
            
        except (ContentInsightNotFoundException, ValidationException):
            raise
        except Exception as e:
            self.logger.error(f"Get content insight entry by ID failed: {str(e)}")
            raise
    
    async def get_content_insight_by_query(self, url_id: Optional[str] = None,
                                   content_id: Optional[str] = None,
                                   insight_category: Optional[str] = None,
                                   is_canonical: Optional[bool] = None,
                                   preferred_choice: Optional[bool] = None,
                                   version: Optional[int] = None,
                                   created_by: Optional[str] = None,
                                   limit: Optional[int] = None) -> List[ContentInsightModel]:
        """Get content insight entries with optional filters"""
        try:
            # Validate limit
            if limit is not None and limit <= 0:
                raise ValidationException("Limit must be a positive number")
            
            insights = await self.insight_repository.get_all_content_insight(
                url_id=url_id.strip() if url_id else None,
                content_id=content_id.strip() if content_id else None,
                insight_category=insight_category.strip() if insight_category else None,
                is_canonical=is_canonical,
                preferred_choice=preferred_choice,
                version=version,
                created_by=created_by.strip() if created_by else None,
                limit=limit
            )
            
            self.logger.info(f"Retrieved {len(insights)} content insight entries with filters: url_id={url_id}, content_id={content_id}, insight_category={insight_category}, is_canonical={is_canonical}, preferred_choice={preferred_choice}, version={version}, created_by={created_by}")
            return insights
            
        except ValidationException:
            raise
        except Exception as e:
            self.logger.error(f"Get content insight entries by query failed: {str(e)}")
            raise
    
    async def update_content_insight(self, insight_id: str, update_data: Dict[str, Any]) -> ContentInsightModel:
        """Update content insight entry by ID"""
        try:
            if not insight_id or not insight_id.strip():
                raise ValidationException("Insight ID is required")
            
            # Check if insight exists
            existing_insight = await self.get_content_insight_by_id(insight_id)
            
            # Validate confidence_score if being updated
            if "confidence_score" in update_data and update_data["confidence_score"] is not None:
                confidence = update_data["confidence_score"]
                if confidence < 0.0 or confidence > 1.0:
                    raise ValidationException("Confidence score must be between 0.0 and 1.0")
            
            # Prepare update data (remove None values)
            clean_update_data = {k: v for k, v in update_data.items() if v is not None}
            
            updated_insight = await self.insight_repository.update_content_insight(
                insight_id.strip(), clean_update_data
            )
            
            if not updated_insight:
                raise ContentInsightNotFoundException(f"Failed to update content insight entry with ID {insight_id}")
            
            self.logger.info(f"Content insight entry updated: {insight_id}")
            return updated_insight
            
        except (ContentInsightNotFoundException, ValidationException):
            raise
        except Exception as e:
            self.logger.error(f"Update content insight entry failed: {str(e)}")
            raise
    
    async def get_all_by_query(self, query_filters: Optional[Dict[str, Any]] = None, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get all content insight entries by query filters
        
        Returns:
            List[Dict[str, Any]]: All returned dictionaries will have 'status' field set to 'saved' by default
        """
        try:
            # Validate limit if provided
            if limit is not None and limit <= 0:
                raise ValidationException("Limit must be greater than 0")
            
            # Get entries from repository
            entries = await self.insight_repository.find_all_by_query(query=query_filters, limit=limit)
            
            # Convert to dictionaries with status field - check if entries are already model objects or dicts
            insight_dicts = []
            for entry in entries:
                if isinstance(entry, ContentInsightModel):
                    # Convert model to dict and ensure status field is present
                    entry_dict = entry.to_dict()
                    entry_dict['status'] = 'saved'
                    insight_dicts.append(entry_dict)
                else:
                    # Always ensure status field is present with default value
                    entry['status'] = 'saved'
                    insight_dicts.append(entry)
            
            self.logger.info(f"Retrieved {len(insight_dicts)} content insight entries with filters: {query_filters}")
            return insight_dicts
            
        except ValidationException:
            raise
        except Exception as e:
            self.logger.error(f"Get content insight entries by query failed: {str(e)}")
            raise
    
