"""
Implication Comment Repository - Uses simplified base repository with only 4 methods
Follows the same pattern as ProjectRepository for consistency
"""

from typing import List, Optional, Dict, Any
from app.repositories.base_repository import BaseRepository
from app.models.implication_comment_model import ImplicationCommentModel

class ImplicationCommentRepository(BaseRepository):
    """Implication comment repository with 4 essential methods"""
    
    def __init__(self):
        super().__init__(ImplicationCommentModel.table_name())
    
    async def create(self, comment_model: ImplicationCommentModel) -> ImplicationCommentModel:
        """Create a new implication comment entry"""
        comment_data = comment_model.to_dict()
        created_data = await super().create(comment_data)
        return ImplicationCommentModel.from_dict(created_data)
    
    async def find_one_by_query(self, query: Dict[str, Any]) -> Optional[ImplicationCommentModel]:
        """Find implication comment entry by query"""
        comment_data = await super().find_one_by_query(query)
        return ImplicationCommentModel.from_dict(comment_data) if comment_data else None
    
    async def find_all_by_query(self, query: Optional[Dict[str, Any]] = None, limit: Optional[int] = None) -> List[ImplicationCommentModel]:
        """Get all implication comment entries with optional filters"""
        comments_data = await super().find_all_by_query(query, limit)
        return [ImplicationCommentModel.from_dict(data) for data in comments_data]
    
    async def get_all_implication_comment(self, implication_id: Optional[str] = None,
                              comment_type: Optional[str] = None,
                              limit: Optional[int] = None) -> List[ImplicationCommentModel]:
        """Get all implication comment entries with optional filters"""
        query = {}
        
        if implication_id:
            query["implication_id"] = implication_id
        if comment_type:
            query["comment_type"] = comment_type
            
        return await self.find_all_by_query(query if query else None, limit)
    
    async def update_implication_comment(self, comment_id: str, update_data: Dict[str, Any]) -> Optional[ImplicationCommentModel]:
        """Update implication comment entry by ID"""
        updated_data = await super().update_by_query({"pk": comment_id}, update_data)
        return ImplicationCommentModel.from_dict(updated_data) if updated_data else None 