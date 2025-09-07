"""
Insight Comment Repository - Uses simplified base repository with only 4 methods
Follows the same pattern as ProjectRepository for consistency
"""

from typing import List, Optional, Dict, Any
from app.repositories.base_repository import BaseRepository
from app.models.insight_comment_model import InsightCommentModel

class InsightCommentRepository(BaseRepository):
    """Insight comment repository with 4 essential methods"""
    
    def __init__(self):
        super().__init__(InsightCommentModel.table_name())
    
    async def create(self, comment_model: InsightCommentModel) -> InsightCommentModel:
        """Create a new insight comment entry"""
        comment_data = comment_model.to_dict()
        created_data = await super().create(comment_data)
        return InsightCommentModel.from_dict(created_data)
    
    async def find_one_by_query(self, query: Dict[str, Any]) -> Optional[InsightCommentModel]:
        """Find insight comment entry by query"""
        comment_data = await super().find_one_by_query(query)
        return InsightCommentModel.from_dict(comment_data) if comment_data else None
    
    async def find_all_by_query(self, query: Optional[Dict[str, Any]] = None, limit: Optional[int] = None) -> List[InsightCommentModel]:
        """Get all insight comment entries with optional filters"""
        comments_data = await super().find_all_by_query(query, limit)
        return [InsightCommentModel.from_dict(data) for data in comments_data]
    
    async def get_all_insight_comment(self, insight_id: Optional[str] = None,
                              comment_type: Optional[str] = None,
                              limit: Optional[int] = None) -> List[InsightCommentModel]:
        """Get all insight comment entries with optional filters"""
        query = {}
        
        if insight_id:
            query["insight_id"] = insight_id
        if comment_type:
            query["comment_type"] = comment_type
            
        return await self.find_all_by_query(query if query else None, limit)
    
    async def update_insight_comment(self, comment_id: str, update_data: Dict[str, Any]) -> Optional[InsightCommentModel]:
        """Update insight comment entry by ID"""
        updated_data = await super().update_by_query({"pk": comment_id}, update_data)
        return InsightCommentModel.from_dict(updated_data) if updated_data else None 