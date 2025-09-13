"""
Perplexity Content Table Configuration
Dedicated configuration for the perplexity_content table schema and settings
Used by Stage 0 Perplexity agent for individual content extraction results
"""

from typing import Dict, Any

class PerplexityContentTableConfig:
    """Configuration for the perplexity_content table"""
    
    # Table name (without environment suffix)
    TABLE_NAME = "perplexity_content"
    
    # Complete DynamoDB schema for perplexity_content table
    SCHEMA = {
        "table_name": TABLE_NAME,
        "key_schema": [
            {
                "AttributeName": "content_id",
                "KeyType": "HASH"  # Partition key
            }
        ],
        "attribute_definitions": [
            {
                "AttributeName": "content_id",
                "AttributeType": "S"  # String (format: {request_id}_{url_hash})
            }
        ],
        "billing_mode": "PAY_PER_REQUEST"
    }
    
    # Sample item structure (for reference - not used in table creation)
    SAMPLE_ITEM = {
        "content_id": "123e4567-e89b-12d3-a456-426614174000_abc123def456",  # Primary key (request_id_url_hash)
        "request_id": "123e4567-e89b-12d3-a456-426614174000",  # Request identifier
        "url": "https://example.com/pharmaceutical-trends-2024",  # Source URL
        "title": "Pharmaceutical Market Trends 2024: Key Insights",  # Content title
        "word_count": 1250,  # Content word count
        "extraction_confidence": 0.92,  # Confidence score (0.0-1.0)
        "content_type": "article",  # Content type
        "language": "en",  # Content language
        "created_at": "2024-12-01T10:00:00.000Z"  # ISO timestamp
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
        return "Individual content extraction results with primary key only - simple and fast" 