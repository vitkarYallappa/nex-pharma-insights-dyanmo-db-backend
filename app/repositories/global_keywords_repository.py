"""
Global Keywords Repository - Uses simplified base repository with only 4 methods
Follows the same pattern as ProjectRepository for consistency
"""

from typing import List, Optional, Dict, Any
from app.repositories.base_repository import BaseRepository
from app.models.global_keywords_model import GlobalKeywordsModel

class GlobalKeywordsRepository(BaseRepository):
    """Global keywords repository with 4 essential methods"""
    
    def __init__(self):
        super().__init__(GlobalKeywordsModel.table_name())
    
    async def create(self, keyword_model: GlobalKeywordsModel) -> GlobalKeywordsModel:
        """Create a new global keyword"""
        keyword_data = keyword_model.to_dict()
        created_data = await super().create(keyword_data)
        return GlobalKeywordsModel.from_dict(created_data)
    
    async def find_one_by_query(self, query: Dict[str, Any]) -> Optional[GlobalKeywordsModel]:
        """Find global keyword by query"""
        keyword_data = await super().find_one_by_query(query)
        return GlobalKeywordsModel.from_dict(keyword_data) if keyword_data else None
    
    async def find_all_by_query(self, query: Optional[Dict[str, Any]] = None, limit: Optional[int] = None) -> List[GlobalKeywordsModel]:
        """Get all global keywords with optional filters"""
        keywords_data = await super().find_all_by_query(query, limit)
        return [GlobalKeywordsModel.from_dict(data) for data in keywords_data]
    
    async def get_all_global_keyword(self, keyword_type: Optional[str] = None,
                              limit: Optional[int] = None) -> List[GlobalKeywordsModel]:
        """Get all global keywords with optional filters"""
        query = {}
        
        if keyword_type:
            query["keyword_type"] = keyword_type
            
        return await self.find_all_by_query(query if query else None, limit)
    
    async def update_global_keyword(self, keyword_id: str, update_data: Dict[str, Any]) -> Optional[GlobalKeywordsModel]:
        """Update global keyword by ID"""
        updated_data = await super().update_by_query({"pk": keyword_id}, update_data)
        return GlobalKeywordsModel.from_dict(updated_data) if updated_data else None 