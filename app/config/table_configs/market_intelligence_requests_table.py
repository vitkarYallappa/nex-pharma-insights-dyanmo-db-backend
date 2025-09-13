"""
Market Intelligence Requests Table Configuration
"""

from app.config.settings import settings

class MarketIntelligenceRequestsTableConfig:
    """Configuration for market_intelligence_requests table"""
    
    BASE_TABLE_NAME = "market_intelligence_requests"
    
    @classmethod
    def get_table_name(cls, environment: str = None) -> str:
        """Get table name without environment suffix"""
        return cls.BASE_TABLE_NAME
    
    SCHEMA = {
        "key_schema": [
            {
                "AttributeName": "request_id",
                "KeyType": "HASH"
            }
        ],
        "attribute_definitions": [
            {
                "AttributeName": "request_id",
                "AttributeType": "S"
            }
        ],
        "billing_mode": "PAY_PER_REQUEST"
    }
    
    # Field definitions for documentation and validation
    FIELDS = {
        "request_id": {
            "type": "string",
            "description": "Unique request identifier (Primary Key)",
            "required": True,
            "example": "req_1757412789250_a08ac7ad"
        },
        "project_id": {
            "type": "string", 
            "description": "Project identifier",
            "required": True,
            "example": "test-project-001"
        },
        "user_id": {
            "type": "string",
            "description": "User who submitted request",
            "required": True,
            "example": "test-user-123"
        },
        "request_type": {
            "type": "string",
            "description": "Type of intelligence request",
            "required": True,
            "example": "semaglutide_intelligence"
        },
        "status": {
            "type": "string",
            "description": "Current status",
            "required": True,
            "enum": ["pending", "processing", "executing", "completed", "failed", "cancelled"],
            "example": "pending"
        },
        "status_message": {
            "type": "string",
            "description": "Current status message",
            "required": False,
            "example": "Processing started"
        },
        "priority": {
            "type": "string",
            "description": "Priority level",
            "required": True,
            "enum": ["high", "medium", "low"],
            "example": "high"
        },
        "processing_strategy": {
            "type": "string",
            "description": "Processing strategy",
            "required": True,
            "enum": ["table", "sqs"],
            "example": "table"
        },
        "config": {
            "type": "map",
            "description": "Request configuration object",
            "required": True
        },
        "created_at": {
            "type": "string",
            "description": "ISO timestamp of creation",
            "required": True,
            "example": "2024-01-09T15:43:09.250000"
        },
        "updated_at": {
            "type": "string",
            "description": "ISO timestamp of last update",
            "required": True,
            "example": "2024-01-09T15:43:19.261000"
        },
        "started_at": {
            "type": "string",
            "description": "ISO timestamp when processing started",
            "required": False,
            "example": "2024-01-09T15:43:09.251000"
        },
        "completed_at": {
            "type": "string",
            "description": "ISO timestamp when processing completed",
            "required": False,
            "example": "2024-01-09T15:45:00.000000"
        },
        "progress": {
            "type": "map",
            "description": "Progress tracking object",
            "required": True
        },
        "results": {
            "type": "map",
            "description": "Processing results object",
            "required": False
        },
        "errors": {
            "type": "list",
            "description": "List of error messages",
            "required": True
        },
        "warnings": {
            "type": "list",
            "description": "List of warning messages",
            "required": True
        },
        "processing_metadata": {
            "type": "map",
            "description": "Additional processing metadata",
            "required": True
        }
    } 