"""
Content Repository Controller
Works with ContentRepositoryService and handles API requests/responses
"""

from typing import List, Optional, Dict, Any
from app.services.content_repository_service import ContentRepositoryService, ContentRepositoryNotFoundException
from app.core.response import ResponseFormatter, APIResponse, to_response_format
from app.core.logging import get_logger
from app.core.exceptions import ValidationException

logger = get_logger("content_repository_controller")


class ContentRepositoryController:
    """Content repository controller with query operations"""

    def __init__(self):
        self.content_repository_service = ContentRepositoryService()
        self.logger = logger

    async def get_all_by_query(self,
                               project_id: Optional[str] = None,
                               request_id: Optional[str] = None,
                               limit: Optional[int] = None,
                               api_request_id: Optional[str] = None) -> APIResponse:
        """Get all content repository entries by query filters"""
        try:
            # Build query filters
            query_filters = {}
            if project_id:
                query_filters['project_id'] = project_id.strip()
            if request_id:
                pass
                # query_filters['request_id'] = request_id.strip()

            # Get content entries from service
            content_entries = await self.content_repository_service.get_all_by_query(
                query_filters=query_filters,
                limit=limit
            )

            # Convert to response format
            response_data = [entry.to_response() if hasattr(entry, 'to_response') else entry for entry in
                             content_entries]

            self.logger.info(
                f"Retrieved {len(content_entries)} content repository entries with filters: {query_filters}")
            return ResponseFormatter.success(
                data=response_data,
                message=f"Retrieved {len(content_entries)} content repository entries",
                request_id=api_request_id
            )

        except ValidationException as e:
            self.logger.error(f"Content repository query validation failed: {str(e)}")
            return ResponseFormatter.error(
                message=str(e),
                errors=[{"field": "validation", "message": str(e)}],
                request_id=api_request_id
            )

        except Exception as e:
            self.logger.error(f"Content repository query failed: {str(e)}")
            return ResponseFormatter.error(
                message="Failed to retrieve content repository entries",
                errors=[{"error": str(e)}],
                request_id=api_request_id
            )
