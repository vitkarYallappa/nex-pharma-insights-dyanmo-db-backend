"""
Project Repository - Uses simplified base repository with only 4 methods
Follows the same pattern as UserRepository for consistency
"""

from typing import List, Optional, Dict, Any
from app.repositories.base_repository import BaseRepository
from app.models.project_model import ProjectModel

class ProjectRepository(BaseRepository):
    """Project repository with 4 essential methods"""
    
    def __init__(self):
        super().__init__(ProjectModel.table_name())
    
    async def create(self, project_model: ProjectModel) -> ProjectModel:
        """Create a new project"""
        project_data = project_model.to_dict()
        created_data = await super().create(project_data)
        return ProjectModel.from_dict(created_data)
    
    async def find_one_by_query(self, query: Dict[str, Any]) -> Optional[ProjectModel]:
        """Find project by query"""
        project_data = await super().find_one_by_query(query)
        return ProjectModel.from_dict(project_data) if project_data else None
    
    async def find_all_by_query(self, query: Optional[Dict[str, Any]] = None, limit: Optional[int] = None) -> List[ProjectModel]:
        """Get all projects with optional filters"""
        projects_data = await super().find_all_by_query(query, limit)
        return [ProjectModel.from_dict(project_data) for project_data in projects_data]
    
    async def get_all_projects(self, status: Optional[str] = None, 
                              created_by: Optional[str] = None, 
                              limit: Optional[int] = None) -> List[ProjectModel]:
        """Get all projects with optional filters"""
        query = {}
        
        if status:
            query["status"] = status
        if created_by:
            query["created_by"] = created_by
            
        return await self.find_all_by_query(query if query else None, limit)
    
    async def update_project(self, project_id: str, update_data: Dict[str, Any]) -> Optional[ProjectModel]:
        """Update project by ID"""
        updated_data = await super().update_by_query({"pk": project_id}, update_data)
        return ProjectModel.from_dict(updated_data) if updated_data else None 