"""
Global Base URLs Service - Works with GlobalBaseUrlsModel and GlobalBaseUrlsRepository
Follows the same pattern as ProjectService for consistency
"""

from typing import List, Optional, Dict, Any
from app.repositories.global_base_urls_repository import GlobalBaseUrlsRepository
from app.models.global_base_urls_model import GlobalBaseUrlsModel
from app.core.logging import get_logger
from app.core.exceptions import (
    ValidationException
)

logger = get_logger("global_base_urls_service")


class GlobalBaseUrlsNotFoundException(Exception):
    """Exception raised when global base URL is not found"""
    pass


class GlobalBaseUrlsAlreadyExistsException(Exception):
    """Exception raised when global base URL already exists"""
    pass


class GlobalBaseUrlsService:
    """Global base URLs service with essential operations"""

    def __init__(self):
        self.urls_repository = GlobalBaseUrlsRepository()
        self.logger = logger

    async def create_global_base_url(self, url: str, source_name: Optional[str] = None,
                                     source_type: Optional[str] = None,
                                     country_region: Optional[str] = None, is_active: bool = True,
                                     url_metadata: Optional[Dict[str, Any]] = None) -> GlobalBaseUrlsModel:
        """Create a new global base URL"""
        try:
            # Validate required fields
            if not url or not url.strip():
                raise ValidationException("URL is required")

            # Create URL model
            url_model = GlobalBaseUrlsModel.create_new(
                url=url.strip(),
                source_name=source_name.strip() if source_name else None,
                source_type=source_type.strip() if source_type else None,
                country_region=country_region.strip() if country_region else None,
                is_active=is_active,
                url_metadata=url_metadata or {}
            )

            # Save to database
            created_url = await self.urls_repository.create(url_model)
            self.logger.info(f"Global base URL created: {url}")
            return created_url

        except ValidationException:
            raise
        except Exception as e:
            self.logger.error(f"Create global base URL failed: {str(e)}")
            raise

    async def get_global_base_url_by_id(self, url_id: str) -> GlobalBaseUrlsModel:
        """Get global base URL by ID"""
        try:
            if not url_id or not url_id.strip():
                raise ValidationException("URL ID is required")

            url = await self.urls_repository.find_one_by_query({"pk": url_id.strip()})
            if not url:
                raise GlobalBaseUrlsNotFoundException(f"Global base URL with ID {url_id} not found")

            return url

        except (GlobalBaseUrlsNotFoundException, ValidationException):
            raise
        except Exception as e:
            self.logger.error(f"Get global base URL by ID failed: {str(e)}")
            raise

    async def get_all_global_base_url(self,
                                      source_name: Optional[str] = None,
                                      source_type: Optional[str] = None,
                                      country_region: Optional[str] = None,
                                      is_active: Optional[bool] = None,
                                      limit: Optional[int] = None) -> List[GlobalBaseUrlsModel]:
        """Get global base URLs with optional filters"""
        try:
            # Validate limit
            if limit is not None and limit <= 0:
                raise ValidationException("Limit must be a positive number")

            urls = await self.urls_repository.get_all_global_base_url(
                source_name=source_name.strip() if source_name else None,
                source_type=source_type.strip() if source_type else None,
                country_region=country_region.strip() if country_region else None,
                is_active=is_active,
                limit=limit
            )

            self.logger.info(
                f"Retrieved {len(urls)} global base URLs with filters: source_name={source_name}, source_type={source_type}, country_region={country_region}, is_active={is_active}")
            return urls

        except ValidationException:
            raise
        except Exception as e:
            self.logger.error(f"Get global base URLs by query failed: {str(e)}")
            raise

    async def update_global_base_url(self, url_id: str, update_data: Dict[str, Any]) -> GlobalBaseUrlsModel:
        """Update global base URL by ID"""
        try:
            if not url_id or not url_id.strip():
                raise ValidationException("URL ID is required")

            # Check if URL exists
            existing_url = await self.get_global_base_url_by_id(url_id)

            # Prepare update data (remove None values and add updated_at)
            clean_update_data = {k: v for k, v in update_data.items() if v is not None}
            if clean_update_data:
                from datetime import datetime
                clean_update_data["updated_at"] = datetime.utcnow().isoformat()

            updated_url = await self.urls_repository.update_global_base_url(
                url_id.strip(), clean_update_data
            )

            if not updated_url:
                raise GlobalBaseUrlsNotFoundException(f"Failed to update global base URL with ID {url_id}")

            self.logger.info(f"Global base URL updated: {url_id}")
            return updated_url

        except (GlobalBaseUrlsNotFoundException, ValidationException):
            raise
        except Exception as e:
            self.logger.error(f"Update global base URL failed: {str(e)}")
            raise
