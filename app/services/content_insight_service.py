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
    
    async def create_project(self, url_id: str, content_id: str, insight_text: str, insight_content_file_path: str,
                            insight_category: Optional[str] = None, confidence_score: Optional[float] = None,
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
    
    async def get_project_by_id(self, insight_id: str) -> ContentInsightModel:
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
    
    async def get_projects_by_query(self, url_id: Optional[str] = None,
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
            
            insights = await self.insight_repository.get_all_projects(
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
    
    async def update_project(self, insight_id: str, update_data: Dict[str, Any]) -> ContentInsightModel:
        """Update content insight entry by ID"""
        try:
            if not insight_id or not insight_id.strip():
                raise ValidationException("Insight ID is required")
            
            # Check if insight exists
            existing_insight = await self.get_project_by_id(insight_id)
            
            # Validate confidence_score if being updated
            if "confidence_score" in update_data and update_data["confidence_score"] is not None:
                confidence = update_data["confidence_score"]
                if confidence < 0.0 or confidence > 1.0:
                    raise ValidationException("Confidence score must be between 0.0 and 1.0")
            
            # Prepare update data (remove None values)
            clean_update_data = {k: v for k, v in update_data.items() if v is not None}
            
            updated_insight = await self.insight_repository.update_project(
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
    
    async def mark_as_canonical(self, insight_id: str) -> ContentInsightModel:
        """Mark insight as canonical"""
        try:
            insight = await self.get_project_by_id(insight_id)
            insight.mark_as_canonical()
            
            updated_insight = await self.insight_repository.update_project(
                insight_id, insight.to_dict()
            )
            
            if not updated_insight:
                raise ContentInsightNotFoundException(f"Failed to mark insight as canonical with ID {insight_id}")
            
            self.logger.info(f"Insight marked as canonical: {insight_id}")
            return updated_insight
            
        except (ContentInsightNotFoundException, ValidationException):
            raise
        except Exception as e:
            self.logger.error(f"Mark insight as canonical failed: {str(e)}")
            raise
    
    async def mark_as_preferred(self, insight_id: str) -> ContentInsightModel:
        """Mark insight as preferred choice"""
        try:
            insight = await self.get_project_by_id(insight_id)
            insight.mark_as_preferred()
            
            updated_insight = await self.insight_repository.update_project(
                insight_id, insight.to_dict()
            )
            
            if not updated_insight:
                raise ContentInsightNotFoundException(f"Failed to mark insight as preferred with ID {insight_id}")
            
            self.logger.info(f"Insight marked as preferred: {insight_id}")
            return updated_insight
            
        except (ContentInsightNotFoundException, ValidationException):
            raise
        except Exception as e:
            self.logger.error(f"Mark insight as preferred failed: {str(e)}")
            raise
    
    async def update_confidence_score(self, insight_id: str, score: float) -> ContentInsightModel:
        """Update confidence score for insight"""
        try:
            if score < 0.0 or score > 1.0:
                raise ValidationException("Confidence score must be between 0.0 and 1.0")
            
            insight = await self.get_project_by_id(insight_id)
            insight.update_confidence(score)
            
            updated_insight = await self.insight_repository.update_project(
                insight_id, insight.to_dict()
            )
            
            if not updated_insight:
                raise ContentInsightNotFoundException(f"Failed to update confidence score for insight with ID {insight_id}")
            
            self.logger.info(f"Confidence score updated for insight: {insight_id} to {score}")
            return updated_insight
            
        except (ContentInsightNotFoundException, ValidationException):
            raise
        except Exception as e:
            self.logger.error(f"Update confidence score failed: {str(e)}")
            raise
    
    async def update_category(self, insight_id: str, category: str) -> ContentInsightModel:
        """Update insight category"""
        try:
            if not category or not category.strip():
                raise ValidationException("Category is required")
            
            insight = await self.get_project_by_id(insight_id)
            insight.update_category(category.strip())
            
            updated_insight = await self.insight_repository.update_project(
                insight_id, insight.to_dict()
            )
            
            if not updated_insight:
                raise ContentInsightNotFoundException(f"Failed to update category for insight with ID {insight_id}")
            
            self.logger.info(f"Category updated for insight: {insight_id} to {category}")
            return updated_insight
            
        except (ContentInsightNotFoundException, ValidationException):
            raise
        except Exception as e:
            self.logger.error(f"Update category failed: {str(e)}")
            raise
    
    async def get_insights_by_content(self, content_id: str, insight_category: Optional[str] = None,
                                     is_canonical: Optional[bool] = None) -> List[ContentInsightModel]:
        """Get all insights for a specific content ID"""
        try:
            if not content_id or not content_id.strip():
                raise ValidationException("Content ID is required")
            
            insights = await self.insight_repository.get_all_projects(
                content_id=content_id.strip(),
                insight_category=insight_category.strip() if insight_category else None,
                is_canonical=is_canonical
            )
            
            self.logger.info(f"Retrieved {len(insights)} insights for content {content_id}")
            return insights
            
        except ValidationException:
            raise
        except Exception as e:
            self.logger.error(f"Get insights by content failed: {str(e)}")
            raise
    
    async def get_insights_by_url(self, url_id: str, preferred_choice: Optional[bool] = None) -> List[ContentInsightModel]:
        """Get all insights for a specific URL ID"""
        try:
            if not url_id or not url_id.strip():
                raise ValidationException("URL ID is required")
            
            insights = await self.insight_repository.get_all_projects(
                url_id=url_id.strip(),
                preferred_choice=preferred_choice
            )
            
            self.logger.info(f"Retrieved {len(insights)} insights for URL {url_id}")
            return insights
            
        except ValidationException:
            raise
        except Exception as e:
            self.logger.error(f"Get insights by URL failed: {str(e)}")
            raise
    
    async def get_insights_by_category(self, insight_category: str, content_id: Optional[str] = None) -> List[ContentInsightModel]:
        """Get all insights for a specific category"""
        try:
            if not insight_category or not insight_category.strip():
                raise ValidationException("Insight category is required")
            
            insights = await self.insight_repository.get_all_projects(
                insight_category=insight_category.strip(),
                content_id=content_id.strip() if content_id else None
            )
            
            self.logger.info(f"Retrieved {len(insights)} insights for category {insight_category}")
            return insights
            
        except ValidationException:
            raise
        except Exception as e:
            self.logger.error(f"Get insights by category failed: {str(e)}")
            raise
    
    async def get_preferred_insights(self, content_id: Optional[str] = None) -> List[ContentInsightModel]:
        """Get all preferred insights, optionally filtered by content ID"""
        try:
            insights = await self.insight_repository.get_all_projects(
                content_id=content_id.strip() if content_id else None,
                preferred_choice=True
            )
            
            self.logger.info(f"Retrieved {len(insights)} preferred insights")
            return insights
            
        except Exception as e:
            self.logger.error(f"Get preferred insights failed: {str(e)}")
            raise 