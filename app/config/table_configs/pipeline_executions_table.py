"""
Pipeline Executions Table Configuration
Dedicated configuration for the pipeline_executions table schema and settings
Used by Stage 0 Orchestrator agent for pipeline execution history and analytics
"""

from typing import Dict, Any

class PipelineExecutionsTableConfig:
    """Configuration for the pipeline_executions table"""
    
    # Table name (without environment suffix)
    TABLE_NAME = "pipeline_executions"
    
    # Complete DynamoDB schema for pipeline_executions table
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
        "original_query": "pharmaceutical market trends 2024",  # Original search query
        "total_urls": 15,  # Total URLs processed
        "content_extracted": 12,  # Content successfully extracted
        "processing_time": 180,  # Total processing time in seconds
        "final_status": "completed",  # Final pipeline status
        "storage_paths": {  # Storage location paths
            "serp_results": "serp/2024/12/01/123e4567-e89b-12d3-a456-426614174000.json",
            "extracted_content": "perplexity/2024/12/01/123e4567-e89b-12d3-a456-426614174000.json",
            "aggregated_results": "aggregated/2024/12/01/123e4567-e89b-12d3-a456-426614174000.json"
        },
        "created_at": "2024-12-01T10:00:00.000Z"  # ISO timestamp
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
        return "Pipeline execution history and analytics with primary key only - simple and fast" 