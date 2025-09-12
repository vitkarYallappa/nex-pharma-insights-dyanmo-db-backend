"""
Content Relevance Service - Works with ContentRelevanceModel and ContentRelevanceRepository
Follows the same pattern as ContentRepositoryService for consistency
"""

from typing import List, Optional, Dict, Any
from app.repositories.content_relevance_repository import ContentRelevanceRepository
from app.models.content_relevance_model import ContentRelevanceModel
from app.core.logging import get_logger
from app.core.exceptions import (
    ValidationException
)

logger = get_logger("content_relevance_service")

class ContentRelevanceNotFoundException(Exception):
    """Exception raised when content relevance entry is not found"""
    pass

class ContentRelevanceAlreadyExistsException(Exception):
    """Exception raised when content relevance entry already exists"""
    pass

class ContentRelevanceService:
    """Content relevance service with essential operations"""
    
    def __init__(self):
        self.relevance_repository = ContentRelevanceRepository()
        self.logger = logger
    
    async def create_relevance(self, url_id: str, content_id: str, relevance_text: str,
                             relevance_score: float, is_relevant: bool, relevance_category: str,
                             confidence_score: float, relevance_content_file_path: Optional[str] = None,
                             version: Optional[int] = None, is_canonical: Optional[bool] = None,
                             preferred_choice: Optional[bool] = None,
                             created_by: str = "system") -> ContentRelevanceModel:
        """Create a new content relevance entry"""
        try:
            # Validate required fields
            if not url_id or not url_id.strip():
                raise ValidationException("URL ID is required")
            
            if not content_id or not content_id.strip():
                raise ValidationException("Content ID is required")
            
            if not relevance_text or not relevance_text.strip():
                raise ValidationException("Relevance text is required")
            
            if not relevance_category or not relevance_category.strip():
                raise ValidationException("Relevance category is required")
            
            if not created_by or not created_by.strip():
                raise ValidationException("Created by is required")
            
            # Validate score ranges
            if not (0.0 <= relevance_score <= 1.0):
                raise ValidationException("Relevance score must be between 0.0 and 1.0")
            
            if not (0.0 <= confidence_score <= 1.0):
                raise ValidationException("Confidence score must be between 0.0 and 1.0")
            
            # Check if relevance already exists for this content
            existing_relevance = await self.relevance_repository.get_relevance_by_content_id(content_id.strip())
            if existing_relevance:
                raise ContentRelevanceAlreadyExistsException(
                    f"Relevance entry already exists for content '{content_id}'"
                )
            
            # Create relevance model
            relevance_model = ContentRelevanceModel.create_new(
                url_id=url_id.strip(),
                content_id=content_id.strip(),
                relevance_text=relevance_text.strip(),
                relevance_score=relevance_score,
                is_relevant=is_relevant,
                relevance_category=relevance_category.strip(),
                confidence_score=confidence_score,
                relevance_content_file_path=relevance_content_file_path,
                version=version,
                is_canonical=is_canonical,
                preferred_choice=preferred_choice,
                created_by=created_by.strip()
            )
            
            # Save to database
            created_relevance = await self.relevance_repository.create(relevance_model)
            self.logger.info(f"Content relevance created for content {content_id} with score {relevance_score}")
            return created_relevance
            
        except (ValidationException, ContentRelevanceAlreadyExistsException):
            raise
        except Exception as e:
            self.logger.error(f"Create content relevance failed: {str(e)}")
            raise
    
    async def get_relevance_by_id(self, relevance_id: str) -> ContentRelevanceModel:
        """Get content relevance entry by ID"""
        try:
            if not relevance_id or not relevance_id.strip():
                raise ValidationException("Relevance ID is required")
            
            relevance = await self.relevance_repository.find_one_by_query({"pk": relevance_id.strip()})
            if not relevance:
                raise ContentRelevanceNotFoundException(f"Relevance entry with ID {relevance_id} not found")
            
            return relevance
            
        except (ContentRelevanceNotFoundException, ValidationException):
            raise
        except Exception as e:
            self.logger.error(f"Get relevance by ID failed: {str(e)}")
            raise
    
    async def get_relevance_by_content_id(self, content_id: str) -> Optional[ContentRelevanceModel]:
        """Get relevance entry by content ID"""
        try:
            if not content_id or not content_id.strip():
                raise ValidationException("Content ID is required")
            
            relevance = await self.relevance_repository.get_relevance_by_content_id(content_id.strip())
            return relevance
            
        except ValidationException:
            raise
        except Exception as e:
            self.logger.error(f"Get relevance by content ID failed: {str(e)}")
            raise
    
    async def get_relevance_by_url_id(self, url_id: str) -> Optional[ContentRelevanceModel]:
        """Get relevance entry by URL ID"""
        try:
            if not url_id or not url_id.strip():
                raise ValidationException("URL ID is required")
            
            relevance = await self.relevance_repository.get_relevance_by_url_id(url_id.strip())
            return relevance
            
        except ValidationException:
            raise
        except Exception as e:
            self.logger.error(f"Get relevance by URL ID failed: {str(e)}")
            raise
    
    async def update_relevance(self, relevance_id: str, update_data: Dict[str, Any]) -> ContentRelevanceModel:
        """Update content relevance entry by ID"""
        try:
            if not relevance_id or not relevance_id.strip():
                raise ValidationException("Relevance ID is required")
            
            # Check if relevance exists
            existing_relevance = await self.get_relevance_by_id(relevance_id)
            
            # Validate score ranges if provided
            if 'relevance_score' in update_data and update_data['relevance_score'] is not None:
                if not (0.0 <= update_data['relevance_score'] <= 1.0):
                    raise ValidationException("Relevance score must be between 0.0 and 1.0")
            
            if 'confidence_score' in update_data and update_data['confidence_score'] is not None:
                if not (0.0 <= update_data['confidence_score'] <= 1.0):
                    raise ValidationException("Confidence score must be between 0.0 and 1.0")
            
            # Prepare update data (remove None values)
            clean_update_data = {k: v for k, v in update_data.items() if v is not None}
            
            updated_relevance = await self.relevance_repository.update_relevance(
                relevance_id.strip(), clean_update_data
            )
            
            if not updated_relevance:
                raise ContentRelevanceNotFoundException(f"Failed to update relevance entry with ID {relevance_id}")
            
            self.logger.info(f"Relevance entry updated: {relevance_id}")
            return updated_relevance
            
        except (ContentRelevanceNotFoundException, ValidationException):
            raise
        except Exception as e:
            self.logger.error(f"Update relevance entry failed: {str(e)}")
            raise
    
    async def update_relevance_by_content_id(self, content_id: str, is_relevant: bool, 
                                            relevance_text: Optional[str] = None,
                                            relevance_score: Optional[float] = None,
                                            confidence_score: Optional[float] = None,
                                            relevance_category: Optional[str] = None,
                                            updated_by: str = "user") -> ContentRelevanceModel:
        """Update content relevance by content ID - for user-based updates"""
        try:
            if not content_id or not content_id.strip():
                raise ValidationException("Content ID is required")
            
            # Find existing relevance by content ID
            existing_relevance = await self.get_relevance_by_content_id(content_id.strip())
            
            if not existing_relevance:
                raise ContentRelevanceNotFoundException(f"No relevance entry found for content ID {content_id}")
            
            # Prepare update data
            update_data = {
                "is_relevant": is_relevant,
                "updated_by": updated_by.strip() if updated_by else "user"
            }
            
            # Add optional fields if provided
            if relevance_text is not None:
                update_data["relevance_text"] = relevance_text.strip()
            
            if relevance_score is not None:
                if not (0.0 <= relevance_score <= 1.0):
                    raise ValidationException("Relevance score must be between 0.0 and 1.0")
                update_data["relevance_score"] = relevance_score
            
            if confidence_score is not None:
                if not (0.0 <= confidence_score <= 1.0):
                    raise ValidationException("Confidence score must be between 0.0 and 1.0")
                update_data["confidence_score"] = confidence_score
            
            if relevance_category is not None:
                update_data["relevance_category"] = relevance_category.strip()
            
            # Update the relevance entry
            updated_relevance = await self.update_relevance(existing_relevance.pk, update_data)
            
            self.logger.info(f"Content relevance updated by {updated_by} for content {content_id}: is_relevant={is_relevant}")
            return updated_relevance
            
        except (ValidationException, ContentRelevanceNotFoundException):
            raise
        except Exception as e:
            self.logger.error(f"Update relevance by content ID failed: {str(e)}")
            raise
    
    async def get_all_relevance(self, content_id: Optional[str] = None,
                              url_id: Optional[str] = None,
                              is_relevant: Optional[bool] = None,
                              relevance_category: Optional[str] = None,
                              is_canonical: Optional[bool] = None,
                              preferred_choice: Optional[bool] = None,
                              created_by: Optional[str] = None,
                              limit: Optional[int] = None) -> List[ContentRelevanceModel]:
        """Get all relevance entries with optional filters"""
        try:
            # Validate limit
            if limit is not None and limit <= 0:
                raise ValidationException("Limit must be a positive number")
            
            relevance_entries = await self.relevance_repository.get_all_relevance(
                content_id=content_id.strip() if content_id else None,
                url_id=url_id.strip() if url_id else None,
                is_relevant=is_relevant,
                relevance_category=relevance_category.strip() if relevance_category else None,
                is_canonical=is_canonical,
                preferred_choice=preferred_choice,
                created_by=created_by.strip() if created_by else None,
                limit=limit
            )
            
            self.logger.info(f"Retrieved {len(relevance_entries)} relevance entries with filters")
            return relevance_entries
            
        except ValidationException:
            raise
        except Exception as e:
            self.logger.error(f"Get all relevance entries failed: {str(e)}")
            raise
    
    async def get_relevant_content(self, is_relevant: bool = True,
                                 relevance_category: Optional[str] = None,
                                 min_score: Optional[float] = None,
                                 limit: Optional[int] = None) -> List[ContentRelevanceModel]:
        """Get relevant content entries with optional filters"""
        try:
            # Validate limit and score
            if limit is not None and limit <= 0:
                raise ValidationException("Limit must be a positive number")
            
            if min_score is not None and not (0.0 <= min_score <= 1.0):
                raise ValidationException("Minimum score must be between 0.0 and 1.0")
            
            relevance_entries = await self.relevance_repository.get_relevant_content(
                is_relevant=is_relevant,
                relevance_category=relevance_category.strip() if relevance_category else None,
                min_score=min_score,
                limit=limit
            )
            
            self.logger.info(f"Retrieved {len(relevance_entries)} relevant content entries")
            return relevance_entries
            
        except ValidationException:
            raise
        except Exception as e:
            self.logger.error(f"Get relevant content failed: {str(e)}")
            raise
    
    async def get_high_confidence_relevance(self, min_confidence: float = 0.8,
                                          is_relevant: Optional[bool] = None,
                                          limit: Optional[int] = None) -> List[ContentRelevanceModel]:
        """Get high confidence relevance entries"""
        try:
            # Validate parameters
            if not (0.0 <= min_confidence <= 1.0):
                raise ValidationException("Minimum confidence must be between 0.0 and 1.0")
            
            if limit is not None and limit <= 0:
                raise ValidationException("Limit must be a positive number")
            
            relevance_entries = await self.relevance_repository.get_high_confidence_relevance(
                min_confidence=min_confidence,
                is_relevant=is_relevant,
                limit=limit
            )
            
            self.logger.info(f"Retrieved {len(relevance_entries)} high confidence relevance entries")
            return relevance_entries
            
        except ValidationException:
            raise
        except Exception as e:
            self.logger.error(f"Get high confidence relevance failed: {str(e)}")
            raise
    
    async def get_relevance_by_category(self, relevance_category: str,
                                      is_relevant: Optional[bool] = None,
                                      limit: Optional[int] = None) -> List[ContentRelevanceModel]:
        """Get relevance entries by category"""
        try:
            if not relevance_category or not relevance_category.strip():
                raise ValidationException("Relevance category is required")
            
            if limit is not None and limit <= 0:
                raise ValidationException("Limit must be a positive number")
            
            relevance_entries = await self.relevance_repository.get_relevance_by_category(
                relevance_category=relevance_category.strip(),
                is_relevant=is_relevant,
                limit=limit
            )
            
            self.logger.info(f"Retrieved {len(relevance_entries)} relevance entries for category {relevance_category}")
            return relevance_entries
            
        except ValidationException:
            raise
        except Exception as e:
            self.logger.error(f"Get relevance by category failed: {str(e)}")
            raise
    
    async def upsert_relevance(self, url_id: str, content_id: str, relevance_text: str,
                             relevance_score: float, is_relevant: bool, relevance_category: str,
                             confidence_score: float, relevance_content_file_path: Optional[str] = None,
                             version: Optional[int] = None, is_canonical: Optional[bool] = None,
                             preferred_choice: Optional[bool] = None,
                             created_by: str = "system") -> ContentRelevanceModel:
        """Create or update relevance entry (upsert operation)"""
        try:
            # Check if relevance already exists
            existing_relevance = await self.get_relevance_by_content_id(content_id)
            
            if existing_relevance:
                # Update existing relevance
                update_data = {
                    "relevance_text": relevance_text,
                    "relevance_score": relevance_score,
                    "is_relevant": is_relevant,
                    "relevance_category": relevance_category,
                    "confidence_score": confidence_score
                }
                
                if relevance_content_file_path is not None:
                    update_data["relevance_content_file_path"] = relevance_content_file_path
                if version is not None:
                    update_data["version"] = version
                if is_canonical is not None:
                    update_data["is_canonical"] = is_canonical
                if preferred_choice is not None:
                    update_data["preferred_choice"] = preferred_choice
                
                return await self.update_relevance(existing_relevance.pk, update_data)
            else:
                # Create new relevance
                return await self.create_relevance(
                    url_id=url_id,
                    content_id=content_id,
                    relevance_text=relevance_text,
                    relevance_score=relevance_score,
                    is_relevant=is_relevant,
                    relevance_category=relevance_category,
                    confidence_score=confidence_score,
                    relevance_content_file_path=relevance_content_file_path,
                    version=version,
                    is_canonical=is_canonical,
                    preferred_choice=preferred_choice,
                    created_by=created_by
                )
                
        except ValidationException:
            raise
        except Exception as e:
            self.logger.error(f"Upsert relevance failed: {str(e)}")
            raise
    
    async def get_relevance_statistics(self, relevance_category: Optional[str] = None) -> Dict[str, Any]:
        """Get relevance statistics"""
        try:
            all_relevance = await self.get_all_relevance(relevance_category=relevance_category)
            
            if not all_relevance:
                return {
                    "total_entries": 0,
                    "relevant_count": 0,
                    "irrelevant_count": 0,
                    "average_relevance_score": 0.0,
                    "average_confidence_score": 0.0,
                    "high_confidence_count": 0,
                    "categories": {}
                }
            
            relevant_count = sum(1 for r in all_relevance if r.is_relevant)
            irrelevant_count = len(all_relevance) - relevant_count
            avg_relevance = sum(r.relevance_score for r in all_relevance) / len(all_relevance)
            avg_confidence = sum(r.confidence_score for r in all_relevance) / len(all_relevance)
            high_confidence_count = sum(1 for r in all_relevance if r.confidence_score >= 0.8)
            
            # Category breakdown
            categories = {}
            for relevance in all_relevance:
                cat = relevance.relevance_category
                if cat not in categories:
                    categories[cat] = {"count": 0, "relevant": 0, "avg_score": 0.0}
                categories[cat]["count"] += 1
                if relevance.is_relevant:
                    categories[cat]["relevant"] += 1
                categories[cat]["avg_score"] += relevance.relevance_score
            
            # Calculate averages for categories
            for cat_data in categories.values():
                if cat_data["count"] > 0:
                    cat_data["avg_score"] /= cat_data["count"]
            
            return {
                "total_entries": len(all_relevance),
                "relevant_count": relevant_count,
                "irrelevant_count": irrelevant_count,
                "average_relevance_score": round(avg_relevance, 3),
                "average_confidence_score": round(avg_confidence, 3),
                "high_confidence_count": high_confidence_count,
                "categories": categories
            }
            
        except Exception as e:
            self.logger.error(f"Get relevance statistics failed: {str(e)}")
            raise 