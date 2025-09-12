"""
Content Repository Metadata Service - Works with ContentRepositoryMetadataModel and ContentRepositoryMetadataRepository
Follows the same pattern as ContentRepositoryService for consistency
"""

from typing import List, Optional, Dict, Any
from app.repositories.content_repository_metadata_repository import ContentRepositoryMetadataRepository
from app.models.content_repository_metadata_model import ContentRepositoryMetadataModel
from app.core.logging import get_logger
from app.core.exceptions import (
    ValidationException
)

logger = get_logger("content_repository_metadata_service")

class ContentRepositoryMetadataNotFoundException(Exception):
    """Exception raised when content repository metadata entry is not found"""
    pass

class ContentRepositoryMetadataAlreadyExistsException(Exception):
    """Exception raised when content repository metadata entry already exists"""
    pass

class ContentRepositoryMetadataService:
    """Content repository metadata service with essential operations"""
    
    def __init__(self):
        self.metadata_repository = ContentRepositoryMetadataRepository()
        self.logger = logger
    
    async def create_metadata(self, content_id: str, request_id: str, project_id: str,
                            metadata_type: str, metadata_key: str, metadata_value: str,
                            data_type: str, is_searchable: Optional[bool] = None) -> ContentRepositoryMetadataModel:
        """Create a new content repository metadata entry"""
        try:
            # Validate required fields
            if not content_id or not content_id.strip():
                raise ValidationException("Content ID is required")
            
            if not request_id or not request_id.strip():
                raise ValidationException("Request ID is required")
            
            if not project_id or not project_id.strip():
                raise ValidationException("Project ID is required")
            
            if not metadata_type or not metadata_type.strip():
                raise ValidationException("Metadata type is required")
            
            if not metadata_key or not metadata_key.strip():
                raise ValidationException("Metadata key is required")
            
            if not metadata_value or not metadata_value.strip():
                raise ValidationException("Metadata value is required")
            
            if not data_type or not data_type.strip():
                raise ValidationException("Data type is required")
            
            # Validate data type
            valid_data_types = ["string", "number", "boolean", "json"]
            if data_type.strip().lower() not in valid_data_types:
                raise ValidationException(f"Data type must be one of: {', '.join(valid_data_types)}")
            
            # Check if metadata already exists for this content and key
            existing_metadata = await self.metadata_repository.get_metadata_by_content_and_key(
                content_id.strip(), metadata_key.strip()
            )
            if existing_metadata:
                raise ContentRepositoryMetadataAlreadyExistsException(
                    f"Metadata with key '{metadata_key}' already exists for content '{content_id}'"
                )
            
            # Create metadata model
            metadata_model = ContentRepositoryMetadataModel.create_new(
                content_id=content_id.strip(),
                request_id=request_id.strip(),
                project_id=project_id.strip(),
                metadata_type=metadata_type.strip(),
                metadata_key=metadata_key.strip(),
                metadata_value=metadata_value.strip(),
                data_type=data_type.strip().lower(),
                is_searchable=is_searchable
            )
            
            # Save to database
            created_metadata = await self.metadata_repository.create(metadata_model)
            self.logger.info(f"Content repository metadata created: {metadata_key} for content {content_id}")
            return created_metadata
            
        except (ValidationException, ContentRepositoryMetadataAlreadyExistsException):
            raise
        except Exception as e:
            self.logger.error(f"Create content repository metadata failed: {str(e)}")
            raise
    
    async def get_metadata_by_id(self, metadata_id: str) -> ContentRepositoryMetadataModel:
        """Get content repository metadata entry by ID"""
        try:
            if not metadata_id or not metadata_id.strip():
                raise ValidationException("Metadata ID is required")
            
            metadata = await self.metadata_repository.find_one_by_query({"pk": metadata_id.strip()})
            if not metadata:
                raise ContentRepositoryMetadataNotFoundException(f"Metadata entry with ID {metadata_id} not found")
            
            return metadata
            
        except (ContentRepositoryMetadataNotFoundException, ValidationException):
            raise
        except Exception as e:
            self.logger.error(f"Get metadata by ID failed: {str(e)}")
            raise
    
    async def get_metadata_by_content_id(self, content_id: str, 
                                       metadata_type: Optional[str] = None,
                                       is_searchable: Optional[bool] = None,
                                       limit: Optional[int] = None) -> List[ContentRepositoryMetadataModel]:
        """Get all metadata entries for a specific content ID"""
        try:
            if not content_id or not content_id.strip():
                raise ValidationException("Content ID is required")
            
            # Validate limit
            if limit is not None and limit <= 0:
                raise ValidationException("Limit must be a positive number")
            
            metadata_entries = await self.metadata_repository.get_all_metadata(
                content_id=content_id.strip(),
                metadata_type=metadata_type.strip() if metadata_type else None,
                is_searchable=is_searchable,
                limit=limit
            )
            
            self.logger.info(f"Retrieved {len(metadata_entries)} metadata entries for content {content_id}")
            return metadata_entries
            
        except ValidationException:
            raise
        except Exception as e:
            self.logger.error(f"Get metadata by content ID failed: {str(e)}")
            raise
    
    async def get_metadata_by_content_and_key(self, content_id: str, metadata_key: str) -> Optional[ContentRepositoryMetadataModel]:
        """Get specific metadata by content ID and metadata key"""
        try:
            if not content_id or not content_id.strip():
                raise ValidationException("Content ID is required")
            
            if not metadata_key or not metadata_key.strip():
                raise ValidationException("Metadata key is required")
            
            metadata = await self.metadata_repository.get_metadata_by_content_and_key(
                content_id.strip(), metadata_key.strip()
            )
            
            return metadata
            
        except ValidationException:
            raise
        except Exception as e:
            self.logger.error(f"Get metadata by content and key failed: {str(e)}")
            raise
    
    async def update_metadata(self, metadata_id: str, update_data: Dict[str, Any]) -> ContentRepositoryMetadataModel:
        """Update content repository metadata entry by ID"""
        try:
            if not metadata_id or not metadata_id.strip():
                raise ValidationException("Metadata ID is required")
            
            # Check if metadata exists
            existing_metadata = await self.get_metadata_by_id(metadata_id)
            
            # Validate data type if provided
            if 'data_type' in update_data and update_data['data_type']:
                valid_data_types = ["string", "number", "boolean", "json"]
                if update_data['data_type'].strip().lower() not in valid_data_types:
                    raise ValidationException(f"Data type must be one of: {', '.join(valid_data_types)}")
                update_data['data_type'] = update_data['data_type'].strip().lower()
            
            # Prepare update data (remove None values and add updated_at)
            clean_update_data = {k: v for k, v in update_data.items() if v is not None}
            if clean_update_data:
                from datetime import datetime
                clean_update_data["updated_at"] = datetime.utcnow().isoformat()
            
            updated_metadata = await self.metadata_repository.update_metadata(
                metadata_id.strip(), clean_update_data
            )
            
            if not updated_metadata:
                raise ContentRepositoryMetadataNotFoundException(f"Failed to update metadata entry with ID {metadata_id}")
            
            self.logger.info(f"Metadata entry updated: {metadata_id}")
            return updated_metadata
            
        except (ContentRepositoryMetadataNotFoundException, ValidationException):
            raise
        except Exception as e:
            self.logger.error(f"Update metadata entry failed: {str(e)}")
            raise
    
    async def get_all_metadata(self, content_id: Optional[str] = None,
                             request_id: Optional[str] = None,
                             project_id: Optional[str] = None,
                             metadata_type: Optional[str] = None,
                             is_searchable: Optional[bool] = None,
                             limit: Optional[int] = None) -> List[ContentRepositoryMetadataModel]:
        """Get all metadata entries with optional filters"""
        try:
            # Validate limit
            if limit is not None and limit <= 0:
                raise ValidationException("Limit must be a positive number")
            
            metadata_entries = await self.metadata_repository.get_all_metadata(
                content_id=content_id.strip() if content_id else None,
                request_id=request_id.strip() if request_id else None,
                project_id=project_id.strip() if project_id else None,
                metadata_type=metadata_type.strip() if metadata_type else None,
                is_searchable=is_searchable,
                limit=limit
            )
            
            self.logger.info(f"Retrieved {len(metadata_entries)} metadata entries with filters")
            return metadata_entries
            
        except ValidationException:
            raise
        except Exception as e:
            self.logger.error(f"Get all metadata entries failed: {str(e)}")
            raise
    
    async def get_searchable_metadata(self, content_id: Optional[str] = None,
                                    project_id: Optional[str] = None,
                                    limit: Optional[int] = None) -> List[ContentRepositoryMetadataModel]:
        """Get all searchable metadata entries"""
        try:
            # Validate limit
            if limit is not None and limit <= 0:
                raise ValidationException("Limit must be a positive number")
            
            metadata_entries = await self.metadata_repository.get_searchable_metadata(
                content_id=content_id.strip() if content_id else None,
                project_id=project_id.strip() if project_id else None,
                limit=limit
            )
            
            self.logger.info(f"Retrieved {len(metadata_entries)} searchable metadata entries")
            return metadata_entries
            
        except ValidationException:
            raise
        except Exception as e:
            self.logger.error(f"Get searchable metadata entries failed: {str(e)}")
            raise
    
    async def upsert_metadata(self, content_id: str, request_id: str, project_id: str,
                            metadata_type: str, metadata_key: str, metadata_value: str,
                            data_type: str, is_searchable: Optional[bool] = None) -> ContentRepositoryMetadataModel:
        """Create or update metadata entry (upsert operation)"""
        try:
            # Check if metadata already exists
            existing_metadata = await self.get_metadata_by_content_and_key(content_id, metadata_key)
            
            if existing_metadata:
                # Update existing metadata
                update_data = {
                    "metadata_value": metadata_value,
                    "data_type": data_type,
                    "metadata_type": metadata_type
                }
                if is_searchable is not None:
                    update_data["is_searchable"] = is_searchable
                
                return await self.update_metadata(existing_metadata.pk, update_data)
            else:
                # Create new metadata
                return await self.create_metadata(
                    content_id=content_id,
                    request_id=request_id,
                    project_id=project_id,
                    metadata_type=metadata_type,
                    metadata_key=metadata_key,
                    metadata_value=metadata_value,
                    data_type=data_type,
                    is_searchable=is_searchable
                )
                
        except ValidationException:
            raise
        except Exception as e:
            self.logger.error(f"Upsert metadata failed: {str(e)}")
            raise 