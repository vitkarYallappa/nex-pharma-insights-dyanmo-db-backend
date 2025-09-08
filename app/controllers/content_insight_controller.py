"""
Content Insight Controller
Works with ContentInsightService and handles API requests/responses
"""

from typing import List, Optional, Dict, Any
from app.services.content_insight_service import ContentInsightService, ContentInsightNotFoundException
from app.use_cases.insights_regenerate_service import InsightsRegenerateService
from app.core.response import ResponseFormatter, APIResponse, to_response_format
from app.core.logging import get_logger
from app.core.exceptions import ValidationException

logger = get_logger("content_insight_controller")


class ContentInsightController:
    """Content insight controller with query operations"""

    def __init__(self):
        self.content_insight_service = ContentInsightService()
        self.insights_regenerate_service = InsightsRegenerateService()
        self.logger = logger

    async def get_all_by_query(self, content_id: Optional[str] = None,
                               limit: Optional[int] = None, api_request_id: Optional[str] = None) -> APIResponse:
        """Get all content insight entries by query filters"""
        try:
            # Build query filters
            query_filters = {}
            if content_id:
                query_filters['content_id'] = content_id.strip()

            # Get insight entries from service
            insight_entries = await self.content_insight_service.get_all_by_query(
                query_filters=query_filters,
                limit=limit
            )

            # Convert to response format
            response_data = [entry.to_response() if hasattr(entry, 'to_response') else entry for entry in
                             insight_entries]

            self.logger.info(f"Retrieved {len(insight_entries)} content insight entries with filters: {query_filters}")
            return ResponseFormatter.success(
                data=response_data,
                message=f"Retrieved {len(insight_entries)} content insight entries",
                request_id=api_request_id
            )

        except ValidationException as e:
            self.logger.error(f"Content insight query validation failed: {str(e)}")
            return ResponseFormatter.error(
                message=str(e),
                errors=[{"field": "validation", "message": str(e)}],
                request_id=api_request_id
            )

        except Exception as e:
            self.logger.error(f"Content insight query failed: {str(e)}")
            return ResponseFormatter.error(
                message="Failed to retrieve content insight entries",
                errors=[{"error": str(e)}],
                request_id=api_request_id
            )

    async def regenerate_insight(self, content_id: str,
                                 metadata_field1: Optional[str] = None,
                                 metadata_field2: Optional[str] = None,
                                 metadata_field3: Optional[str] = None,
                                 question_text: Optional[str] = None,
                                 api_request_id: Optional[str] = None) -> APIResponse:
        """Regenerate insight for given content"""
        try:
            result = await self.insights_regenerate_service.regenerate_insight(
                content_id=content_id,
                metadata_field1=metadata_field1,
                metadata_field2=metadata_field2,
                metadata_field3=metadata_field3,
                question_text=question_text
            )

            self.logger.info(f"Insight regenerated successfully for content: {content_id}")
            return ResponseFormatter.success(
                data=result,
                message="Insight regenerated successfully",
                request_id=api_request_id
            )

        except ValidationException as e:
            self.logger.error(f"Insight regeneration validation failed: {str(e)}")
            return ResponseFormatter.error(
                message=str(e),
                errors=[{"field": "validation", "message": str(e)}],
                request_id=api_request_id
            )

        except Exception as e:
            self.logger.error(f"Insight regeneration failed: {str(e)}")
            return ResponseFormatter.error(
                message="Failed to regenerate insight",
                errors=[{"error": str(e)}],
                request_id=api_request_id
            )
