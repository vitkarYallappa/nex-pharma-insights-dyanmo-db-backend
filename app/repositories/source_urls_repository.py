"""
Source URLs Repository - Uses simplified base repository with only 4 methods
Follows the same pattern as ProjectRepository for consistency
"""

from typing import List, Optional, Dict, Any
from app.repositories.base_repository import BaseRepository
from app.models.source_urls_model import SourceUrlsModel

class SourceUrlsRepository(BaseRepository):
    """Source URLs repository with 4 essential methods"""
    
    def __init__(self):
        super().__init__(SourceUrlsModel.table_name())
    
    async def create(self, url_model: SourceUrlsModel) -> SourceUrlsModel:
        """Create a new source URL"""
        url_data = url_model.to_dict()
        created_data = await super().create(url_data)
        return SourceUrlsModel.from_dict(created_data)
    
    async def find_one_by_query(self, query: Dict[str, Any]) -> Optional[SourceUrlsModel]:
        """Find source URL by query"""
        url_data = await super().find_one_by_query(query)
        return SourceUrlsModel.from_dict(url_data) if url_data else None
    
    async def find_all_by_query(self, query: Optional[Dict[str, Any]] = None, limit: Optional[int] = None) -> List[SourceUrlsModel]:
        """Get all source URLs with optional filters"""
        urls_data = await super().find_all_by_query(query, limit)
        return [SourceUrlsModel.from_dict(data) for data in urls_data]
    
    async def get_all_projects(self, request_id: Optional[str] = None, 
                              source_name: Optional[str] = None,
                              source_type: Optional[str] = None,
                              country_region: Optional[str] = None,
                              is_active: Optional[bool] = None,
                              limit: Optional[int] = None) -> List[SourceUrlsModel]:
        """Get all source URLs with optional filters"""
        query = {}
        
        if request_id:
            query["request_id"] = request_id
        if source_name:
            query["source_name"] = source_name
        if source_type:
            query["source_type"] = source_type
        if country_region:
            query["country_region"] = country_region
        if is_active is not None:
            query["is_active"] = is_active
            
        return await self.find_all_by_query(query if query else None, limit)
    
    async def update_project(self, url_id: str, update_data: Dict[str, Any]) -> Optional[SourceUrlsModel]:
        """Update source URL by ID"""
        updated_data = await super().update_by_query({"pk": url_id}, update_data)
        return SourceUrlsModel.from_dict(updated_data) if updated_data else None 