"""
Implication QA Table Configuration
Dedicated configuration for the implication_qa table schema and settings
Matches SQLAlchemy schema structure with DynamoDB NoSQL approach
"""

from typing import Dict, Any

class ImplicationQaTableConfig:
    """Configuration for the implication_qa table"""
    
    # Table name (without environment suffix)
    TABLE_NAME = "implication_qa"
    
    # Field mapping from SQLAlchemy to DynamoDB
    # SQLAlchemy -> DynamoDB mapping:
    # id (UUID) -> pk (String) - Primary key
    # implication_id (UUID) -> implication_id (String) - Implication ID reference
    # question (Text) -> question (String) - Question text
    # answer (Text) -> answer (String) - Answer text
    # question_type (String) -> question_type (String) - Question type
    # qa_metadata (JSON) -> qa_metadata (Map) - QA metadata
    # created_at (DateTime) -> created_at (String) - ISO timestamp
    
    # Complete DynamoDB schema for implication_qa table
    SCHEMA = {
        "table_name": TABLE_NAME,
        "key_schema": [
            {
                "AttributeName": "pk",  # Maps to SQLAlchemy 'id' field
                "KeyType": "HASH"  # Partition key
            }
        ],
        "attribute_definitions": [
            {
                "AttributeName": "pk",
                "AttributeType": "S"  # String (UUID as string)
            }
        ],
        "billing_mode": "PAY_PER_REQUEST"
    }
    
    # Sample item structure (for reference - not used in table creation)
    SAMPLE_ITEM = {
        "pk": "123e4567-e89b-12d3-a456-426614174000",  # Primary key (UUID as string)
        "implication_id": "987fcdeb-51a2-43d7-8f9e-123456789abc",  # Implication ID reference
        "question": "What are the potential regulatory risks associated with this market entry strategy?",  # Question text
        "answer": "The primary regulatory risks include compliance with FDA approval processes, adherence to local pharmaceutical regulations, and potential changes in regulatory framework during the approval timeline. We recommend conducting a comprehensive regulatory impact assessment before proceeding.",  # Answer text
        "question_type": "regulatory_risk",  # Question type
        "qa_metadata": {  # QA metadata (Map type)
            "confidence_score": 0.95,
            "source": "regulatory_expert",
            "review_status": "approved",
            "tags": ["regulatory", "risk_assessment", "market_entry"]
        },
        "created_at": "2024-12-01T10:00:00Z"  # ISO timestamp
    }
    
    @classmethod
    def get_table_name(cls, environment: str = None) -> str:
        """Get table name without environment suffix"""
        return cls.TABLE_NAME
    
    @classmethod
    def get_schema(cls, environment: str = None) -> Dict[str, Any]:
        """Get complete schema with table name"""
        schema = cls.SCHEMA.copy()
        schema["table_name"] = cls.get_table_name()
        return schema
    
    @classmethod
    def get_description(cls) -> str:
        """Get table description"""
        return "Implication QA table with primary key only - simple and fast" 