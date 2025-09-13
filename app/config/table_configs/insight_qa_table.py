"""
Insight QA Table Configuration
Dedicated configuration for the insight_qa table schema and settings
Matches SQLAlchemy schema structure with DynamoDB NoSQL approach
"""

from typing import Dict, Any

class InsightQaTableConfig:
    """Configuration for the insight_qa table"""
    
    # Table name (without environment suffix)
    TABLE_NAME = "insight_qa"
    
    # Field mapping from SQLAlchemy to DynamoDB
    # SQLAlchemy -> DynamoDB mapping:
    # id (UUID) -> pk (String) - Primary key
    # insight_id (UUID) -> insight_id (String) - Insight ID reference
    # question (Text) -> question (String) - Question text
    # answer (Text) -> answer (String) - Answer text
    # question_type (String) -> question_type (String) - Question type
    # qa_metadata (JSON) -> qa_metadata (Map) - QA metadata
    # created_at (DateTime) -> created_at (String) - ISO timestamp
    
    # Complete DynamoDB schema for insight_qa table
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
        "insight_id": "987fcdeb-51a2-43d7-8f9e-123456789abc",  # Insight ID reference
        "question": "What are the key market trends identified in this pharmaceutical analysis?",  # Question text
        "answer": "The analysis reveals three major market trends: increasing demand for personalized medicine, growing adoption of digital health solutions, and rising focus on preventive care. These trends suggest significant opportunities for targeted product development and strategic partnerships in the healthcare technology sector.",  # Answer text
        "question_type": "market_analysis",  # Question type
        "qa_metadata": {  # QA metadata (Map type)
            "confidence_score": 0.92,
            "source": "market_analyst",
            "review_status": "approved",
            "tags": ["market_trends", "pharmaceutical", "digital_health"]
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
        return "Insight QA table with primary key only - simple and fast" 