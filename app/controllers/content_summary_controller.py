"""
Content Summary Controller
Works with ContentSummaryService and handles API requests/responses
"""

from typing import List, Optional, Dict, Any
from app.services.content_summary_service import ContentSummaryService, ContentSummaryNotFoundException
from app.core.response import ResponseFormatter, APIResponse, to_response_format
from app.core.logging import get_logger
from app.core.exceptions import ValidationException

logger = get_logger("content_summary_controller")


class ContentSummaryController:
    """Content summary controller with query operations"""

    def __init__(self):
        self.content_summary_service = ContentSummaryService()
        self.logger = logger

    async def get_all_by_query(self,
                               content_id: Optional[str] = None,
                               limit: Optional[int] = None,
                               api_request_id: Optional[str] = None) -> APIResponse:
        """Get all content summary entries by query filters"""
        try:
            # Build query filters
            query_filters = {}
            if content_id:
                query_filters['content_id'] = content_id.strip()

            # Get summary entries from service
            summary_entries = await self.content_summary_service.get_all_by_query(
                query_filters=query_filters,
                limit=limit
            )

            # Convert to response format
            response_data = [entry.to_response() if hasattr(entry, 'to_response') else entry for entry in
                             summary_entries]

            self.logger.info(f"Retrieved {len(summary_entries)} content summary entries with filters: {query_filters}")
            return ResponseFormatter.success(
                data=response_data,
                message=f"Retrieved {len(summary_entries)} content summary entries",
                request_id=api_request_id
            )

        except ValidationException as e:
            self.logger.error(f"Content summary query validation failed: {str(e)}")
            return ResponseFormatter.error(
                message=str(e),
                errors=[{"field": "validation", "message": str(e)}],
                request_id=api_request_id
            )

        except Exception as e:
            self.logger.error(f"Content summary query failed: {str(e)}")
            return ResponseFormatter.error(
                message="Failed to retrieve content summary entries",
                errors=[{"error": str(e)}],
                request_id=api_request_id
            )
