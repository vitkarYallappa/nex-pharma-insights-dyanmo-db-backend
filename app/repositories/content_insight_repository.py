"""
Content Insight Repository - Uses simplified base repository with only 4 methods
Follows the same pattern as ProjectRepository for consistency
"""

from typing import List, Optional, Dict, Any
from app.repositories.base_repository import BaseRepository
from app.models.content_insight_model import ContentInsightModel

class ContentInsightRepository(BaseRepository):
    """Content insight repository with 4 essential methods"""
    
    def __init__(self):
        super().__init__(ContentInsightModel.table_name())
    
    async def create(self, insight_model: ContentInsightModel) -> ContentInsightModel:
        """Create a new content insight entry"""
        insight_data = insight_model.to_dict()
        created_data = await super().create(insight_data)
        return ContentInsightModel.from_dict(created_data)
    
    async def find_one_by_query(self, query: Dict[str, Any]) -> Optional[ContentInsightModel]:
        """Find content insight entry by query"""
        insight_data = await super().find_one_by_query(query)
        return ContentInsightModel.from_dict(insight_data) if insight_data else None
    
    async def find_all_by_query(self, query: Optional[Dict[str, Any]] = None, limit: Optional[int] = None) -> List[ContentInsightModel]:
        """Get all content insight entries with optional filters"""
        insights_data = await super().find_all_by_query(query, limit)
        return [ContentInsightModel.from_dict(data) for data in insights_data]
    
    async def get_all_content_insight(self, url_id: Optional[str] = None,
                              content_id: Optional[str] = None,
                              insight_category: Optional[str] = None,
                              is_canonical: Optional[bool] = None,
                              preferred_choice: Optional[bool] = None,
                              version: Optional[int] = None,
                              created_by: Optional[str] = None,
                              limit: Optional[int] = None) -> List[ContentInsightModel]:
        """Get all content insight entries with optional filters"""
        query = {}
        
        if url_id:
            query["url_id"] = url_id
        if content_id:
            query["content_id"] = content_id
        if insight_category:
            query["insight_category"] = insight_category
        if is_canonical is not None:
            query["is_canonical"] = is_canonical
        if preferred_choice is not None:
            query["preferred_choice"] = preferred_choice
        if version is not None:
            query["version"] = version
        if created_by:
            query["created_by"] = created_by
            
        return await self.find_all_by_query(query if query else None, limit)
    
    async def update_content_insight(self, insight_id: str, update_data: Dict[str, Any]) -> Optional[ContentInsightModel]:
        """Update content insight entry by ID"""
        updated_data = await super().update_by_query({"pk": insight_id}, update_data)
        return ContentInsightModel.from_dict(updated_data) if updated_data else None 