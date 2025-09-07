"""
Content Summary Service - Works with ContentSummaryModel and ContentSummaryRepository
Follows the same pattern as ProjectService for consistency
"""

from typing import List, Optional, Dict, Any
from app.repositories.content_summary_repository import ContentSummaryRepository
from app.models.content_summary_model import ContentSummaryModel
from app.core.logging import get_logger
from app.core.exceptions import (
    ValidationException
)

logger = get_logger("content_summary_service")

class ContentSummaryNotFoundException(Exception):
    """Exception raised when content summary entry is not found"""
    pass

class ContentSummaryAlreadyExistsException(Exception):
    """Exception raised when content summary entry already exists"""
    pass

class ContentSummaryService:
    """Content summary service with essential operations"""
    
    def __init__(self):
        self.summary_repository = ContentSummaryRepository()
        self.logger = logger
    
    async def create_project(self, url_id: str, content_id: str, summary_text: str, summary_content_file_path: str,
                            confidence_score: Optional[float] = None, version: Optional[int] = None,
                            is_canonical: Optional[bool] = None, preferred_choice: Optional[bool] = None,
                            created_by: Optional[str] = None) -> ContentSummaryModel:
        """Create a new content summary entry"""
        try:
            # Validate required fields
            if not url_id or not url_id.strip():
                raise ValidationException("URL ID is required")
            
            if not content_id or not content_id.strip():
                raise ValidationException("Content ID is required")
            
            if not summary_text or not summary_text.strip():
                raise ValidationException("Summary text is required")
            
            if not summary_content_file_path or not summary_content_file_path.strip():
                raise ValidationException("Summary content file path is required")
            
            # Validate confidence_score range if provided
            if confidence_score is not None and (confidence_score < 0.0 or confidence_score > 1.0):
                raise ValidationException("Confidence score must be between 0.0 and 1.0")
            
            # Create summary model
            summary_model = ContentSummaryModel.create_new(
                url_id=url_id.strip(),
                content_id=content_id.strip(),
                summary_text=summary_text.strip(),
                summary_content_file_path=summary_content_file_path.strip(),
                confidence_score=confidence_score,
                version=version,
                is_canonical=is_canonical,
                preferred_choice=preferred_choice,
                created_by=created_by.strip() if created_by else None
            )
            
            # Save to database
            created_summary = await self.summary_repository.create(summary_model)
            self.logger.info(f"Content summary entry created for content {content_id} and URL {url_id}")
            return created_summary
            
        except ValidationException:
            raise
        except Exception as e:
            self.logger.error(f"Create content summary entry failed: {str(e)}")
            raise
    
    async def get_project_by_id(self, summary_id: str) -> ContentSummaryModel:
        """Get content summary entry by ID"""
        try:
            if not summary_id or not summary_id.strip():
                raise ValidationException("Summary ID is required")
            
            summary = await self.summary_repository.find_one_by_query({"pk": summary_id.strip()})
            if not summary:
                raise ContentSummaryNotFoundException(f"Content summary entry with ID {summary_id} not found")
            
            return summary
            
        except (ContentSummaryNotFoundException, ValidationException):
            raise
        except Exception as e:
            self.logger.error(f"Get content summary entry by ID failed: {str(e)}")
            raise
    
    async def get_projects_by_query(self, url_id: Optional[str] = None,
                                   content_id: Optional[str] = None,
                                   is_canonical: Optional[bool] = None,
                                   preferred_choice: Optional[bool] = None,
                                   version: Optional[int] = None,
                                   created_by: Optional[str] = None,
                                   limit: Optional[int] = None) -> List[ContentSummaryModel]:
        """Get content summary entries with optional filters"""
        try:
            # Validate limit
            if limit is not None and limit <= 0:
                raise ValidationException("Limit must be a positive number")
            
            summaries = await self.summary_repository.get_all_projects(
                url_id=url_id.strip() if url_id else None,
                content_id=content_id.strip() if content_id else None,
                is_canonical=is_canonical,
                preferred_choice=preferred_choice,
                version=version,
                created_by=created_by.strip() if created_by else None,
                limit=limit
            )
            
            self.logger.info(f"Retrieved {len(summaries)} content summary entries with filters: url_id={url_id}, content_id={content_id}, is_canonical={is_canonical}, preferred_choice={preferred_choice}, version={version}, created_by={created_by}")
            return summaries
            
        except ValidationException:
            raise
        except Exception as e:
            self.logger.error(f"Get content summary entries by query failed: {str(e)}")
            raise
    
    async def update_project(self, summary_id: str, update_data: Dict[str, Any]) -> ContentSummaryModel:
        """Update content summary entry by ID"""
        try:
            if not summary_id or not summary_id.strip():
                raise ValidationException("Summary ID is required")
            
            # Check if summary exists
            existing_summary = await self.get_project_by_id(summary_id)
            
            # Validate confidence_score if being updated
            if "confidence_score" in update_data and update_data["confidence_score"] is not None:
                confidence = update_data["confidence_score"]
                if confidence < 0.0 or confidence > 1.0:
                    raise ValidationException("Confidence score must be between 0.0 and 1.0")
            
            # Prepare update data (remove None values)
            clean_update_data = {k: v for k, v in update_data.items() if v is not None}
            
            updated_summary = await self.summary_repository.update_project(
                summary_id.strip(), clean_update_data
            )
            
            if not updated_summary:
                raise ContentSummaryNotFoundException(f"Failed to update content summary entry with ID {summary_id}")
            
            self.logger.info(f"Content summary entry updated: {summary_id}")
            return updated_summary
            
        except (ContentSummaryNotFoundException, ValidationException):
            raise
        except Exception as e:
            self.logger.error(f"Update content summary entry failed: {str(e)}")
            raise
    
    async def mark_as_canonical(self, summary_id: str) -> ContentSummaryModel:
        """Mark summary as canonical"""
        try:
            summary = await self.get_project_by_id(summary_id)
            summary.mark_as_canonical()
            
            updated_summary = await self.summary_repository.update_project(
                summary_id, summary.to_dict()
            )
            
            if not updated_summary:
                raise ContentSummaryNotFoundException(f"Failed to mark summary as canonical with ID {summary_id}")
            
            self.logger.info(f"Summary marked as canonical: {summary_id}")
            return updated_summary
            
        except (ContentSummaryNotFoundException, ValidationException):
            raise
        except Exception as e:
            self.logger.error(f"Mark summary as canonical failed: {str(e)}")
            raise
    
    async def mark_as_preferred(self, summary_id: str) -> ContentSummaryModel:
        """Mark summary as preferred choice"""
        try:
            summary = await self.get_project_by_id(summary_id)
            summary.mark_as_preferred()
            
            updated_summary = await self.summary_repository.update_project(
                summary_id, summary.to_dict()
            )
            
            if not updated_summary:
                raise ContentSummaryNotFoundException(f"Failed to mark summary as preferred with ID {summary_id}")
            
            self.logger.info(f"Summary marked as preferred: {summary_id}")
            return updated_summary
            
        except (ContentSummaryNotFoundException, ValidationException):
            raise
        except Exception as e:
            self.logger.error(f"Mark summary as preferred failed: {str(e)}")
            raise
    
    async def update_confidence_score(self, summary_id: str, score: float) -> ContentSummaryModel:
        """Update confidence score for summary"""
        try:
            if score < 0.0 or score > 1.0:
                raise ValidationException("Confidence score must be between 0.0 and 1.0")
            
            summary = await self.get_project_by_id(summary_id)
            summary.update_confidence(score)
            
            updated_summary = await self.summary_repository.update_project(
                summary_id, summary.to_dict()
            )
            
            if not updated_summary:
                raise ContentSummaryNotFoundException(f"Failed to update confidence score for summary with ID {summary_id}")
            
            self.logger.info(f"Confidence score updated for summary: {summary_id} to {score}")
            return updated_summary
            
        except (ContentSummaryNotFoundException, ValidationException):
            raise
        except Exception as e:
            self.logger.error(f"Update confidence score failed: {str(e)}")
            raise
    
    async def get_summaries_by_content(self, content_id: str, is_canonical: Optional[bool] = None) -> List[ContentSummaryModel]:
        """Get all summaries for a specific content ID"""
        try:
            if not content_id or not content_id.strip():
                raise ValidationException("Content ID is required")
            
            summaries = await self.summary_repository.get_all_projects(
                content_id=content_id.strip(),
                is_canonical=is_canonical
            )
            
            self.logger.info(f"Retrieved {len(summaries)} summaries for content {content_id}")
            return summaries
            
        except ValidationException:
            raise
        except Exception as e:
            self.logger.error(f"Get summaries by content failed: {str(e)}")
            raise
    
    async def get_summaries_by_url(self, url_id: str, preferred_choice: Optional[bool] = None) -> List[ContentSummaryModel]:
        """Get all summaries for a specific URL ID"""
        try:
            if not url_id or not url_id.strip():
                raise ValidationException("URL ID is required")
            
            summaries = await self.summary_repository.get_all_projects(
                url_id=url_id.strip(),
                preferred_choice=preferred_choice
            )
            
            self.logger.info(f"Retrieved {len(summaries)} summaries for URL {url_id}")
            return summaries
            
        except ValidationException:
            raise
        except Exception as e:
            self.logger.error(f"Get summaries by URL failed: {str(e)}")
            raise
    
    async def get_preferred_summaries(self, content_id: Optional[str] = None) -> List[ContentSummaryModel]:
        """Get all preferred summaries, optionally filtered by content ID"""
        try:
            summaries = await self.summary_repository.get_all_projects(
                content_id=content_id.strip() if content_id else None,
                preferred_choice=True
            )
            
            self.logger.info(f"Retrieved {len(summaries)} preferred summaries")
            return summaries
            
        except Exception as e:
            self.logger.error(f"Get preferred summaries failed: {str(e)}")
            raise 