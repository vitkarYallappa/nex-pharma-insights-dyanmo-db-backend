"""
Implication Comment Controller
Works with ImplicationCommentService and handles API requests/responses
"""

from typing import List, Optional, Dict, Any
from app.services.implication_comment_service import ImplicationCommentService, ImplicationCommentNotFoundException
from app.core.response import ResponseFormatter, APIResponse, to_response_format
from app.core.logging import get_logger
from app.core.exceptions import ValidationException

logger = get_logger("implication_comment_controller")

class ImplicationCommentController:
    """Implication comment controller with query operations"""
    
    def __init__(self):
        self.implication_comment_service = ImplicationCommentService()
        self.logger = logger
    
    async def get_all_by_query(self, implication_id: Optional[str] = None, comment_type: Optional[str] = None,
                              limit: Optional[int] = None, api_request_id: Optional[str] = None) -> APIResponse:
        """Get all implication comment entries by query filters"""
        try:
            # Build query filters
            query_filters = {}
            if implication_id:
                query_filters['implication_id'] = implication_id.strip()
            if comment_type:
                query_filters['comment_type'] = comment_type.strip()
            
            # Get comment entries from service
            comment_entries = await self.implication_comment_service.get_all_by_query(
                query_filters=query_filters,
                limit=limit
            )
            
            # Convert to response format
            response_data = [entry.to_response() if hasattr(entry, 'to_response') else entry for entry in comment_entries]
            
            self.logger.info(f"Retrieved {len(comment_entries)} implication comment entries with filters: {query_filters}")
            return ResponseFormatter.success(
                data=response_data,
                message=f"Retrieved {len(comment_entries)} implication comment entries",
                request_id=api_request_id
            )
            
        except ValidationException as e:
            self.logger.error(f"Implication comment query validation failed: {str(e)}")
            return ResponseFormatter.error(
                message=str(e),
                errors=[{"field": "validation", "message": str(e)}],
                request_id=api_request_id
            )
            
        except Exception as e:
            self.logger.error(f"Implication comment query failed: {str(e)}")
            return ResponseFormatter.error(
                message="Failed to retrieve implication comment entries",
                errors=[{"error": str(e)}],
                request_id=api_request_id
            )
    
    async def create_implication_comment(self, implication_id: str, comment_text: str, 
                                       comment_type: Optional[str] = None,
                                       api_request_id: Optional[str] = None) -> APIResponse:
        """Create a new implication comment"""
        try:
            comment = await self.implication_comment_service.create_implication_comment(
                implication_id=implication_id,
                comment_text=comment_text,
                comment_type=comment_type
            )
            
            self.logger.info(f"Implication comment created successfully for implication: {implication_id}")
            return ResponseFormatter.created(
                data=comment.to_response(),
                message="Implication comment created successfully",
                request_id=api_request_id
            )
            
        except ValidationException as e:
            self.logger.error(f"Implication comment creation validation failed: {str(e)}")
            return ResponseFormatter.error(
                message=str(e),
                errors=[{"field": "validation", "message": str(e)}],
                request_id=api_request_id
            )
            
        except Exception as e:
            self.logger.error(f"Implication comment creation failed: {str(e)}")
            return ResponseFormatter.error(
                message="Failed to create implication comment",
                errors=[{"error": str(e)}],
                request_id=api_request_id
            )
