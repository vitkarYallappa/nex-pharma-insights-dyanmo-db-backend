"""
Keywords Repository - Uses simplified base repository with only 4 methods
Follows the same pattern as ProjectRepository for consistency
"""

from typing import List, Optional, Dict, Any
from app.repositories.base_repository import BaseRepository
from app.models.keywords_model import KeywordsModel

class KeywordsRepository(BaseRepository):
    """Keywords repository with 4 essential methods"""
    
    def __init__(self):
        super().__init__(KeywordsModel.table_name())
    
    async def create(self, keyword_model: KeywordsModel) -> KeywordsModel:
        """Create a new keyword"""
        keyword_data = keyword_model.to_dict()
        created_data = await super().create(keyword_data)
        return KeywordsModel.from_dict(created_data)
    
    async def find_one_by_query(self, query: Dict[str, Any]) -> Optional[KeywordsModel]:
        """Find keyword by query"""
        keyword_data = await super().find_one_by_query(query)
        return KeywordsModel.from_dict(keyword_data) if keyword_data else None
    
    async def find_all_by_query(self, query: Optional[Dict[str, Any]] = None, limit: Optional[int] = None) -> List[KeywordsModel]:
        """Get all keywords with optional filters"""
        keywords_data = await super().find_all_by_query(query, limit)
        return [KeywordsModel.from_dict(data) for data in keywords_data]
    
    async def get_all_keyword(self, request_id: Optional[str] = None,
                              keyword_type: Optional[str] = None,
                              limit: Optional[int] = None) -> List[KeywordsModel]:
        """Get all keywords with optional filters"""
        query = {}
        
        if request_id:
            query["request_id"] = request_id
        if keyword_type:
            query["keyword_type"] = keyword_type
            
        return await self.find_all_by_query(query if query else None, limit)
    
    async def update_keyword(self, keyword_id: str, update_data: Dict[str, Any]) -> Optional[KeywordsModel]:
        """Update keyword by ID"""
        updated_data = await super().update_by_query({"pk": keyword_id}, update_data)
        return KeywordsModel.from_dict(updated_data) if updated_data else None 