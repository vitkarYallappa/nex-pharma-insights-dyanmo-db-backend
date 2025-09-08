"""
Content Implication Controller
Works with ContentImplicationService and handles API requests/responses
"""

from typing import List, Optional, Dict, Any
from app.services.content_implication_service import ContentImplicationService, ContentImplicationNotFoundException
from app.core.response import ResponseFormatter, APIResponse, to_response_format
from app.core.logging import get_logger
from app.core.exceptions import ValidationException

logger = get_logger("content_implication_controller")


class ContentImplicationController:
    """Content implication controller with query operations"""

    def __init__(self):
        self.content_implication_service = ContentImplicationService()
        self.logger = logger

    async def get_all_by_query(self,
                               content_id: Optional[str] = None, url_id: Optional[str] = None,
                               api_request_id: Optional[str] = None) -> APIResponse:
        """Get all content implication entries by query filters"""
        try:
            # Build query filters
            query_filters = {}
            if content_id:
                query_filters['content_id'] = content_id.strip()

            # Get implication entries from service
            implication_entries = await self.content_implication_service.get_all_by_query(
                query_filters=query_filters,
                limit=10
            )

            # Convert to response format
            response_data = [entry.to_response() if hasattr(entry, 'to_response') else entry for entry in
                             implication_entries]

            self.logger.info(
                f"Retrieved {len(implication_entries)} content implication entries with filters: {query_filters}")
            return ResponseFormatter.success(
                data=response_data,
                message=f"Retrieved {len(implication_entries)} content implication entries",
                request_id=api_request_id
            )

        except ValidationException as e:
            self.logger.error(f"Content implication query validation failed: {str(e)}")
            return ResponseFormatter.error(
                message=str(e),
                errors=[{"field": "validation", "message": str(e)}],
                request_id=api_request_id
            )

        except Exception as e:
            self.logger.error(f"Content implication query failed: {str(e)}")
            return ResponseFormatter.error(
                message="Failed to retrieve content implication entries",
                errors=[{"error": str(e)}],
                request_id=api_request_id
            )
