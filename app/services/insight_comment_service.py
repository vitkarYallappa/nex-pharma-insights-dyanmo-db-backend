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
    
    async def create_project(self, insight_id: str, comment_text: str, comment_type: Optional[str] = None) -> InsightCommentModel:
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
    
    async def get_project_by_id(self, comment_id: str) -> InsightCommentModel:
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
    
    async def get_projects_by_query(self, insight_id: Optional[str] = None,
                                   comment_type: Optional[str] = None,
                                   limit: Optional[int] = None) -> List[InsightCommentModel]:
        """Get insight comment entries with optional filters"""
        try:
            # Validate limit
            if limit is not None and limit <= 0:
                raise ValidationException("Limit must be a positive number")
            
            comments = await self.comment_repository.get_all_projects(
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
    
    async def update_project(self, comment_id: str, update_data: Dict[str, Any]) -> InsightCommentModel:
        """Update insight comment entry by ID"""
        try:
            if not comment_id or not comment_id.strip():
                raise ValidationException("Comment ID is required")
            
            # Check if comment exists
            existing_comment = await self.get_project_by_id(comment_id)
            
            # Prepare update data (remove None values and add updated_at)
            clean_update_data = {k: v for k, v in update_data.items() if v is not None}
            if clean_update_data:
                from datetime import datetime
                clean_update_data["updated_at"] = datetime.utcnow().isoformat()
            
            updated_comment = await self.comment_repository.update_project(
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
    
    async def get_comments_by_insight(self, insight_id: str, comment_type: Optional[str] = None) -> List[InsightCommentModel]:
        """Get all comments for a specific insight ID"""
        try:
            if not insight_id or not insight_id.strip():
                raise ValidationException("Insight ID is required")
            
            comments = await self.comment_repository.get_all_projects(
                insight_id=insight_id.strip(),
                comment_type=comment_type.strip() if comment_type else None
            )
            
            self.logger.info(f"Retrieved {len(comments)} comments for insight {insight_id}")
            return comments
            
        except ValidationException:
            raise
        except Exception as e:
            self.logger.error(f"Get comments by insight failed: {str(e)}")
            raise
    
    async def get_comments_by_type(self, comment_type: str, insight_id: Optional[str] = None) -> List[InsightCommentModel]:
        """Get all comments for a specific type"""
        try:
            if not comment_type or not comment_type.strip():
                raise ValidationException("Comment type is required")
            
            comments = await self.comment_repository.get_all_projects(
                comment_type=comment_type.strip(),
                insight_id=insight_id.strip() if insight_id else None
            )
            
            self.logger.info(f"Retrieved {len(comments)} comments for type {comment_type}")
            return comments
            
        except ValidationException:
            raise
        except Exception as e:
            self.logger.error(f"Get comments by type failed: {str(e)}")
            raise
    
    async def update_comment_text(self, comment_id: str, comment_text: str) -> InsightCommentModel:
        """Update comment text"""
        try:
            if not comment_text or not comment_text.strip():
                raise ValidationException("Comment text is required")
            
            comment = await self.get_project_by_id(comment_id)
            comment.update_comment_text(comment_text.strip())
            
            updated_comment = await self.comment_repository.update_project(
                comment_id, comment.to_dict()
            )
            
            if not updated_comment:
                raise InsightCommentNotFoundException(f"Failed to update comment text for comment with ID {comment_id}")
            
            self.logger.info(f"Comment text updated for comment: {comment_id}")
            return updated_comment
            
        except (InsightCommentNotFoundException, ValidationException):
            raise
        except Exception as e:
            self.logger.error(f"Update comment text failed: {str(e)}")
            raise
    
    async def update_comment_type(self, comment_id: str, comment_type: str) -> InsightCommentModel:
        """Update comment type"""
        try:
            if not comment_type or not comment_type.strip():
                raise ValidationException("Comment type is required")
            
            comment = await self.get_project_by_id(comment_id)
            comment.update_comment_type(comment_type.strip())
            
            updated_comment = await self.comment_repository.update_project(
                comment_id, comment.to_dict()
            )
            
            if not updated_comment:
                raise InsightCommentNotFoundException(f"Failed to update comment type for comment with ID {comment_id}")
            
            self.logger.info(f"Comment type updated for comment: {comment_id} to {comment_type}")
            return updated_comment
            
        except (InsightCommentNotFoundException, ValidationException):
            raise
        except Exception as e:
            self.logger.error(f"Update comment type failed: {str(e)}")
            raise 