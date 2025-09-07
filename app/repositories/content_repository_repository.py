"""
Content Repository Repository - Uses simplified base repository with only 4 methods
Follows the same pattern as ProjectRepository for consistency
"""

from typing import List, Optional, Dict, Any
from app.repositories.base_repository import BaseRepository
from app.models.content_repository_model import ContentRepositoryModel

class ContentRepositoryRepository(BaseRepository):
    """Content repository repository with 4 essential methods"""
    
    def __init__(self):
        super().__init__(ContentRepositoryModel.table_name())
    
    async def create(self, content_model: ContentRepositoryModel) -> ContentRepositoryModel:
        """Create a new content repository entry"""
        content_data = content_model.to_dict()
        created_data = await super().create(content_data)
        return ContentRepositoryModel.from_dict(created_data)
    
    async def find_one_by_query(self, query: Dict[str, Any]) -> Optional[ContentRepositoryModel]:
        """Find content repository entry by query"""
        content_data = await super().find_one_by_query(query)
        return ContentRepositoryModel.from_dict(content_data) if content_data else None
    
    async def find_all_by_query(self, query: Optional[Dict[str, Any]] = None, limit: Optional[int] = None) -> List[ContentRepositoryModel]:
        """Get all content repository entries with optional filters"""
        contents_data = await super().find_all_by_query(query, limit)
        return [ContentRepositoryModel.from_dict(data) for data in contents_data]
    
    async def get_all_content_repository(self, request_id: Optional[str] = None,
                              project_id: Optional[str] = None,
                              source_type: Optional[str] = None,
                              relevance_type: Optional[str] = None,
                              is_canonical: Optional[bool] = None,
                              limit: Optional[int] = None) -> List[ContentRepositoryModel]:
        """Get all content repository entries with optional filters"""
        query = {}
        
        if request_id:
            query["request_id"] = request_id
        if project_id:
            query["project_id"] = project_id
        if source_type:
            query["source_type"] = source_type
        if relevance_type:
            query["relevance_type"] = relevance_type
        if is_canonical is not None:
            query["is_canonical"] = is_canonical
            
        return await self.find_all_by_query(query if query else None, limit)
    
    async def update_content_repository(self, content_id: str, update_data: Dict[str, Any]) -> Optional[ContentRepositoryModel]:
        """Update content repository entry by ID"""
        updated_data = await super().update_by_query({"pk": content_id}, update_data)
        return ContentRepositoryModel.from_dict(updated_data) if updated_data else None 