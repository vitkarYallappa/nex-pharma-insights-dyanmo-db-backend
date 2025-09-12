"""
Content Repository Metadata Repository - Uses simplified base repository with only 4 methods
Follows the same pattern as ContentRepositoryRepository for consistency
"""

from typing import List, Optional, Dict, Any
from app.repositories.base_repository import BaseRepository
from app.models.content_repository_metadata_model import ContentRepositoryMetadataModel

class ContentRepositoryMetadataRepository(BaseRepository):
    """Content repository metadata repository with 4 essential methods"""
    
    def __init__(self):
        super().__init__(ContentRepositoryMetadataModel.table_name())
    
    async def create(self, metadata_model: ContentRepositoryMetadataModel) -> ContentRepositoryMetadataModel:
        """Create a new content repository metadata entry"""
        metadata_data = metadata_model.to_dict()
        created_data = await super().create(metadata_data)
        return ContentRepositoryMetadataModel.from_dict(created_data)
    
    async def find_one_by_query(self, query: Dict[str, Any]) -> Optional[ContentRepositoryMetadataModel]:
        """Find content repository metadata entry by query"""
        metadata_data = await super().find_one_by_query(query)
        return ContentRepositoryMetadataModel.from_dict(metadata_data) if metadata_data else None
    
    async def find_all_by_query(self, query: Optional[Dict[str, Any]] = None, limit: Optional[int] = None) -> List[ContentRepositoryMetadataModel]:
        """Get all content repository metadata entries with optional filters"""
        metadata_data = await super().find_all_by_query(query, limit)
        return [ContentRepositoryMetadataModel.from_dict(data) for data in metadata_data]
    
    async def get_all_metadata(self, content_id: Optional[str] = None,
                              request_id: Optional[str] = None,
                              project_id: Optional[str] = None,
                              metadata_type: Optional[str] = None,
                              metadata_key: Optional[str] = None,
                              is_searchable: Optional[bool] = None,
                              limit: Optional[int] = None) -> List[ContentRepositoryMetadataModel]:
        """Get all content repository metadata entries with optional filters"""
        query = {}
        
        if content_id:
            query["content_id"] = content_id
        if request_id:
            query["request_id"] = request_id
        if project_id:
            query["project_id"] = project_id
        if metadata_type:
            query["metadata_type"] = metadata_type
        if metadata_key:
            query["metadata_key"] = metadata_key
        if is_searchable is not None:
            query["is_searchable"] = is_searchable
            
        return await self.find_all_by_query(query if query else None, limit)
    
    async def update_metadata(self, metadata_id: str, update_data: Dict[str, Any]) -> Optional[ContentRepositoryMetadataModel]:
        """Update content repository metadata entry by ID"""
        updated_data = await super().update_by_query({"pk": metadata_id}, update_data)
        return ContentRepositoryMetadataModel.from_dict(updated_data) if updated_data else None
    
    async def get_metadata_by_content_and_key(self, content_id: str, metadata_key: str) -> Optional[ContentRepositoryMetadataModel]:
        """Get specific metadata by content ID and metadata key"""
        return await self.find_one_by_query({
            "content_id": content_id,
            "metadata_key": metadata_key
        })
    
    async def get_metadata_by_type(self, content_id: str, metadata_type: str) -> List[ContentRepositoryMetadataModel]:
        """Get all metadata of a specific type for a content entry"""
        return await self.find_all_by_query({
            "content_id": content_id,
            "metadata_type": metadata_type
        })
    
    async def get_searchable_metadata(self, content_id: Optional[str] = None,
                                    project_id: Optional[str] = None,
                                    limit: Optional[int] = None) -> List[ContentRepositoryMetadataModel]:
        """Get all searchable metadata entries"""
        query = {"is_searchable": True}
        
        if content_id:
            query["content_id"] = content_id
        if project_id:
            query["project_id"] = project_id
            
        return await self.find_all_by_query(query, limit)
    
    async def exists(self, query: Dict[str, Any]) -> bool:
        """Check if metadata exists with given query"""
        result = await self.find_one_by_query(query)
        return result is not None 