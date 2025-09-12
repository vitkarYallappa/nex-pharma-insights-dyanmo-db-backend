"""
Global Keywords Controller
Works with GlobalKeywordsService and handles API requests/responses
Follows the same pattern as ProjectController for consistency
"""

from typing import List, Optional, Dict, Any
from app.services.global_keywords_service import GlobalKeywordsService, GlobalKeywordsNotFoundException, GlobalKeywordsAlreadyExistsException
from app.core.response import ResponseFormatter, APIResponse
from app.core.logging import get_logger
from app.core.exceptions import ValidationException

logger = get_logger("global_keywords_controller")

class GlobalKeywordsController:
    """Global keywords controller with essential operations"""
    
    def __init__(self):
        self.global_keywords_service = GlobalKeywordsService()
        self.logger = logger
    
    async def create_global_keyword(self, keyword: str, keyword_type: Optional[str] = None,
                                   request_id: Optional[str] = None) -> APIResponse:
        """Create a new global keyword"""
        try:
            global_keyword = await self.global_keywords_service.create_global_keyword(
                keyword=keyword,
                keyword_type=keyword_type
            )
            
            self.logger.info(f"Global keyword created successfully: {keyword}")
            return ResponseFormatter.created(
                data=global_keyword.to_response(),
                message=f"Global keyword '{keyword}' created successfully",
                request_id=request_id
            )
            
        except ValidationException as e:
            self.logger.error(f"Global keyword creation validation failed: {str(e)}")
            return ResponseFormatter.error(
                message=str(e),
                errors=[{"field": "validation", "message": str(e)}],
                request_id=request_id
            )
            
        except GlobalKeywordsAlreadyExistsException as e:
            self.logger.error(f"Global keyword creation failed: {str(e)}")
            return ResponseFormatter.error(
                message=str(e),
                errors=[{"field": "keyword", "message": "Global keyword already exists"}],
                request_id=request_id
            )
            
        except Exception as e:
            self.logger.error(f"Global keyword creation failed: {str(e)}")
            return ResponseFormatter.error(
                message="Failed to create global keyword",
                errors=[{"error": str(e)}],
                request_id=request_id
            )
    
    async def get_global_keywords_by_query(self, keyword_type: Optional[str] = None,
                                          limit: Optional[int] = None,
                                          request_id: Optional[str] = None) -> APIResponse:
        """Get global keywords with optional filters"""
        try:
            global_keywords = await self.global_keywords_service.get_all_global_keyword(
                keyword_type=keyword_type,
                limit=limit
            )
            
            global_keywords_data = [keyword.to_response() for keyword in global_keywords]
            
            # Build filter description for message
            filters = []
            if keyword_type:
                filters.append(f"keyword_type={keyword_type}")
            if limit:
                filters.append(f"limit={limit}")
            
            filter_desc = f" with filters: {', '.join(filters)}" if filters else ""
            
            self.logger.info(f"Retrieved {len(global_keywords)} global keywords{filter_desc}")
            return ResponseFormatter.success(
                data={
                    "global_keywords": global_keywords_data,
                    "count": len(global_keywords_data),
                    "filters": {
                        "keyword_type": keyword_type,
                        "limit": limit
                    }
                },
                message=f"Retrieved {len(global_keywords)} global keywords{filter_desc}",
                request_id=request_id
            )
            
        except ValidationException as e:
            self.logger.error(f"Global keywords query validation failed: {str(e)}")
            return ResponseFormatter.error(
                message=str(e),
                errors=[{"field": "validation", "message": str(e)}],
                request_id=request_id
            )
            
        except Exception as e:
            self.logger.error(f"Global keywords query failed: {str(e)}")
            return ResponseFormatter.error(
                message="Failed to retrieve global keywords",
                errors=[{"error": str(e)}],
                request_id=request_id
            )
    
    async def delete_global_keyword(self, keyword_id: str, request_id: Optional[str] = None) -> APIResponse:
        """Delete global keyword by ID"""
        try:
            deleted = await self.global_keywords_service.delete_global_keyword(keyword_id)
            
            if deleted:
                self.logger.info(f"Global keyword deleted successfully: {keyword_id}")
                return ResponseFormatter.deleted(
                    message=f"Global keyword with ID '{keyword_id}' deleted successfully",
                    request_id=request_id
                )
            else:
                self.logger.warning(f"Global keyword deletion failed: {keyword_id}")
                return ResponseFormatter.error(
                    message="Failed to delete global keyword",
                    errors=[{"field": "keyword_id", "message": "Global keyword not found or deletion failed"}],
                    request_id=request_id
                )
            
        except ValidationException as e:
            self.logger.error(f"Global keyword deletion validation failed: {str(e)}")
            return ResponseFormatter.error(
                message=str(e),
                errors=[{"field": "validation", "message": str(e)}],
                request_id=request_id
            )
            
        except GlobalKeywordsNotFoundException as e:
            self.logger.error(f"Global keyword deletion failed: {str(e)}")
            return ResponseFormatter.error(
                message=str(e),
                errors=[{"field": "keyword_id", "message": "Global keyword not found"}],
                request_id=request_id
            )
            
        except Exception as e:
            self.logger.error(f"Global keyword deletion failed: {str(e)}")
            return ResponseFormatter.error(
                message="Failed to delete global keyword",
                errors=[{"error": str(e)}],
                request_id=request_id
            )
    
    async def get_all_global_keywords_by_query(self, keyword_type: Optional[str] = None,
                                              limit: Optional[int] = None,
                                              request_id: Optional[str] = None) -> APIResponse:
        """Get all global keywords with optional filters (alias for get_global_keywords_by_query)"""
        return await self.get_global_keywords_by_query(
            keyword_type=keyword_type,
            limit=limit,
            request_id=request_id
        ) 