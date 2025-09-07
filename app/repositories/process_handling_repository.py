"""
Process Handling Repository - Uses simplified base repository with only 4 methods
Follows the same pattern as ProjectRepository for consistency
"""

from typing import List, Optional, Dict, Any
from app.repositories.base_repository import BaseRepository
from app.models.process_handling_model import ProcessHandlingModel

class ProcessHandlingRepository(BaseRepository):
    """Process handling repository with 4 essential methods"""
    
    def __init__(self):
        super().__init__(ProcessHandlingModel.table_name())
    
    async def create(self, process_model: ProcessHandlingModel) -> ProcessHandlingModel:
        """Create a new process handling entry"""
        process_data = process_model.to_dict()
        created_data = await super().create(process_data)
        return ProcessHandlingModel.from_dict(created_data)
    
    async def find_one_by_query(self, query: Dict[str, Any]) -> Optional[ProcessHandlingModel]:
        """Find process handling entry by query"""
        process_data = await super().find_one_by_query(query)
        return ProcessHandlingModel.from_dict(process_data) if process_data else None
    
    async def find_all_by_query(self, query: Optional[Dict[str, Any]] = None, limit: Optional[int] = None) -> List[ProcessHandlingModel]:
        """Get all process handling entries with optional filters"""
        processes_data = await super().find_all_by_query(query, limit)
        return [ProcessHandlingModel.from_dict(data) for data in processes_data]
    
    async def get_all_projects(self, request_id: Optional[str] = None, 
                              project_id: Optional[str] = None,
                              status: Optional[str] = None,
                              assigned_worker: Optional[str] = None,
                              priority: Optional[int] = None,
                              limit: Optional[int] = None) -> List[ProcessHandlingModel]:
        """Get all process handling entries with optional filters"""
        query = {}
        
        if request_id:
            query["request_id"] = request_id
        if project_id:
            query["project_id"] = project_id
        if status:
            query["status"] = status
        if assigned_worker:
            query["assigned_worker"] = assigned_worker
        if priority is not None:
            query["priority"] = priority
            
        return await self.find_all_by_query(query if query else None, limit)
    
    async def update_project(self, process_id: str, update_data: Dict[str, Any]) -> Optional[ProcessHandlingModel]:
        """Update process handling entry by ID"""
        updated_data = await super().update_by_query({"pk": process_id}, update_data)
        return ProcessHandlingModel.from_dict(updated_data) if updated_data else None 