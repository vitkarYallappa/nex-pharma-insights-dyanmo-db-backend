"""
Global Base URL Controller
Works with GlobalBaseUrlsService and handles API requests/responses
Follows the same pattern as ProjectController for consistency
"""

from typing import List, Optional, Dict, Any
from app.services.global_base_urls_service import GlobalBaseUrlsService, GlobalBaseUrlsNotFoundException, \
    GlobalBaseUrlsAlreadyExistsException
from app.core.response import ResponseFormatter, APIResponse
from app.core.logging import get_logger
from app.core.exceptions import ValidationException

logger = get_logger("global_base_url_controller")


class GlobalBaseUrlController:
    """Global base URL controller with essential operations"""

    def __init__(self):
        self.global_base_url_service = GlobalBaseUrlsService()
        self.logger = logger

    async def create_global_base_url(self, url: str, source_name: Optional[str] = None,
                                     source_type: Optional[str] = None,
                                     country_region: Optional[str] = None, is_active: bool = True,
                                     url_metadata: Optional[Dict[str, Any]] = None,
                                     request_id: Optional[str] = None) -> APIResponse:
        """Create a new global base URL"""
        try:
            global_base_url = await self.global_base_url_service.create_global_base_url(
                url=url,
                source_name=source_name,
                source_type=source_type,
                country_region=country_region,
                is_active=is_active,
                url_metadata=url_metadata
            )

            self.logger.info(f"Global base URL created successfully: {url}")
            return ResponseFormatter.created(
                data=global_base_url.to_response(),
                message=f"Global base URL {url} created successfully",
                request_id=request_id
            )

        except GlobalBaseUrlsAlreadyExistsException as e:
            self.logger.error(f"Global base URL creation failed: {str(e)}")
            return ResponseFormatter.error(
                message=str(e),
                errors=[{"field": "url", "message": "URL already exists"}],
                request_id=request_id
            )

        except ValidationException as e:
            self.logger.error(f"Global base URL creation validation failed: {str(e)}")
            return ResponseFormatter.error(
                message=str(e),
                errors=[{"field": "validation", "message": str(e)}],
                request_id=request_id
            )

        except Exception as e:
            self.logger.error(f"Global base URL creation failed: {str(e)}")
            return ResponseFormatter.error(
                message="Failed to create global base URL",
                errors=[{"error": str(e)}],
                request_id=request_id
            )

    async def get_global_base_url_by_id(self, url_id: str, request_id: Optional[str] = None) -> APIResponse:
        """Get global base URL by ID"""
        try:
            global_base_url = await self.global_base_url_service.get_global_base_url_by_id(url_id)

            self.logger.info(f"Global base URL retrieved: {url_id}")
            return ResponseFormatter.success(
                data=global_base_url.to_response(),
                message="Global base URL retrieved successfully",
                request_id=request_id
            )

        except GlobalBaseUrlsNotFoundException:
            self.logger.error(f"Global base URL not found: {url_id}")
            return ResponseFormatter.not_found(
                resource="Global base URL",
                request_id=request_id
            )

        except ValidationException as e:
            self.logger.error(f"Global base URL retrieval validation failed: {str(e)}")
            return ResponseFormatter.error(
                message=str(e),
                errors=[{"field": "validation", "message": str(e)}],
                request_id=request_id
            )

        except Exception as e:
            self.logger.error(f"Get global base URL failed: {str(e)}")
            return ResponseFormatter.error(
                message="Failed to retrieve global base URL",
                errors=[{"error": str(e)}],
                request_id=request_id
            )

    async def get_all_global_base_url(self,
                                      source_name: Optional[str] = None,
                                      source_type: Optional[str] = None,
                                      country_region: Optional[str] = None,
                                      is_active: Optional[bool] = None,
                                      limit: Optional[int] = None,
                                      request_id: Optional[str] = None) -> APIResponse:
        """Get global base URLs with optional filters"""
        try:
            global_base_urls = await self.global_base_url_service.get_all_global_base_url(
                source_name=source_name,
                source_type=source_type,
                country_region=country_region,
                is_active=is_active,
                limit=limit
            )

            urls_data = [
                {
                    "url": url.url,
                    "source_name": url.source_name,
                    "source_type": url.source_type
                }
                for url in global_base_urls
            ]

            # Build filter description for message
            filters = []
            if source_name:
                filters.append(f"source_name={source_name}")
            if source_type:
                filters.append(f"source_type={source_type}")
            if country_region:
                filters.append(f"country_region={country_region}")
            if is_active is not None:
                filters.append(f"is_active={is_active}")
            if limit:
                filters.append(f"limit={limit}")

            filter_desc = f" with filters: {', '.join(filters)}" if filters else ""

            self.logger.info(f"Retrieved {len(global_base_urls)} global base URLs{filter_desc}")
            return ResponseFormatter.success(
                data={
                    "global_base_urls": urls_data,
                    "count": len(urls_data),
                    "filters": {
                        "source_name": source_name,
                        "source_type": source_type,
                        "country_region": country_region,
                        "is_active": is_active,
                        "limit": limit
                    }
                },
                message=f"Retrieved {len(global_base_urls)} global base URLs{filter_desc}",
                request_id=request_id
            )

        except ValidationException as e:
            self.logger.error(f"Global base URL query validation failed: {str(e)}")
            return ResponseFormatter.error(
                message=str(e),
                errors=[{"field": "validation", "message": str(e)}],
                request_id=request_id
            )

        except Exception as e:
            self.logger.error(f"Global base URL query failed: {str(e)}")
            return ResponseFormatter.error(
                message="Failed to retrieve global base URLs",
                errors=[{"error": str(e)}],
                request_id=request_id
            )
    
    async def delete_global_base_url(self, url_id: str, request_id: Optional[str] = None) -> APIResponse:
        """Delete global base URL by ID"""
        try:
            deleted = await self.global_base_url_service.delete_global_base_url(url_id)
            
            if deleted:
                self.logger.info(f"Global base URL deleted successfully: {url_id}")
                return ResponseFormatter.deleted(
                    message=f"Global base URL with ID '{url_id}' deleted successfully",
                    request_id=request_id
                )
            else:
                self.logger.warning(f"Global base URL deletion failed: {url_id}")
                return ResponseFormatter.error(
                    message="Failed to delete global base URL",
                    errors=[{"field": "url_id", "message": "Global base URL not found or deletion failed"}],
                    request_id=request_id
                )
            
        except ValidationException as e:
            self.logger.error(f"Global base URL deletion validation failed: {str(e)}")
            return ResponseFormatter.error(
                message=str(e),
                errors=[{"field": "validation", "message": str(e)}],
                request_id=request_id
            )
            
        except GlobalBaseUrlsNotFoundException as e:
            self.logger.error(f"Global base URL deletion failed: {str(e)}")
            return ResponseFormatter.error(
                message=str(e),
                errors=[{"field": "url_id", "message": "Global base URL not found"}],
                request_id=request_id
            )
            
        except Exception as e:
            self.logger.error(f"Global base URL deletion failed: {str(e)}")
            return ResponseFormatter.error(
                message="Failed to delete global base URL",
                errors=[{"error": str(e)}],
                request_id=request_id
            )