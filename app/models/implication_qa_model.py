"""
Implication QA Model - Matches SQLAlchemy schema structure
Handles implication QA data operations with DynamoDB
"""

import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

from app.config.table_configs.implication_qa_table import ImplicationQaTableConfig
from app.config.settings import settings

class ImplicationQaModel(BaseModel):
    """Implication QA model matching SQLAlchemy schema"""
    
    # SQLAlchemy: id (UUID) -> DynamoDB: pk (String)
    pk: str = Field(..., description="QA ID (UUID as string)")
    
    # SQLAlchemy: implication_id (UUID) -> DynamoDB: implication_id (String)
    implication_id: str = Field(..., description="Implication ID reference (UUID as string)")
    
    # SQLAlchemy: question (Text) -> DynamoDB: question (String)
    question: str = Field(..., description="Question text")
    
    # SQLAlchemy: answer (Text) -> DynamoDB: answer (String)
    answer: str = Field(..., description="Answer text")
    
    # SQLAlchemy: question_type (String) -> DynamoDB: question_type (String)
    question_type: Optional[str] = Field(None, description="Question type")
    
    # SQLAlchemy: qa_metadata (JSON) -> DynamoDB: qa_metadata (Map)
    qa_metadata: Optional[Dict[str, Any]] = Field(None, description="QA metadata")
    
    # SQLAlchemy: created_at (DateTime) -> DynamoDB: created_at (String)
    created_at: str = Field(..., description="Creation timestamp (ISO string)")
    
    @classmethod
    def table_name(cls) -> str:
        """Return DynamoDB table name for current environment"""
        return ImplicationQaTableConfig.get_table_name()
    
    @classmethod
    def create_new(cls, implication_id: str, question: str, answer: str, 
                   question_type: Optional[str] = None, qa_metadata: Optional[Dict[str, Any]] = None) -> 'ImplicationQaModel':
        """Create a new implication QA instance"""
        now = datetime.utcnow().isoformat()
        
        return cls(
            pk=str(uuid.uuid4()),
            implication_id=implication_id,
            question=question,
            answer=answer,
            question_type=question_type,
            qa_metadata=qa_metadata,
            created_at=now
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary for DynamoDB storage"""
        data = self.model_dump()
        
        # Remove None values to keep DynamoDB items clean
        return {k: v for k, v in data.items() if v is not None}
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ImplicationQaModel':
        """Create model instance from DynamoDB data"""
        return cls(**data)
    
    def to_response(self) -> Dict[str, Any]:
        """Convert model to API response format"""
        return {
            "id": self.pk,  # Return as 'id' for API consistency
            "implication_id": self.implication_id,
            "question": self.question,
            "answer": self.answer,
            "question_type": self.question_type,
            "qa_metadata": self.qa_metadata,
            "created_at": self.created_at
        }
    
    def update_fields(self, **kwargs) -> None:
        """Update model fields"""
        for key, value in kwargs.items():
            if hasattr(self, key) and key not in ['pk', 'created_at']:
                setattr(self, key, value)
    
    def update_question(self, question: str) -> None:
        """Update question text"""
        self.question = question
    
    def update_answer(self, answer: str) -> None:
        """Update answer text"""
        self.answer = answer
    
    def update_question_type(self, question_type: str) -> None:
        """Update question type"""
        self.question_type = question_type
    
    def update_qa_metadata(self, qa_metadata: Dict[str, Any]) -> None:
        """Update QA metadata"""
        self.qa_metadata = qa_metadata 