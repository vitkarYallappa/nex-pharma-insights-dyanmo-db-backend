"""
Application Settings Configuration
Handles all environment variables and application configuration
"""

from pydantic_settings import BaseSettings
from typing import Optional
import os
from app.config.tables import TableConfig, TableNames

class Settings(BaseSettings):
    # Project Information
    PROJECT_NAME: str = "FastAPI DynamoDB App"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "A scalable FastAPI application with DynamoDB"
    
    # Environment
    ENVIRONMENT: str = "development"  # development, staging, production
    DEBUG: bool = True
    
    # Server Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8002
    
    # Database Configuration
    DATABASE_TYPE: str = "dynamodb"  # dynamodb, sqlite
    AWS_REGION: str = "us-east-1"
    
    # DynamoDB Mode Configuration
    USE_LOCAL_DYNAMODB: bool = False  # True for local DynamoDB, False for AWS DynamoDB
    
    # AWS DynamoDB Configuration
    AWS_ACCESS_KEY_ID: Optional[str] = "dummy"  # Default for local development
    AWS_SECRET_ACCESS_KEY: Optional[str] = "dummy"  # Default for local development
    AWS_SESSION_TOKEN: Optional[str] = None  # For temporary credentials
    DYNAMODB_ENDPOINT: Optional[str] = "http://localhost:8000"  # For local development
    
    # Table Configuration
    TABLE_ENVIRONMENT: str = "local"  # local, dev, staging, prod
    
    @property
    def table_config(self) -> TableConfig:
        """Get table configuration for current environment"""
        return TableConfig(self.TABLE_ENVIRONMENT)
    
    @property
    def has_real_aws_credentials(self) -> bool:
        """Check if real AWS credentials are provided (not dummy values)"""
        return (
            self.AWS_ACCESS_KEY_ID and 
            self.AWS_SECRET_ACCESS_KEY and
            self.AWS_ACCESS_KEY_ID != "dummy" and 
            self.AWS_SECRET_ACCESS_KEY != "dummy"
        )
    
    @property
    def should_use_aws_dynamodb(self) -> bool:
        """Determine if AWS DynamoDB should be used based on credentials and configuration"""
        # If real AWS credentials are provided, always use AWS DynamoDB
        if self.has_real_aws_credentials:
            return True
        # If dummy credentials, always use local DynamoDB (safer)
        else:
            return False
    
    @property
    def dynamodb_endpoint(self) -> Optional[str]:
        """Get DynamoDB endpoint based on configuration and credentials"""
        if self.should_use_aws_dynamodb:
            return None  # Use AWS DynamoDB service (no endpoint needed)
        else:
            return self.DYNAMODB_ENDPOINT  # Use local endpoint
    
    @property
    def effective_table_environment(self) -> str:
        """Get effective table environment based on DynamoDB mode and credentials"""
        if self.should_use_aws_dynamodb:
            # Use the configured table environment for AWS
            return self.TABLE_ENVIRONMENT if self.TABLE_ENVIRONMENT != "local" else "dev"
        else:
            return "local"
    
    @property
    def aws_credentials_required(self) -> bool:
        """Check if real AWS credentials are required"""
        return self.should_use_aws_dynamodb
    
    @property
    def USERS_TABLE(self) -> str:
        """Get users table name for current environment"""
        return TableNames.get_users_table(self.effective_table_environment)
    
    # Security
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Logging Configuration
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_MAX_SIZE: int = 10 * 1024 * 1024  # 10MB
    LOG_BACKUP_COUNT: int = 5
    
    # API Configuration
    API_V1_PREFIX: str = "/api/v1"
    DOCS_URL: str = "/docs"
    REDOC_URL: str = "/redoc"
    
    # CORS Configuration
    CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:8000", "http://localhost:8001", "http://localhost:8002","http://localhost:5173", "http://localhost:5174"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: list = ["*"]
    CORS_ALLOW_HEADERS: list = ["*"]
    
    # Pagination
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 60  # seconds
    
    @property
    def is_development(self) -> bool:
        return self.ENVIRONMENT == "development"
    
    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"
    
    @property
    def log_file_path(self) -> str:
        # Put logs outside the app directory to avoid reload loops
        if self.is_development:
            log_file = os.path.join("..", "logs", "app.log")
        else:
            log_file = self.LOG_FILE
        
        # Ensure logs directory exists
        log_dir = os.path.dirname(log_file)
        os.makedirs(log_dir, exist_ok=True)
        return log_file
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "allow"  # Allow extra properties like USERS_TABLE

# Global settings instance
settings = Settings()