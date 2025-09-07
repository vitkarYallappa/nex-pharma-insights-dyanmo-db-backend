"""
Content URL Mapping Repository - Uses simplified base repository with only 4 methods
Follows the same pattern as ProjectRepository for consistency
"""

from typing import List, Optional, Dict, Any
from app.repositories.base_repository import BaseRepository
from app.models.content_url_mapping_model import ContentUrlMappingModel

class ContentUrlMappingRepository(BaseRepository):
    """Content URL mapping repository with 4 essential methods"""
    
    def __init__(self):
        super().__init__(ContentUrlMappingModel.table_name())
    
    async def create(self, mapping_model: ContentUrlMappingModel) -> ContentUrlMappingModel:
        """Create a new content URL mapping entry"""
        mapping_data = mapping_model.to_dict()
        created_data = await super().create(mapping_data)
        return ContentUrlMappingModel.from_dict(created_data)
    
    async def find_one_by_query(self, query: Dict[str, Any]) -> Optional[ContentUrlMappingModel]:
        """Find content URL mapping entry by query"""
        mapping_data = await super().find_one_by_query(query)
        return ContentUrlMappingModel.from_dict(mapping_data) if mapping_data else None
    
    async def find_all_by_query(self, query: Optional[Dict[str, Any]] = None, limit: Optional[int] = None) -> List[ContentUrlMappingModel]:
        """Get all content URL mapping entries with optional filters"""
        mappings_data = await super().find_all_by_query(query, limit)
        return [ContentUrlMappingModel.from_dict(data) for data in mappings_data]
    
    async def get_all_content_url_mapping(self, content_id: Optional[str] = None,
                              source_domain: Optional[str] = None,
                              is_canonical: Optional[bool] = None,
                              dedup_method: Optional[str] = None,
                              limit: Optional[int] = None) -> List[ContentUrlMappingModel]:
        """Get all content URL mapping entries with optional filters"""
        query = {}
        
        if content_id:
            query["content_id"] = content_id
        if source_domain:
            query["source_domain"] = source_domain
        if is_canonical is not None:
            query["is_canonical"] = is_canonical
        if dedup_method:
            query["dedup_method"] = dedup_method
            
        return await self.find_all_by_query(query if query else None, limit)
    
    async def update_content_url_mapping(self, url_id: str, update_data: Dict[str, Any]) -> Optional[ContentUrlMappingModel]:
        """Update content URL mapping entry by ID"""
        updated_data = await super().update_by_query({"pk": url_id}, update_data)
        return ContentUrlMappingModel.from_dict(updated_data) if updated_data else None 