"""
Implication QA Repository - Uses simplified base repository with only 4 methods
Follows the same pattern as ProjectRepository for consistency
"""

from typing import List, Optional, Dict, Any
from app.repositories.base_repository import BaseRepository
from app.models.implication_qa_model import ImplicationQaModel

class ImplicationQaRepository(BaseRepository):
    """Implication QA repository with 4 essential methods"""
    
    def __init__(self):
        super().__init__(ImplicationQaModel.table_name())
    
    async def create(self, qa_model: ImplicationQaModel) -> ImplicationQaModel:
        """Create a new implication QA entry"""
        qa_data = qa_model.to_dict()
        created_data = await super().create(qa_data)
        return ImplicationQaModel.from_dict(created_data)
    
    async def find_one_by_query(self, query: Dict[str, Any]) -> Optional[ImplicationQaModel]:
        """Find implication QA entry by query"""
        qa_data = await super().find_one_by_query(query)
        return ImplicationQaModel.from_dict(qa_data) if qa_data else None
    
    async def find_all_by_query(self, query: Optional[Dict[str, Any]] = None, limit: Optional[int] = None) -> List[ImplicationQaModel]:
        """Get all implication QA entries with optional filters"""
        qa_data_list = await super().find_all_by_query(query, limit)
        return [ImplicationQaModel.from_dict(data) for data in qa_data_list]
    
    async def get_all_projects(self, implication_id: Optional[str] = None,
                              question_type: Optional[str] = None,
                              limit: Optional[int] = None) -> List[ImplicationQaModel]:
        """Get all implication QA entries with optional filters"""
        query = {}
        
        if implication_id:
            query["implication_id"] = implication_id
        if question_type:
            query["question_type"] = question_type
            
        return await self.find_all_by_query(query if query else None, limit)
    
    async def update_project(self, qa_id: str, update_data: Dict[str, Any]) -> Optional[ImplicationQaModel]:
        """Update implication QA entry by ID"""
        updated_data = await super().update_by_query({"pk": qa_id}, update_data)
        return ImplicationQaModel.from_dict(updated_data) if updated_data else None 