"""
Source URLs Service - Works with SourceUrlsModel and SourceUrlsRepository
Follows the same pattern as ProjectService for consistency
"""

from typing import List, Optional, Dict, Any
from app.repositories.source_urls_repository import SourceUrlsRepository
from app.models.source_urls_model import SourceUrlsModel
from app.core.logging import get_logger
from app.core.exceptions import (
    ValidationException
)

logger = get_logger("source_urls_service")

class SourceUrlsNotFoundException(Exception):
    """Exception raised when source URL is not found"""
    pass

class SourceUrlsAlreadyExistsException(Exception):
    """Exception raised when source URL already exists"""
    pass

class SourceUrlsService:
    """Source URLs service with essential operations"""
    
    def __init__(self):
        self.urls_repository = SourceUrlsRepository()
        self.logger = logger
    
    async def create_project(self, request_id: str, url: str, source_name: Optional[str] = None,
                            source_type: Optional[str] = None, country_region: Optional[str] = None,
                            is_active: bool = True, url_metadata: Optional[Dict[str, Any]] = None) -> SourceUrlsModel:
        """Create a new source URL"""
        try:
            # Validate required fields
            if not request_id or not request_id.strip():
                raise ValidationException("Request ID is required")
            
            if not url or not url.strip():
                raise ValidationException("URL is required")
            
            # Create URL model
            url_model = SourceUrlsModel.create_new(
                request_id=request_id.strip(),
                url=url.strip(),
                source_name=source_name.strip() if source_name else None,
                source_type=source_type.strip() if source_type else None,
                country_region=country_region.strip() if country_region else None,
                is_active=is_active,
                url_metadata=url_metadata or {}
            )
            
            # Save to database
            created_url = await self.urls_repository.create(url_model)
            self.logger.info(f"Source URL created: {url} for request {request_id}")
            return created_url
            
        except ValidationException:
            raise
        except Exception as e:
            self.logger.error(f"Create source URL failed: {str(e)}")
            raise
    
    async def get_source_urls_by_id(self, url_id: str) -> SourceUrlsModel:
        """Get source URL by ID"""
        try:
            if not url_id or not url_id.strip():
                raise ValidationException("URL ID is required")
            
            url = await self.urls_repository.find_one_by_query({"pk": url_id.strip()})
            if not url:
                raise SourceUrlsNotFoundException(f"Source URL with ID {url_id} not found")
            
            return url
            
        except (SourceUrlsNotFoundException, ValidationException):
            raise
        except Exception as e:
            self.logger.error(f"Get source URL by ID failed: {str(e)}")
            raise
    
    async def get_source_urls_by_query(self, request_id: Optional[str] = None,
                                   source_name: Optional[str] = None,
                                   source_type: Optional[str] = None,
                                   country_region: Optional[str] = None,
                                   is_active: Optional[bool] = None,
                                   limit: Optional[int] = None) -> List[SourceUrlsModel]:
        """Get source URLs with optional filters"""
        try:
            # Validate limit
            if limit is not None and limit <= 0:
                raise ValidationException("Limit must be a positive number")
            
            urls = await self.urls_repository.get_all_source_urls(
                request_id=request_id.strip() if request_id else None,
                source_name=source_name.strip() if source_name else None,
                source_type=source_type.strip() if source_type else None,
                country_region=country_region.strip() if country_region else None,
                is_active=is_active,
                limit=limit
            )
            
            self.logger.info(f"Retrieved {len(urls)} source URLs with filters: request_id={request_id}, source_name={source_name}, source_type={source_type}, country_region={country_region}, is_active={is_active}")
            return urls
            
        except ValidationException:
            raise
        except Exception as e:
            self.logger.error(f"Get source URLs by query failed: {str(e)}")
            raise
    
    async def update_source_urls(self, url_id: str, update_data: Dict[str, Any]) -> SourceUrlsModel:
        """Update source URL by ID"""
        try:
            if not url_id or not url_id.strip():
                raise ValidationException("URL ID is required")
            
            # Check if URL exists
            existing_url = await self.get_source_urls_by_id(url_id)
            
            # Prepare update data (remove None values and add updated_at)
            clean_update_data = {k: v for k, v in update_data.items() if v is not None}
            if clean_update_data:
                from datetime import datetime
                clean_update_data["updated_at"] = datetime.utcnow().isoformat()
            
            updated_url = await self.urls_repository.update_source_urls(
                url_id.strip(), clean_update_data
            )
            
            if not updated_url:
                raise SourceUrlsNotFoundException(f"Failed to update source URL with ID {url_id}")
            
            self.logger.info(f"Source URL updated: {url_id}")
            return updated_url
            
        except (SourceUrlsNotFoundException, ValidationException):
            raise
        except Exception as e:
            self.logger.error(f"Update source URL failed: {str(e)}")
            raise 