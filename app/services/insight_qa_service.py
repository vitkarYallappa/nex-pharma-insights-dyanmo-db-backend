"""
Insight QA Service - Works with InsightQaModel and InsightQaRepository
Follows the same pattern as ProjectService for consistency
"""

from typing import List, Optional, Dict, Any
from app.repositories.insight_qa_repository import InsightQaRepository
from app.models.insight_qa_model import InsightQaModel
from app.core.logging import get_logger
from app.core.exceptions import (
    ValidationException
)

logger = get_logger("insight_qa_service")

class InsightQaNotFoundException(Exception):
    """Exception raised when insight QA entry is not found"""
    pass

class InsightQaAlreadyExistsException(Exception):
    """Exception raised when insight QA entry already exists"""
    pass

class InsightQaService:
    """Insight QA service with essential operations"""
    
    def __init__(self):
        self.qa_repository = InsightQaRepository()
        self.logger = logger
    
    async def create_insight_qa(self, insight_id: str, question: str, answer: str,
                            question_type: Optional[str] = None, qa_metadata: Optional[Dict[str, Any]] = None) -> InsightQaModel:
        """Create a new insight QA entry"""
        try:
            # Validate required fields
            if not insight_id or not insight_id.strip():
                raise ValidationException("Insight ID is required")
            
            if not question or not question.strip():
                raise ValidationException("Question is required")
            
            if not answer or not answer.strip():
                raise ValidationException("Answer is required")
            
            # Create QA model
            qa_model = InsightQaModel.create_new(
                insight_id=insight_id.strip(),
                question=question.strip(),
                answer=answer.strip(),
                question_type=question_type.strip() if question_type else None,
                qa_metadata=qa_metadata
            )
            
            # Save to database
            created_qa = await self.qa_repository.create(qa_model)
            self.logger.info(f"Insight QA entry created for insight {insight_id}")
            return created_qa
            
        except ValidationException:
            raise
        except Exception as e:
            self.logger.error(f"Create insight QA entry failed: {str(e)}")
            raise
    
    async def get_insight_qa_by_id(self, qa_id: str) -> InsightQaModel:
        """Get insight QA entry by ID"""
        try:
            if not qa_id or not qa_id.strip():
                raise ValidationException("QA ID is required")
            
            qa = await self.qa_repository.find_one_by_query({"pk": qa_id.strip()})
            if not qa:
                raise InsightQaNotFoundException(f"Insight QA entry with ID {qa_id} not found")
            
            return qa
            
        except (InsightQaNotFoundException, ValidationException):
            raise
        except Exception as e:
            self.logger.error(f"Get insight QA entry by ID failed: {str(e)}")
            raise
    
    async def get_all_insight_qa(self, insight_id: Optional[str] = None,
                                   question_type: Optional[str] = None,
                                   limit: Optional[int] = None) -> List[InsightQaModel]:
        """Get insight QA entries with optional filters"""
        try:
            # Validate limit
            if limit is not None and limit <= 0:
                raise ValidationException("Limit must be a positive number")
            
            qa_list = await self.qa_repository.get_all_insight_qa(
                insight_id=insight_id.strip() if insight_id else None,
                question_type=question_type.strip() if question_type else None,
                limit=limit
            )
            
            self.logger.info(f"Retrieved {len(qa_list)} insight QA entries with filters: insight_id={insight_id}, question_type={question_type}")
            return qa_list
            
        except ValidationException:
            raise
        except Exception as e:
            self.logger.error(f"Get insight QA entries by query failed: {str(e)}")
            raise
    
    async def update_insight_qa(self, qa_id: str, update_data: Dict[str, Any]) -> InsightQaModel:
        """Update insight QA entry by ID"""
        try:
            if not qa_id or not qa_id.strip():
                raise ValidationException("QA ID is required")
            
            # Check if QA exists
            existing_qa = await self.get_insight_qa_by_id(qa_id)
            
            # Prepare update data (remove None values)
            clean_update_data = {k: v for k, v in update_data.items() if v is not None}
            
            updated_qa = await self.qa_repository.update_insight_qa(
                qa_id.strip(), clean_update_data
            )
            
            if not updated_qa:
                raise InsightQaNotFoundException(f"Failed to update insight QA entry with ID {qa_id}")
            
            self.logger.info(f"Insight QA entry updated: {qa_id}")
            return updated_qa
            
        except (InsightQaNotFoundException, ValidationException):
            raise
        except Exception as e:
            self.logger.error(f"Update insight QA entry failed: {str(e)}")
            raise
    
