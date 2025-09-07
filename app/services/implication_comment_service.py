"""
Implication Comment Service - Works with ImplicationCommentModel and ImplicationCommentRepository
Follows the same pattern as ProjectService for consistency
"""

from typing import List, Optional, Dict, Any
from app.repositories.implication_comment_repository import ImplicationCommentRepository
from app.models.implication_comment_model import ImplicationCommentModel
from app.core.logging import get_logger
from app.core.exceptions import (
    ValidationException
)

logger = get_logger("implication_comment_service")

class ImplicationCommentNotFoundException(Exception):
    """Exception raised when implication comment entry is not found"""
    pass

class ImplicationCommentAlreadyExistsException(Exception):
    """Exception raised when implication comment entry already exists"""
    pass

class ImplicationCommentService:
    """Implication comment service with essential operations"""
    
    def __init__(self):
        self.comment_repository = ImplicationCommentRepository()
        self.logger = logger
    
    async def create_project(self, implication_id: str, comment_text: str, comment_type: Optional[str] = None) -> ImplicationCommentModel:
        """Create a new implication comment entry"""
        try:
            # Validate required fields
            if not implication_id or not implication_id.strip():
                raise ValidationException("Implication ID is required")
            
            if not comment_text or not comment_text.strip():
                raise ValidationException("Comment text is required")
            
            # Create comment model
            comment_model = ImplicationCommentModel.create_new(
                implication_id=implication_id.strip(),
                comment_text=comment_text.strip(),
                comment_type=comment_type.strip() if comment_type else None
            )
            
            # Save to database
            created_comment = await self.comment_repository.create(comment_model)
            self.logger.info(f"Implication comment entry created for implication {implication_id}")
            return created_comment
            
        except ValidationException:
            raise
        except Exception as e:
            self.logger.error(f"Create implication comment entry failed: {str(e)}")
            raise
    
    async def get_project_by_id(self, comment_id: str) -> ImplicationCommentModel:
        """Get implication comment entry by ID"""
        try:
            if not comment_id or not comment_id.strip():
                raise ValidationException("Comment ID is required")
            
            comment = await self.comment_repository.find_one_by_query({"pk": comment_id.strip()})
            if not comment:
                raise ImplicationCommentNotFoundException(f"Implication comment entry with ID {comment_id} not found")
            
            return comment
            
        except (ImplicationCommentNotFoundException, ValidationException):
            raise
        except Exception as e:
            self.logger.error(f"Get implication comment entry by ID failed: {str(e)}")
            raise
    
    async def get_projects_by_query(self, implication_id: Optional[str] = None,
                                   comment_type: Optional[str] = None,
                                   limit: Optional[int] = None) -> List[ImplicationCommentModel]:
        """Get implication comment entries with optional filters"""
        try:
            # Validate limit
            if limit is not None and limit <= 0:
                raise ValidationException("Limit must be a positive number")
            
            comments = await self.comment_repository.get_all_projects(
                implication_id=implication_id.strip() if implication_id else None,
                comment_type=comment_type.strip() if comment_type else None,
                limit=limit
            )
            
            self.logger.info(f"Retrieved {len(comments)} implication comment entries with filters: implication_id={implication_id}, comment_type={comment_type}")
            return comments
            
        except ValidationException:
            raise
        except Exception as e:
            self.logger.error(f"Get implication comment entries by query failed: {str(e)}")
            raise
    
    async def update_project(self, comment_id: str, update_data: Dict[str, Any]) -> ImplicationCommentModel:
        """Update implication comment entry by ID"""
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
                raise ImplicationCommentNotFoundException(f"Failed to update implication comment entry with ID {comment_id}")
            
            self.logger.info(f"Implication comment entry updated: {comment_id}")
            return updated_comment
            
        except (ImplicationCommentNotFoundException, ValidationException):
            raise
        except Exception as e:
            self.logger.error(f"Update implication comment entry failed: {str(e)}")
            raise
    
    async def get_comments_by_implication(self, implication_id: str, comment_type: Optional[str] = None) -> List[ImplicationCommentModel]:
        """Get all comments for a specific implication ID"""
        try:
            if not implication_id or not implication_id.strip():
                raise ValidationException("Implication ID is required")
            
            comments = await self.comment_repository.get_all_projects(
                implication_id=implication_id.strip(),
                comment_type=comment_type.strip() if comment_type else None
            )
            
            self.logger.info(f"Retrieved {len(comments)} comments for implication {implication_id}")
            return comments
            
        except ValidationException:
            raise
        except Exception as e:
            self.logger.error(f"Get comments by implication failed: {str(e)}")
            raise
    
    async def get_comments_by_type(self, comment_type: str, implication_id: Optional[str] = None) -> List[ImplicationCommentModel]:
        """Get all comments for a specific type"""
        try:
            if not comment_type or not comment_type.strip():
                raise ValidationException("Comment type is required")
            
            comments = await self.comment_repository.get_all_projects(
                comment_type=comment_type.strip(),
                implication_id=implication_id.strip() if implication_id else None
            )
            
            self.logger.info(f"Retrieved {len(comments)} comments for type {comment_type}")
            return comments
            
        except ValidationException:
            raise
        except Exception as e:
            self.logger.error(f"Get comments by type failed: {str(e)}")
            raise
    
    async def update_comment_text(self, comment_id: str, comment_text: str) -> ImplicationCommentModel:
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
                raise ImplicationCommentNotFoundException(f"Failed to update comment text for comment with ID {comment_id}")
            
            self.logger.info(f"Comment text updated for comment: {comment_id}")
            return updated_comment
            
        except (ImplicationCommentNotFoundException, ValidationException):
            raise
        except Exception as e:
            self.logger.error(f"Update comment text failed: {str(e)}")
            raise
    
    async def update_comment_type(self, comment_id: str, comment_type: str) -> ImplicationCommentModel:
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
                raise ImplicationCommentNotFoundException(f"Failed to update comment type for comment with ID {comment_id}")
            
            self.logger.info(f"Comment type updated for comment: {comment_id} to {comment_type}")
            return updated_comment
            
        except (ImplicationCommentNotFoundException, ValidationException):
            raise
        except Exception as e:
            self.logger.error(f"Update comment type failed: {str(e)}")
            raise 