"""
Main FastAPI Application
Simplified setup with basic functionality
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config.settings import settings
from app.core.logging import setup_logging, get_logger
from app.core.response import ResponseFormatter, APIResponse
from app.core.database import dynamodb_client
from app.routes.user_routes import router as user_router
from app.routes.project_routes import router as project_router
from app.routes.global_keywords_routes import router as global_keywords_router
from app.routes.global_base_url_routes import router as global_base_url_router
from app.routes.migration_routes import router as migration_router
from app.routes.seeder_routes import router as seeder_router

# Initialize logging
setup_logging()
logger = get_logger("main")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info(f"Starting {settings.PROJECT_NAME}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    
    try:
        # Test database connection
        health = dynamodb_client.health_check()
        if health['status'] == 'healthy':
            logger.info("Database connection established")
        else:
            logger.warning(f"Database connection issues: {health.get('error', 'Unknown')}")
        
        logger.info("Application startup completed")
        
    except Exception as e:
        logger.error(f"Startup failed: {str(e)}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down application")

# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
    docs_url=settings.DOCS_URL,
    redoc_url=settings.REDOC_URL,
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)

# Routes
app.include_router(
    user_router,
    prefix="/api/v1/users",
    tags=["Users"]
)

app.include_router(
    project_router,
    prefix="/api/v1/projects",
    tags=["Projects"]
)

app.include_router(
    global_keywords_router,
    prefix="/api/v1/global-keywords",
    tags=["Global Keywords"]
)

app.include_router(
    global_base_url_router,
    prefix="/api/v1/global-base-urls",
    tags=["Global Base URLs"]
)

# Migration and Seeder Routes
app.include_router(
    migration_router,
    prefix="/api/v1"
)

app.include_router(
    seeder_router,
    prefix="/api/v1"
)

# Health Check Endpoint
@app.get("/health", 
         response_model=APIResponse,
         summary="Health check",
         description="Check application and database health")
async def health_check() -> APIResponse:
    """Health check endpoint"""
    try:
        # Get database health
        db_health = dynamodb_client.health_check()
        
        health_data = {
            "status": "healthy" if db_health['status'] == 'healthy' else "degraded",
            "version": settings.VERSION,
            "environment": settings.ENVIRONMENT,
            "database": db_health
        }
        
        return ResponseFormatter.success(
            data=health_data,
            message="Application is healthy"
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        
        return ResponseFormatter.error(
            message="Health check failed",
            errors=[{"error": str(e)}]
        )

# Root endpoint
@app.get("/",
         response_model=APIResponse,
         summary="API information",
         description="Get basic API information")
async def root() -> APIResponse:
    """Root endpoint with API information"""
    api_info = {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "description": settings.DESCRIPTION,
        "environment": settings.ENVIRONMENT,
        "endpoints": {
            "users": "/api/v1/users",
            "projects": "/api/v1/projects",
            "global_keywords": "/api/v1/global-keywords",
            "global_base_urls": "/api/v1/global-base-urls",
            "migrations": "/api/v1/migrations",
            "seeders": "/api/v1/seeders",
            "health": "/health",
            "docs": settings.DOCS_URL
        }
    }
    
    return ResponseFormatter.success(
        data=api_info,
        message=f"Welcome to {settings.PROJECT_NAME}"
    )

if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"Starting {settings.PROJECT_NAME} on {settings.HOST}:{settings.PORT}")
    
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
        reload_excludes=["logs/*", "*.log", "__pycache__/*"] if settings.DEBUG else None
    )