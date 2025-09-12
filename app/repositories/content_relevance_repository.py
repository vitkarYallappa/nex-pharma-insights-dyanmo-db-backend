"""
Content Relevance Repository - Uses simplified base repository with only 4 methods
Follows the same pattern as ContentRepositoryRepository for consistency
"""

from typing import List, Optional, Dict, Any
from app.repositories.base_repository import BaseRepository
from app.models.content_relevance_model import ContentRelevanceModel

class ContentRelevanceRepository(BaseRepository):
    """Content relevance repository with 4 essential methods"""
    
    def __init__(self):
        super().__init__(ContentRelevanceModel.table_name())
    
    async def create(self, relevance_model: ContentRelevanceModel) -> ContentRelevanceModel:
        """Create a new content relevance entry"""
        relevance_data = relevance_model.to_dict()
        created_data = await super().create(relevance_data)
        return ContentRelevanceModel.from_dict(created_data)
    
    async def find_one_by_query(self, query: Dict[str, Any]) -> Optional[ContentRelevanceModel]:
        """Find content relevance entry by query"""
        relevance_data = await super().find_one_by_query(query)
        return ContentRelevanceModel.from_dict(relevance_data) if relevance_data else None
    
    async def find_all_by_query(self, query: Optional[Dict[str, Any]] = None, limit: Optional[int] = None) -> List[ContentRelevanceModel]:
        """Get all content relevance entries with optional filters"""
        relevance_data = await super().find_all_by_query(query, limit)
        return [ContentRelevanceModel.from_dict(data) for data in relevance_data]
    
    async def get_all_relevance(self, content_id: Optional[str] = None,
                              url_id: Optional[str] = None,
                              is_relevant: Optional[bool] = None,
                              relevance_category: Optional[str] = None,
                              is_canonical: Optional[bool] = None,
                              preferred_choice: Optional[bool] = None,
                              created_by: Optional[str] = None,
                              limit: Optional[int] = None) -> List[ContentRelevanceModel]:
        """Get all content relevance entries with optional filters"""
        query = {}
        
        if content_id:
            query["content_id"] = content_id
        if url_id:
            query["url_id"] = url_id
        if is_relevant is not None:
            query["is_relevant"] = is_relevant
        if relevance_category:
            query["relevance_category"] = relevance_category
        if is_canonical is not None:
            query["is_canonical"] = is_canonical
        if preferred_choice is not None:
            query["preferred_choice"] = preferred_choice
        if created_by:
            query["created_by"] = created_by
            
        return await self.find_all_by_query(query if query else None, limit)
    
    async def update_relevance(self, relevance_id: str, update_data: Dict[str, Any]) -> Optional[ContentRelevanceModel]:
        """Update content relevance entry by ID"""
        updated_data = await super().update_by_query({"pk": relevance_id}, update_data)
        return ContentRelevanceModel.from_dict(updated_data) if updated_data else None
    
    async def get_relevance_by_content_id(self, content_id: str) -> Optional[ContentRelevanceModel]:
        """Get relevance entry by content ID"""
        return await self.find_one_by_query({"content_id": content_id})
    
    async def get_relevance_by_url_id(self, url_id: str) -> Optional[ContentRelevanceModel]:
        """Get relevance entry by URL ID"""
        return await self.find_one_by_query({"url_id": url_id})
    
    async def get_relevant_content(self, is_relevant: bool = True, 
                                 relevance_category: Optional[str] = None,
                                 min_score: Optional[float] = None,
                                 limit: Optional[int] = None) -> List[ContentRelevanceModel]:
        """Get relevant content entries with optional filters"""
        query = {"is_relevant": is_relevant}
        
        if relevance_category:
            query["relevance_category"] = relevance_category
            
        results = await self.find_all_by_query(query, limit)
        
        # Filter by minimum score if provided (client-side filtering since DynamoDB doesn't support range queries on non-key attributes easily)
        if min_score is not None:
            results = [r for r in results if r.relevance_score >= min_score]
            
        return results
    
    async def get_high_confidence_relevance(self, min_confidence: float = 0.8,
                                          is_relevant: Optional[bool] = None,
                                          limit: Optional[int] = None) -> List[ContentRelevanceModel]:
        """Get high confidence relevance entries"""
        query = {}
        if is_relevant is not None:
            query["is_relevant"] = is_relevant
            
        results = await self.find_all_by_query(query, limit)
        
        # Filter by minimum confidence (client-side filtering)
        return [r for r in results if r.confidence_score >= min_confidence]
    
    async def get_canonical_relevance(self, is_canonical: bool = True,
                                    preferred_choice: Optional[bool] = None,
                                    limit: Optional[int] = None) -> List[ContentRelevanceModel]:
        """Get canonical relevance entries"""
        query = {"is_canonical": is_canonical}
        
        if preferred_choice is not None:
            query["preferred_choice"] = preferred_choice
            
        return await self.find_all_by_query(query, limit)
    
    async def get_relevance_by_category(self, relevance_category: str,
                                      is_relevant: Optional[bool] = None,
                                      limit: Optional[int] = None) -> List[ContentRelevanceModel]:
        """Get relevance entries by category"""
        query = {"relevance_category": relevance_category}
        
        if is_relevant is not None:
            query["is_relevant"] = is_relevant
            
        return await self.find_all_by_query(query, limit)
    
    async def get_relevance_by_creator(self, created_by: str,
                                     is_relevant: Optional[bool] = None,
                                     limit: Optional[int] = None) -> List[ContentRelevanceModel]:
        """Get relevance entries by creator"""
        query = {"created_by": created_by}
        
        if is_relevant is not None:
            query["is_relevant"] = is_relevant
            
        return await self.find_all_by_query(query, limit)
    
    async def exists(self, query: Dict[str, Any]) -> bool:
        """Check if relevance entry exists with given query"""
        result = await self.find_one_by_query(query)
        return result is not None 