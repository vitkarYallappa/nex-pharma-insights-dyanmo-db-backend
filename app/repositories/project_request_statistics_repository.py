"""
Project Request Statistics Repository - Uses simplified base repository with only 4 methods
Follows the same pattern as ProjectRepository for consistency
"""

from typing import List, Optional, Dict, Any
from app.repositories.base_repository import BaseRepository
from app.models.project_request_statistics_model import ProjectRequestStatisticsModel

class ProjectRequestStatisticsRepository(BaseRepository):
    """Project request statistics repository with 4 essential methods"""
    
    def __init__(self):
        super().__init__(ProjectRequestStatisticsModel.table_name())
    
    async def create(self, statistics_model: ProjectRequestStatisticsModel) -> ProjectRequestStatisticsModel:
        """Create a new project request statistics"""
        statistics_data = statistics_model.to_dict()
        created_data = await super().create(statistics_data)
        return ProjectRequestStatisticsModel.from_dict(created_data)
    
    async def find_one_by_query(self, query: Dict[str, Any]) -> Optional[ProjectRequestStatisticsModel]:
        """Find project request statistics by query"""
        statistics_data = await super().find_one_by_query(query)
        return ProjectRequestStatisticsModel.from_dict(statistics_data) if statistics_data else None
    
    async def find_all_by_query(self, query: Optional[Dict[str, Any]] = None, limit: Optional[int] = None) -> List[ProjectRequestStatisticsModel]:
        """Get all project request statistics with optional filters"""
        statistics_data = await super().find_all_by_query(query, limit)
        return [ProjectRequestStatisticsModel.from_dict(data) for data in statistics_data]
    
    async def get_all_project_request_statistics(self, project_id: Optional[str] = None,
                              limit: Optional[int] = None) -> List[ProjectRequestStatisticsModel]:
        """Get all project request statistics with optional filters"""
        query = {}
        
        if project_id:
            query["project_id"] = project_id
            
        return await self.find_all_by_query(query if query else None, limit)
    
    async def update_project_request_statistics(self, statistics_id: str, update_data: Dict[str, Any]) -> Optional[ProjectRequestStatisticsModel]:
        """Update project request statistics by ID"""
        updated_data = await super().update_by_query({"pk": statistics_id}, update_data)
        return ProjectRequestStatisticsModel.from_dict(updated_data) if updated_data else None 