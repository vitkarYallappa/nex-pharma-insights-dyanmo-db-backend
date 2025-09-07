"""
Content Implication Repository - Uses simplified base repository with only 4 methods
Follows the same pattern as ProjectRepository for consistency
"""

from typing import List, Optional, Dict, Any
from app.repositories.base_repository import BaseRepository
from app.models.content_implication_model import ContentImplicationModel

class ContentImplicationRepository(BaseRepository):
    """Content implication repository with 4 essential methods"""
    
    def __init__(self):
        super().__init__(ContentImplicationModel.table_name())
    
    async def create(self, implication_model: ContentImplicationModel) -> ContentImplicationModel:
        """Create a new content implication entry"""
        implication_data = implication_model.to_dict()
        created_data = await super().create(implication_data)
        return ContentImplicationModel.from_dict(created_data)
    
    async def find_one_by_query(self, query: Dict[str, Any]) -> Optional[ContentImplicationModel]:
        """Find content implication entry by query"""
        implication_data = await super().find_one_by_query(query)
        return ContentImplicationModel.from_dict(implication_data) if implication_data else None
    
    async def find_all_by_query(self, query: Optional[Dict[str, Any]] = None, limit: Optional[int] = None) -> List[ContentImplicationModel]:
        """Get all content implication entries with optional filters"""
        implications_data = await super().find_all_by_query(query, limit)
        return [ContentImplicationModel.from_dict(data) for data in implications_data]
    
    async def get_all_content_implication(self, url_id: Optional[str] = None,
                              content_id: Optional[str] = None,
                              implication_type: Optional[str] = None,
                              priority_level: Optional[str] = None,
                              is_canonical: Optional[bool] = None,
                              preferred_choice: Optional[bool] = None,
                              version: Optional[int] = None,
                              created_by: Optional[str] = None,
                              limit: Optional[int] = None) -> List[ContentImplicationModel]:
        """Get all content implication entries with optional filters"""
        query = {}
        
        if url_id:
            query["url_id"] = url_id
        if content_id:
            query["content_id"] = content_id
        if implication_type:
            query["implication_type"] = implication_type
        if priority_level:
            query["priority_level"] = priority_level
        if is_canonical is not None:
            query["is_canonical"] = is_canonical
        if preferred_choice is not None:
            query["preferred_choice"] = preferred_choice
        if version is not None:
            query["version"] = version
        if created_by:
            query["created_by"] = created_by
            
        return await self.find_all_by_query(query if query else None, limit)
    
    async def update_content_implication(self, implication_id: str, update_data: Dict[str, Any]) -> Optional[ContentImplicationModel]:
        """Update content implication entry by ID"""
        updated_data = await super().update_by_query({"pk": implication_id}, update_data)
        return ContentImplicationModel.from_dict(updated_data) if updated_data else None 