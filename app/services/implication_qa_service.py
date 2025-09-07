"""
Implication QA Service - Works with ImplicationQaModel and ImplicationQaRepository
Follows the same pattern as ProjectService for consistency
"""

from typing import List, Optional, Dict, Any
from app.repositories.implication_qa_repository import ImplicationQaRepository
from app.models.implication_qa_model import ImplicationQaModel
from app.core.logging import get_logger
from app.core.exceptions import (
    ValidationException
)

logger = get_logger("implication_qa_service")

class ImplicationQaNotFoundException(Exception):
    """Exception raised when implication QA entry is not found"""
    pass

class ImplicationQaAlreadyExistsException(Exception):
    """Exception raised when implication QA entry already exists"""
    pass

class ImplicationQaService:
    """Implication QA service with essential operations"""
    
    def __init__(self):
        self.qa_repository = ImplicationQaRepository()
        self.logger = logger
    
    async def create_project(self, implication_id: str, question: str, answer: str, 
                            question_type: Optional[str] = None, qa_metadata: Optional[Dict[str, Any]] = None) -> ImplicationQaModel:
        """Create a new implication QA entry"""
        try:
            # Validate required fields
            if not implication_id or not implication_id.strip():
                raise ValidationException("Implication ID is required")
            
            if not question or not question.strip():
                raise ValidationException("Question is required")
            
            if not answer or not answer.strip():
                raise ValidationException("Answer is required")
            
            # Create QA model
            qa_model = ImplicationQaModel.create_new(
                implication_id=implication_id.strip(),
                question=question.strip(),
                answer=answer.strip(),
                question_type=question_type.strip() if question_type else None,
                qa_metadata=qa_metadata
            )
            
            # Save to database
            created_qa = await self.qa_repository.create(qa_model)
            self.logger.info(f"Implication QA entry created for implication {implication_id}")
            return created_qa
            
        except ValidationException:
            raise
        except Exception as e:
            self.logger.error(f"Create implication QA entry failed: {str(e)}")
            raise
    
    async def get_project_by_id(self, qa_id: str) -> ImplicationQaModel:
        """Get implication QA entry by ID"""
        try:
            if not qa_id or not qa_id.strip():
                raise ValidationException("QA ID is required")
            
            qa = await self.qa_repository.find_one_by_query({"pk": qa_id.strip()})
            if not qa:
                raise ImplicationQaNotFoundException(f"Implication QA entry with ID {qa_id} not found")
            
            return qa
            
        except (ImplicationQaNotFoundException, ValidationException):
            raise
        except Exception as e:
            self.logger.error(f"Get implication QA entry by ID failed: {str(e)}")
            raise
    
    async def get_projects_by_query(self, implication_id: Optional[str] = None,
                                   question_type: Optional[str] = None,
                                   limit: Optional[int] = None) -> List[ImplicationQaModel]:
        """Get implication QA entries with optional filters"""
        try:
            # Validate limit
            if limit is not None and limit <= 0:
                raise ValidationException("Limit must be a positive number")
            
            qa_list = await self.qa_repository.get_all_projects(
                implication_id=implication_id.strip() if implication_id else None,
                question_type=question_type.strip() if question_type else None,
                limit=limit
            )
            
            self.logger.info(f"Retrieved {len(qa_list)} implication QA entries with filters: implication_id={implication_id}, question_type={question_type}")
            return qa_list
            
        except ValidationException:
            raise
        except Exception as e:
            self.logger.error(f"Get implication QA entries by query failed: {str(e)}")
            raise
    
    async def update_project(self, qa_id: str, update_data: Dict[str, Any]) -> ImplicationQaModel:
        """Update implication QA entry by ID"""
        try:
            if not qa_id or not qa_id.strip():
                raise ValidationException("QA ID is required")
            
            # Check if QA exists
            existing_qa = await self.get_project_by_id(qa_id)
            
            # Prepare update data (remove None values)
            clean_update_data = {k: v for k, v in update_data.items() if v is not None}
            
            updated_qa = await self.qa_repository.update_project(
                qa_id.strip(), clean_update_data
            )
            
            if not updated_qa:
                raise ImplicationQaNotFoundException(f"Failed to update implication QA entry with ID {qa_id}")
            
            self.logger.info(f"Implication QA entry updated: {qa_id}")
            return updated_qa
            
        except (ImplicationQaNotFoundException, ValidationException):
            raise
        except Exception as e:
            self.logger.error(f"Update implication QA entry failed: {str(e)}")
            raise
    
    async def get_qa_by_implication(self, implication_id: str, question_type: Optional[str] = None) -> List[ImplicationQaModel]:
        """Get all QA entries for a specific implication ID"""
        try:
            if not implication_id or not implication_id.strip():
                raise ValidationException("Implication ID is required")
            
            qa_list = await self.qa_repository.get_all_projects(
                implication_id=implication_id.strip(),
                question_type=question_type.strip() if question_type else None
            )
            
            self.logger.info(f"Retrieved {len(qa_list)} QA entries for implication {implication_id}")
            return qa_list
            
        except ValidationException:
            raise
        except Exception as e:
            self.logger.error(f"Get QA by implication failed: {str(e)}")
            raise
    
    async def get_qa_by_type(self, question_type: str, implication_id: Optional[str] = None) -> List[ImplicationQaModel]:
        """Get all QA entries for a specific question type"""
        try:
            if not question_type or not question_type.strip():
                raise ValidationException("Question type is required")
            
            qa_list = await self.qa_repository.get_all_projects(
                question_type=question_type.strip(),
                implication_id=implication_id.strip() if implication_id else None
            )
            
            self.logger.info(f"Retrieved {len(qa_list)} QA entries for type {question_type}")
            return qa_list
            
        except ValidationException:
            raise
        except Exception as e:
            self.logger.error(f"Get QA by type failed: {str(e)}")
            raise
    
    async def update_question(self, qa_id: str, question: str) -> ImplicationQaModel:
        """Update question text"""
        try:
            if not question or not question.strip():
                raise ValidationException("Question is required")
            
            qa = await self.get_project_by_id(qa_id)
            qa.update_question(question.strip())
            
            updated_qa = await self.qa_repository.update_project(
                qa_id, qa.to_dict()
            )
            
            if not updated_qa:
                raise ImplicationQaNotFoundException(f"Failed to update question for QA with ID {qa_id}")
            
            self.logger.info(f"Question updated for QA: {qa_id}")
            return updated_qa
            
        except (ImplicationQaNotFoundException, ValidationException):
            raise
        except Exception as e:
            self.logger.error(f"Update question failed: {str(e)}")
            raise
    
    async def update_answer(self, qa_id: str, answer: str) -> ImplicationQaModel:
        """Update answer text"""
        try:
            if not answer or not answer.strip():
                raise ValidationException("Answer is required")
            
            qa = await self.get_project_by_id(qa_id)
            qa.update_answer(answer.strip())
            
            updated_qa = await self.qa_repository.update_project(
                qa_id, qa.to_dict()
            )
            
            if not updated_qa:
                raise ImplicationQaNotFoundException(f"Failed to update answer for QA with ID {qa_id}")
            
            self.logger.info(f"Answer updated for QA: {qa_id}")
            return updated_qa
            
        except (ImplicationQaNotFoundException, ValidationException):
            raise
        except Exception as e:
            self.logger.error(f"Update answer failed: {str(e)}")
            raise
    
    async def update_question_type(self, qa_id: str, question_type: str) -> ImplicationQaModel:
        """Update question type"""
        try:
            if not question_type or not question_type.strip():
                raise ValidationException("Question type is required")
            
            qa = await self.get_project_by_id(qa_id)
            qa.update_question_type(question_type.strip())
            
            updated_qa = await self.qa_repository.update_project(
                qa_id, qa.to_dict()
            )
            
            if not updated_qa:
                raise ImplicationQaNotFoundException(f"Failed to update question type for QA with ID {qa_id}")
            
            self.logger.info(f"Question type updated for QA: {qa_id} to {question_type}")
            return updated_qa
            
        except (ImplicationQaNotFoundException, ValidationException):
            raise
        except Exception as e:
            self.logger.error(f"Update question type failed: {str(e)}")
            raise
    
    async def update_qa_metadata(self, qa_id: str, qa_metadata: Dict[str, Any]) -> ImplicationQaModel:
        """Update QA metadata"""
        try:
            if not qa_metadata:
                raise ValidationException("QA metadata is required")
            
            qa = await self.get_project_by_id(qa_id)
            qa.update_qa_metadata(qa_metadata)
            
            updated_qa = await self.qa_repository.update_project(
                qa_id, qa.to_dict()
            )
            
            if not updated_qa:
                raise ImplicationQaNotFoundException(f"Failed to update QA metadata for QA with ID {qa_id}")
            
            self.logger.info(f"QA metadata updated for QA: {qa_id}")
            return updated_qa
            
        except (ImplicationQaNotFoundException, ValidationException):
            raise
        except Exception as e:
            self.logger.error(f"Update QA metadata failed: {str(e)}")
            raise 