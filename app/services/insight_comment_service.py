"""
Insight Comment Service - Works with InsightCommentModel and InsightCommentRepository
Follows the same pattern as ProjectService for consistency
"""

from typing import List, Optional, Dict, Any
from app.repositories.insight_comment_repository import InsightCommentRepository
from app.models.insight_comment_model import InsightCommentModel
from app.core.logging import get_logger
from app.core.exceptions import (
    ValidationException
)

logger = get_logger("insight_comment_service")

class InsightCommentNotFoundException(Exception):
    """Exception raised when insight comment entry is not found"""
    pass

class InsightCommentAlreadyExistsException(Exception):
    """Exception raised when insight comment entry already exists"""
    pass

class InsightCommentService:
    """Insight comment service with essential operations"""
    
    def __init__(self):
        self.comment_repository = InsightCommentRepository()
        self.logger = logger
    
    async def create_insight_comment(self, insight_id: str, comment_text: str, comment_type: Optional[str] = None) -> InsightCommentModel:
        """Create a new insight comment entry"""
        try:
            # Validate required fields
            if not insight_id or not insight_id.strip():
                raise ValidationException("Insight ID is required")
            
            if not comment_text or not comment_text.strip():
                raise ValidationException("Comment text is required")
            
            # Create comment model
            comment_model = InsightCommentModel.create_new(
                insight_id=insight_id.strip(),
                comment_text=comment_text.strip(),
                comment_type=comment_type.strip() if comment_type else None
            )
            
            # Save to database
            created_comment = await self.comment_repository.create(comment_model)
            self.logger.info(f"Insight comment entry created for insight {insight_id}")
            return created_comment
            
        except ValidationException:
            raise
        except Exception as e:
            self.logger.error(f"Create insight comment entry failed: {str(e)}")
            raise
    
    async def get_insight_comment_by_id(self, comment_id: str) -> InsightCommentModel:
        """Get insight comment entry by ID"""
        try:
            if not comment_id or not comment_id.strip():
                raise ValidationException("Comment ID is required")
            
            comment = await self.comment_repository.find_one_by_query({"pk": comment_id.strip()})
            if not comment:
                raise InsightCommentNotFoundException(f"Insight comment entry with ID {comment_id} not found")
            
            return comment
            
        except (InsightCommentNotFoundException, ValidationException):
            raise
        except Exception as e:
            self.logger.error(f"Get insight comment entry by ID failed: {str(e)}")
            raise
    
    async def get_all_insight_comment(self, insight_id: Optional[str] = None,
                                   comment_type: Optional[str] = None,
                                   limit: Optional[int] = None) -> List[InsightCommentModel]:
        """Get insight comment entries with optional filters"""
        try:
            # Validate limit
            if limit is not None and limit <= 0:
                raise ValidationException("Limit must be a positive number")
            
            comments = await self.comment_repository.get_all_insight_comment(
                insight_id=insight_id.strip() if insight_id else None,
                comment_type=comment_type.strip() if comment_type else None,
                limit=limit
            )
            
            self.logger.info(f"Retrieved {len(comments)} insight comment entries with filters: insight_id={insight_id}, comment_type={comment_type}")
            return comments
            
        except ValidationException:
            raise
        except Exception as e:
            self.logger.error(f"Get insight comment entries by query failed: {str(e)}")
            raise
    
    async def update_insight_comment(self, comment_id: str, update_data: Dict[str, Any]) -> InsightCommentModel:
        """Update insight comment entry by ID"""
        try:
            if not comment_id or not comment_id.strip():
                raise ValidationException("Comment ID is required")
            
            # Check if comment exists
            existing_comment = await self.get_insight_comment_by_id(comment_id)
            
            # Prepare update data (remove None values and add updated_at)
            clean_update_data = {k: v for k, v in update_data.items() if v is not None}
            if clean_update_data:
                from datetime import datetime
                clean_update_data["updated_at"] = datetime.utcnow().isoformat()
            
            updated_comment = await self.comment_repository.update_insight_comment(
                comment_id.strip(), clean_update_data
            )
            
            if not updated_comment:
                raise InsightCommentNotFoundException(f"Failed to update insight comment entry with ID {comment_id}")
            
            self.logger.info(f"Insight comment entry updated: {comment_id}")
            return updated_comment
            
        except (InsightCommentNotFoundException, ValidationException):
            raise
        except Exception as e:
            self.logger.error(f"Update insight comment entry failed: {str(e)}")
            raise
    
    async def get_all_by_query(self, query_filters: Optional[Dict[str, Any]] = None, limit: Optional[int] = None) -> List[InsightCommentModel]:
        """Get all insight comment entries by query filters"""
        try:
            # Validate limit if provided
            if limit is not None and limit <= 0:
                raise ValidationException("Limit must be greater than 0")
            
            # Get entries from repository
            entries = await self.comment_repository.find_all_by_query(query=query_filters, limit=limit)
            
            # Convert to model objects - check if entries are already model objects or dicts
            comment_models = []
            for entry in entries:
                if isinstance(entry, InsightCommentModel):
                    comment_models.append(entry)
                else:
                    comment_models.append(InsightCommentModel.from_dict(entry))
            
            self.logger.info(f"Retrieved {len(comment_models)} insight comment entries with filters: {query_filters}")
            return comment_models
            
        except ValidationException:
            raise
        except Exception as e:
            self.logger.error(f"Get insight comment entries by query failed: {str(e)}")
            raise
    
