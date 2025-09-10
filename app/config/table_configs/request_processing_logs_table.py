"""
Request Processing Logs Table Configuration
"""

from app.config.settings import settings

class RequestProcessingLogsTableConfig:
    """Configuration for request_processing_logs table"""
    
    BASE_TABLE_NAME = "request_processing_logs"
    
    @classmethod
    def get_table_name(cls, environment: str = None) -> str:
        """Get environment-specific table name"""
        env = environment or settings.TABLE_ENVIRONMENT
        if env == "production":
            return f"prod-{cls.BASE_TABLE_NAME}"
        elif env == "staging":
            return f"staging-{cls.BASE_TABLE_NAME}"
        elif env == "development":
            return f"dev-{cls.BASE_TABLE_NAME}"
        else:
            return cls.BASE_TABLE_NAME
    
    SCHEMA = {
        "key_schema": [
            {
                "AttributeName": "log_id",
                "KeyType": "HASH"
            }
        ],
        "attribute_definitions": [
            {
                "AttributeName": "log_id",
                "AttributeType": "S"
            }
        ],
        "billing_mode": "PAY_PER_REQUEST"
    }
    
    # Field definitions for documentation and validation
    FIELDS = {
        "log_id": {
            "type": "string",
            "description": "Unique log identifier (Primary Key)",
            "required": True,
            "example": "log_1757412789250_001"
        },
        "request_id": {
            "type": "string",
            "description": "Associated request identifier",
            "required": True,
            "example": "req_1757412789250_a08ac7ad"
        },
        "timestamp": {
            "type": "string",
            "description": "ISO timestamp of log entry",
            "required": True,
            "example": "2024-01-09T15:43:09.250000"
        },
        "log_level": {
            "type": "string",
            "description": "Log level",
            "required": True,
            "enum": ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
            "example": "INFO"
        },
        "message": {
            "type": "string",
            "description": "Log message",
            "required": True,
            "example": "Request processing started"
        },
        "stage": {
            "type": "string",
            "description": "Processing stage",
            "required": False,
            "example": "initialization"
        },
        "metadata": {
            "type": "map",
            "description": "Additional log metadata",
            "required": False
        }
    } 