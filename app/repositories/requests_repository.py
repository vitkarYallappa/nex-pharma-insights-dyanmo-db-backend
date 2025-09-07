"""
Requests Repository - Uses simplified base repository with only 4 methods
Follows the same pattern as ProjectRepository for consistency
"""

from typing import List, Optional, Dict, Any
from app.repositories.base_repository import BaseRepository
from app.models.requests_model import RequestsModel

class RequestsRepository(BaseRepository):
    """Requests repository with 4 essential methods"""
    
    def __init__(self):
        super().__init__(RequestsModel.table_name())
    
    async def create(self, request_model: RequestsModel) -> RequestsModel:
        """Create a new request"""
        request_data = request_model.to_dict()
        created_data = await super().create(request_data)
        return RequestsModel.from_dict(created_data)
    
    async def find_one_by_query(self, query: Dict[str, Any]) -> Optional[RequestsModel]:
        """Find request by query"""
        request_data = await super().find_one_by_query(query)
        return RequestsModel.from_dict(request_data) if request_data else None
    
    async def find_all_by_query(self, query: Optional[Dict[str, Any]] = None, limit: Optional[int] = None) -> List[RequestsModel]:
        """Get all requests with optional filters"""
        requests_data = await super().find_all_by_query(query, limit)
        return [RequestsModel.from_dict(data) for data in requests_data]
    
    async def get_all_projects(self, project_id: Optional[str] = None, 
                              status: Optional[str] = None,
                              priority: Optional[str] = None,
                              created_by: Optional[str] = None,
                              limit: Optional[int] = None) -> List[RequestsModel]:
        """Get all requests with optional filters"""
        query = {}
        
        if project_id:
            query["project_id"] = project_id
        if status:
            query["status"] = status
        if priority:
            query["priority"] = priority
        if created_by:
            query["created_by"] = created_by
            
        return await self.find_all_by_query(query if query else None, limit)
    
    async def update_project(self, request_id: str, update_data: Dict[str, Any]) -> Optional[RequestsModel]:
        """Update request by ID"""
        updated_data = await super().update_by_query({"pk": request_id}, update_data)
        return RequestsModel.from_dict(updated_data) if updated_data else None 