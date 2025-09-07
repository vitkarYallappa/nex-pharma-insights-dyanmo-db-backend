"""
Content Summary Repository - Uses simplified base repository with only 4 methods
Follows the same pattern as ProjectRepository for consistency
"""

from typing import List, Optional, Dict, Any
from app.repositories.base_repository import BaseRepository
from app.models.content_summary_model import ContentSummaryModel

class ContentSummaryRepository(BaseRepository):
    """Content summary repository with 4 essential methods"""
    
    def __init__(self):
        super().__init__(ContentSummaryModel.table_name())
    
    async def create(self, summary_model: ContentSummaryModel) -> ContentSummaryModel:
        """Create a new content summary entry"""
        summary_data = summary_model.to_dict()
        created_data = await super().create(summary_data)
        return ContentSummaryModel.from_dict(created_data)
    
    async def find_one_by_query(self, query: Dict[str, Any]) -> Optional[ContentSummaryModel]:
        """Find content summary entry by query"""
        summary_data = await super().find_one_by_query(query)
        return ContentSummaryModel.from_dict(summary_data) if summary_data else None
    
    async def find_all_by_query(self, query: Optional[Dict[str, Any]] = None, limit: Optional[int] = None) -> List[ContentSummaryModel]:
        """Get all content summary entries with optional filters"""
        summaries_data = await super().find_all_by_query(query, limit)
        return [ContentSummaryModel.from_dict(data) for data in summaries_data]
    
    async def get_all_projects(self, url_id: Optional[str] = None,
                              content_id: Optional[str] = None,
                              is_canonical: Optional[bool] = None,
                              preferred_choice: Optional[bool] = None,
                              version: Optional[int] = None,
                              created_by: Optional[str] = None,
                              limit: Optional[int] = None) -> List[ContentSummaryModel]:
        """Get all content summary entries with optional filters"""
        query = {}
        
        if url_id:
            query["url_id"] = url_id
        if content_id:
            query["content_id"] = content_id
        if is_canonical is not None:
            query["is_canonical"] = is_canonical
        if preferred_choice is not None:
            query["preferred_choice"] = preferred_choice
        if version is not None:
            query["version"] = version
        if created_by:
            query["created_by"] = created_by
            
        return await self.find_all_by_query(query if query else None, limit)
    
    async def update_project(self, summary_id: str, update_data: Dict[str, Any]) -> Optional[ContentSummaryModel]:
        """Update content summary entry by ID"""
        updated_data = await super().update_by_query({"pk": summary_id}, update_data)
        return ContentSummaryModel.from_dict(updated_data) if updated_data else None 