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
    
    async def create_implication_comment(self, implication_id: str, comment_text: str, comment_type: Optional[str] = None) -> ImplicationCommentModel:
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
    
    async def get_implication_comment_by_id(self, comment_id: str) -> ImplicationCommentModel:
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
    
    async def get_all_implication_comment(self, implication_id: Optional[str] = None,
                                   comment_type: Optional[str] = None,
                                   limit: Optional[int] = None) -> List[ImplicationCommentModel]:
        """Get implication comment entries with optional filters"""
        try:
            # Validate limit
            if limit is not None and limit <= 0:
                raise ValidationException("Limit must be a positive number")
            
            comments = await self.comment_repository.get_all_implication_comment(
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
    
    async def update_implication_comment(self, comment_id: str, update_data: Dict[str, Any]) -> ImplicationCommentModel:
        """Update implication comment entry by ID"""
        try:
            if not comment_id or not comment_id.strip():
                raise ValidationException("Comment ID is required")
            
            # Check if comment exists
            existing_comment = await self.get_implication_comment_by_id(comment_id)
            
            # Prepare update data (remove None values and add updated_at)
            clean_update_data = {k: v for k, v in update_data.items() if v is not None}
            if clean_update_data:
                from datetime import datetime
                clean_update_data["updated_at"] = datetime.utcnow().isoformat()
            
            updated_comment = await self.comment_repository.update_implication_comment(
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
    
    async def get_all_by_query(self, query_filters: Optional[Dict[str, Any]] = None, limit: Optional[int] = None) -> List[ImplicationCommentModel]:
        """Get all implication comment entries by query filters"""
        try:
            # Validate limit if provided
            if limit is not None and limit <= 0:
                raise ValidationException("Limit must be greater than 0")
            
            # Get entries from repository
            entries = await self.comment_repository.find_all_by_query(query=query_filters, limit=limit)
            
            # Convert to model objects - check if entries are already model objects or dicts
            comment_models = []
            for entry in entries:
                if isinstance(entry, ImplicationCommentModel):
                    comment_models.append(entry)
                else:
                    comment_models.append(ImplicationCommentModel.from_dict(entry))
            
            self.logger.info(f"Retrieved {len(comment_models)} implication comment entries with filters: {query_filters}")
            return comment_models
            
        except ValidationException:
            raise
        except Exception as e:
            self.logger.error(f"Get implication comment entries by query failed: {str(e)}")
            raise
