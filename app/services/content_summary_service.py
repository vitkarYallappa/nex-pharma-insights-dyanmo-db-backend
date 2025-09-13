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
    
    async def create_content_summary(self, url_id: str, content_id: str, summary_text: str, summary_content_file_path: str,
                            confidence_score: Optional[str] = None, version: Optional[int] = None,
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
    
    async def get_content_summary_by_id(self, summary_id: str) -> ContentSummaryModel:
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
            
            summaries = await self.summary_repository.get_all_content_summary(
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
    
    async def update_content_summary(self, summary_id: str, update_data: Dict[str, Any]) -> ContentSummaryModel:
        """Update content summary entry by ID"""
        try:
            if not summary_id or not summary_id.strip():
                raise ValidationException("Summary ID is required")
            
            # Check if summary exists
            existing_summary = await self.get_content_summary_by_id(summary_id)
            
            # Validate confidence_score if being updated
            if "confidence_score" in update_data and update_data["confidence_score"] is not None:
                confidence = update_data["confidence_score"]
                if confidence < 0.0 or confidence > 1.0:
                    raise ValidationException("Confidence score must be between 0.0 and 1.0")
            
            # Prepare update data (remove None values)
            clean_update_data = {k: v for k, v in update_data.items() if v is not None}
            
            updated_summary = await self.summary_repository.update_content_summary(
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
    
    async def get_all_by_query(self, query_filters: Optional[Dict[str, Any]] = None, limit: Optional[int] = None) -> List[ContentSummaryModel]:
        """Get all content summary entries by query filters"""
        try:
            # Validate limit if provided
            if limit is not None and limit <= 0:
                raise ValidationException("Limit must be greater than 0")
            
            # Get entries from repository
            entries = await self.summary_repository.find_all_by_query(query=query_filters, limit=limit)
            
            # Convert to model objects - check if entries are already model objects or dicts
            summary_models = []
            for entry in entries:
                if isinstance(entry, ContentSummaryModel):
                    summary_models.append(entry)
                else:
                    summary_models.append(ContentSummaryModel.from_dict(entry))
            
            self.logger.info(f"Retrieved {len(summary_models)} content summary entries with filters: {query_filters}")
            return summary_models
            
        except ValidationException:
            raise
        except Exception as e:
            self.logger.error(f"Get content summary entries by query failed: {str(e)}")
            raise
