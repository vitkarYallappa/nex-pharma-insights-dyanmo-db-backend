"""
Insight Comment Controller
Works with InsightCommentService and handles API requests/responses
"""

from typing import List, Optional, Dict, Any
from app.services.insight_comment_service import InsightCommentService, InsightCommentNotFoundException
from app.core.response import ResponseFormatter, APIResponse, to_response_format
from app.core.logging import get_logger
from app.core.exceptions import ValidationException

logger = get_logger("insight_comment_controller")

class InsightCommentController:
    """Insight comment controller with query operations"""
    
    def __init__(self):
        self.insight_comment_service = InsightCommentService()
        self.logger = logger
    
    async def get_all_by_query(self, insight_id: Optional[str] = None, comment_type: Optional[str] = None,
                              limit: Optional[int] = None, api_request_id: Optional[str] = None) -> APIResponse:
        """Get all insight comment entries by query filters"""
        try:
            # Build query filters
            query_filters = {}
            if insight_id:
                query_filters['insight_id'] = insight_id.strip()
            if comment_type:
                query_filters['comment_type'] = comment_type.strip()
            
            # Get comment entries from service
            comment_entries = await self.insight_comment_service.get_all_by_query(
                query_filters=query_filters,
                limit=limit
            )
            
            # Convert to response format
            response_data = [entry.to_response() if hasattr(entry, 'to_response') else entry for entry in comment_entries]
            
            self.logger.info(f"Retrieved {len(comment_entries)} insight comment entries with filters: {query_filters}")
            return ResponseFormatter.success(
                data=response_data,
                message=f"Retrieved {len(comment_entries)} insight comment entries",
                request_id=api_request_id
            )
            
        except ValidationException as e:
            self.logger.error(f"Insight comment query validation failed: {str(e)}")
            return ResponseFormatter.error(
                message=str(e),
                errors=[{"field": "validation", "message": str(e)}],
                request_id=api_request_id
            )
            
        except Exception as e:
            self.logger.error(f"Insight comment query failed: {str(e)}")
            return ResponseFormatter.error(
                message="Failed to retrieve insight comment entries",
                errors=[{"error": str(e)}],
                request_id=api_request_id
            )
    
    async def create_insight_comment(self, insight_id: str, comment_text: str, 
                                   comment_type: Optional[str] = None,
                                   api_request_id: Optional[str] = None) -> APIResponse:
        """Create a new insight comment"""
        try:
            comment = await self.insight_comment_service.create_insight_comment(
                insight_id=insight_id,
                comment_text=comment_text,
                comment_type=comment_type
            )
            
            self.logger.info(f"Insight comment created successfully for insight: {insight_id}")
            return ResponseFormatter.created(
                data=comment.to_response(),
                message="Insight comment created successfully",
                request_id=api_request_id
            )
            
        except ValidationException as e:
            self.logger.error(f"Insight comment creation validation failed: {str(e)}")
            return ResponseFormatter.error(
                message=str(e),
                errors=[{"field": "validation", "message": str(e)}],
                request_id=api_request_id
            )
            
        except Exception as e:
            self.logger.error(f"Insight comment creation failed: {str(e)}")
            return ResponseFormatter.error(
                message="Failed to create insight comment",
                errors=[{"error": str(e)}],
                request_id=api_request_id
            )
