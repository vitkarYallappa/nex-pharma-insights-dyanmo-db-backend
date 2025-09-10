"""
Pipeline States Table Configuration
Dedicated configuration for the pipeline_states table schema and settings
Used by Stage 0 Orchestrator agent for pipeline orchestration state tracking
"""

from typing import Dict, Any

class PipelineStatesTableConfig:
    """Configuration for the pipeline_states table"""
    
    # Table name (without environment suffix)
    TABLE_NAME = "pipeline_states"
    
    # Complete DynamoDB schema for pipeline_states table
    SCHEMA = {
        "table_name": TABLE_NAME,
        "key_schema": [
            {
                "AttributeName": "request_id",
                "KeyType": "HASH"  # Partition key
            }
        ],
        "attribute_definitions": [
            {
                "AttributeName": "request_id",
                "AttributeType": "S"  # String (UUID)
            }
        ],
        "billing_mode": "PAY_PER_REQUEST"
    }
    
    # Sample item structure (for reference - not used in table creation)
    SAMPLE_ITEM = {
        "request_id": "123e4567-e89b-12d3-a456-426614174000",  # Primary key (UUID)
        "status": "extracting",  # Pipeline status (pending, searching, extracting, aggregating, completed, failed, partial_success)
        "current_stage": "perplexity_extraction",  # Current processing stage
        "progress_percentage": 65,  # Progress percentage (0-100)
        "search_completed": True,  # Search stage completed
        "extraction_completed": False,  # Extraction stage completed
        "aggregation_completed": False,  # Aggregation stage completed
        "urls_found": 15,  # URLs found in search
        "content_extracted": 8,  # Successfully extracted content
        "content_failed": 2,  # Failed content extractions
        "started_at": "2024-12-01T10:00:00.000Z",  # ISO timestamp
        "search_started_at": "2024-12-01T10:00:30.000Z",  # ISO timestamp
        "extraction_started_at": "2024-12-01T10:05:00.000Z",  # ISO timestamp
        "completed_at": None,  # ISO timestamp (null if not completed)
        "errors": ["Failed to extract content from https://example.com/blocked"],  # Error messages
        "warnings": ["Low confidence extraction for https://example.com/partial"]  # Warning messages
    }
    
    @classmethod
    def get_table_name(cls, environment: str = "local") -> str:
        """Get full table name with environment suffix"""
        return f"{cls.TABLE_NAME}-{environment}"
    
    @classmethod
    def get_schema(cls, environment: str = "local") -> Dict[str, Any]:
        """Get complete schema with environment-specific table name"""
        schema = cls.SCHEMA.copy()
        schema["table_name"] = cls.get_table_name(environment)
        return schema
    
    @classmethod
    def get_description(cls) -> str:
        """Get table description"""
        return "Pipeline orchestration state tracking with primary key only - simple and fast" 