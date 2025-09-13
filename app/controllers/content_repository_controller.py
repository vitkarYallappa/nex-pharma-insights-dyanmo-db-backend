"""
Content Repository Controller
Works with ContentRepositoryService and handles API requests/responses
"""

from typing import List, Optional, Dict, Any
from app.services.content_repository_service import ContentRepositoryService, ContentRepositoryNotFoundException
from app.services.content_relevance_service import ContentRelevanceService, ContentRelevanceNotFoundException
from app.core.response import ResponseFormatter, APIResponse, to_response_format
from app.core.logging import get_logger
from app.core.exceptions import ValidationException

logger = get_logger("content_repository_controller")


class ContentRepositoryController:
    """Content repository controller with query operations"""

    def __init__(self):
        self.content_repository_service = ContentRepositoryService()
        self.content_relevance_service = ContentRelevanceService()
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
                limit=1000
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

    async def update_relevance_by_content_id(self, 
                                           content_id: str,
                                           is_relevant: bool,
                                           relevance_text: Optional[str] = None,
                                           relevance_score: Optional[float] = None,
                                           confidence_score: Optional[float] = None,
                                           relevance_category: Optional[str] = None,
                                           updated_by: Optional[str] = None,
                                           api_request_id: Optional[str] = None) -> APIResponse:
        """Update content relevance by content ID"""
        try:
            # Validate required fields
            if not content_id or not content_id.strip():
                raise ValidationException("Content ID is required")

            # Update relevance using service
            updated_relevance = await self.content_relevance_service.update_relevance_by_content_id(
                content_id=content_id.strip(),
                is_relevant=is_relevant,
                relevance_text=relevance_text,
                relevance_score=relevance_score,
                confidence_score=confidence_score,
                relevance_category=relevance_category,
                updated_by=updated_by or "user"
            )

            # Convert to response format
            response_data = updated_relevance.to_response() if hasattr(updated_relevance, 'to_response') else updated_relevance.to_dict()

            self.logger.info(f"Content relevance updated for content {content_id}: is_relevant={is_relevant}")
            return ResponseFormatter.success(
                data=response_data,
                message=f"Content relevance updated successfully for content {content_id}",
                request_id=api_request_id
            )

        except ValidationException as e:
            self.logger.error(f"Content relevance update validation failed: {str(e)}")
            return ResponseFormatter.error(
                message=str(e),
                errors=[{"field": "validation", "message": str(e)}],
                request_id=api_request_id
            )

        except ContentRelevanceNotFoundException as e:
            self.logger.error(f"Content relevance not found: {str(e)}")
            return ResponseFormatter.error(
                message=str(e),
                errors=[{"field": "content_id", "message": str(e)}],
                request_id=api_request_id,
                status_code=404
            )

        except Exception as e:
            self.logger.error(f"Content relevance update failed: {str(e)}")
            return ResponseFormatter.error(
                message="Failed to update content relevance",
                errors=[{"error": str(e)}],
                request_id=api_request_id
            )
