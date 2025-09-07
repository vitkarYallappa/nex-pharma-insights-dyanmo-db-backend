"""
Content Analysis Mapping Repository - Uses simplified base repository with only 4 methods
Follows the same pattern as ProjectRepository for consistency
"""

from typing import List, Optional, Dict, Any
from app.repositories.base_repository import BaseRepository
from app.models.content_analysis_mapping_model import ContentAnalysisMappingModel

class ContentAnalysisMappingRepository(BaseRepository):
    """Content analysis mapping repository with 4 essential methods"""
    
    def __init__(self):
        super().__init__(ContentAnalysisMappingModel.table_name())
    
    async def create(self, mapping_model: ContentAnalysisMappingModel) -> ContentAnalysisMappingModel:
        """Create a new content analysis mapping entry"""
        mapping_data = mapping_model.to_dict()
        created_data = await super().create(mapping_data)
        return ContentAnalysisMappingModel.from_dict(created_data)
    
    async def find_one_by_query(self, query: Dict[str, Any]) -> Optional[ContentAnalysisMappingModel]:
        """Find content analysis mapping entry by query"""
        mapping_data = await super().find_one_by_query(query)
        return ContentAnalysisMappingModel.from_dict(mapping_data) if mapping_data else None
    
    async def find_all_by_query(self, query: Optional[Dict[str, Any]] = None, limit: Optional[int] = None) -> List[ContentAnalysisMappingModel]:
        """Get all content analysis mapping entries with optional filters"""
        mappings_data = await super().find_all_by_query(query, limit)
        return [ContentAnalysisMappingModel.from_dict(data) for data in mappings_data]
    
    async def get_all_projects(self, content_id: Optional[str] = None,
                              primary_summary_id: Optional[str] = None,
                              primary_insight_id: Optional[str] = None,
                              primary_implication_id: Optional[str] = None,
                              selection_strategy: Optional[str] = None,
                              selection_context: Optional[str] = None,
                              selected_by: Optional[str] = None,
                              version: Optional[int] = None,
                              is_current: Optional[bool] = None,
                              limit: Optional[int] = None) -> List[ContentAnalysisMappingModel]:
        """Get all content analysis mapping entries with optional filters"""
        query = {}
        
        if content_id:
            query["content_id"] = content_id
        if primary_summary_id:
            query["primary_summary_id"] = primary_summary_id
        if primary_insight_id:
            query["primary_insight_id"] = primary_insight_id
        if primary_implication_id:
            query["primary_implication_id"] = primary_implication_id
        if selection_strategy:
            query["selection_strategy"] = selection_strategy
        if selection_context:
            query["selection_context"] = selection_context
        if selected_by:
            query["selected_by"] = selected_by
        if version is not None:
            query["version"] = version
        if is_current is not None:
            query["is_current"] = is_current
            
        return await self.find_all_by_query(query if query else None, limit)
    
    async def update_project(self, mapping_id: str, update_data: Dict[str, Any]) -> Optional[ContentAnalysisMappingModel]:
        """Update content analysis mapping entry by ID"""
        updated_data = await super().update_by_query({"pk": mapping_id}, update_data)
        return ContentAnalysisMappingModel.from_dict(updated_data) if updated_data else None 