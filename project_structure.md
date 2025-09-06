# Nex Pharma Insights Backend - Project Structure

## Complete Folder and File Structure

```
nex-pharma-insights-backend/
├── .git/                                    # Git repository data
├── .idea/                                   # IDE configuration files
├── .venv/                                   # Python virtual environment
├── __pycache__/                            # Python bytecode cache
│
├── main.py                                  # FastAPI application entry point
├── requirements.txt                         # Python dependencies
├── alembic.ini                             # Alembic migration configuration
├── env.example                             # Environment variables template
├── README.md                               # Project documentation
├── DATABASE_SETUP_GUIDE.md                # Database setup instructions
│
├── create_project_request_flow.py          # Project request flow creation script
├── multi_dataset_seeder.py                # Multi-dataset seeding script
├── run_multi_dataset_seeder.py            # Runner for multi-dataset seeder
├── seed_database.py                        # Database seeding script
│
├── app/                                    # Main application package
│   ├── __init__.py                         # Package initialization
│   │
│   ├── core/                               # Core application components
│   │   ├── __init__.py
│   │   ├── config.py                       # Application configuration
│   │   ├── database.py                     # Database connection and session
│   │   └── response.py                     # Standard API response formats
│   │
│   ├── models/                             # SQLAlchemy database models
│   │   ├── __init__.py                     # Models package initialization
│   │   ├── user.py                         # User model
│   │   ├── project_details.py              # Project details model
│   │   ├── project_request_statistics.py   # Project request statistics model
│   │   ├── project_modules_statistics.py   # Project modules statistics model
│   │   ├── request.py                      # Request model
│   │   ├── global_keyword.py               # Global keyword model
│   │   ├── global_base_url.py              # Global base URL model
│   │   ├── keyword.py                      # Keyword model
│   │   ├── source_url.py                   # Source URL model
│   │   ├── content_repository.py           # Content repository model
│   │   ├── process_handling.py             # Process handling model
│   │   ├── content_url_mapping.py          # Content URL mapping model
│   │   ├── content_summary.py              # Content summary model
│   │   ├── content_insight.py              # Content insight model
│   │   ├── content_implication.py          # Content implication model
│   │   ├── content_analysis_mapping.py     # Content analysis mapping model
│   │   ├── insight_comment.py              # Insight comment model
│   │   ├── implication_comment.py          # Implication comment model
│   │   ├── insight_qa.py                   # Insight Q&A model
│   │   └── implication_qa.py               # Implication Q&A model
│   │
│   ├── controllers/                        # Request handlers/controllers
│   │   ├── __init__.py
│   │   ├── user_controller.py              # User management controller
│   │   ├── project_details_controller.py   # Project details controller
│   │   ├── project_request_statistics_controller.py    # Project request stats controller
│   │   ├── project_modules_statistics_controller.py    # Project modules stats controller
│   │   ├── request_controller.py           # Request management controller
│   │   ├── global_keyword_controller.py    # Global keyword controller
│   │   ├── global_base_url_controller.py   # Global base URL controller
│   │   ├── content_repository_controller.py # Content repository controller
│   │   ├── content_summary_controller.py   # Content summary controller
│   │   ├── content_insight_controller.py   # Content insight controller
│   │   ├── content_implication_controller.py # Content implication controller
│   │   ├── insight_comment_controller.py   # Insight comment controller
│   │   └── implication_comment_controller.py # Implication comment controller
│   │
│   ├── services/                           # Business logic services
│   │   ├── __init__.py
│   │   ├── user_service.py                 # User business logic
│   │   ├── project_details_service.py      # Project details business logic
│   │   ├── project_request_statistics_service.py      # Project request stats service
│   │   ├── project_modules_statistics_service.py      # Project modules stats service
│   │   ├── request_service.py              # Request business logic
│   │   ├── global_keyword_service.py       # Global keyword service
│   │   ├── global_base_url_service.py      # Global base URL service
│   │   ├── keyword_service.py              # Keyword service
│   │   ├── source_url_service.py           # Source URL service
│   │   ├── content_repository_service.py   # Content repository service
│   │   ├── content_url_mapping_service.py  # Content URL mapping service
│   │   ├── content_summary_service.py      # Content summary service
│   │   ├── content_insight_service.py      # Content insight service
│   │   ├── content_implication_service.py  # Content implication service
│   │   ├── insight_comment_service.py      # Insight comment service
│   │   └── implication_comment_service.py  # Implication comment service
│   │
│   ├── repositories/                       # Data access layer
│   │   ├── __init__.py
│   │   ├── base_repository.py              # Base repository with common operations
│   │   ├── user_repository.py              # User data access
│   │   ├── project_details_repository.py   # Project details data access
│   │   ├── project_request_statistics_repository.py    # Project request stats repository
│   │   ├── project_modules_statistics_repository.py    # Project modules stats repository
│   │   ├── request_repository.py           # Request data access
│   │   ├── global_keyword_repository.py    # Global keyword repository
│   │   ├── global_base_url_repository.py   # Global base URL repository
│   │   ├── keyword_repository.py           # Keyword repository
│   │   ├── source_url_repository.py        # Source URL repository
│   │   ├── content_repository_repository.py # Content repository data access
│   │   ├── content_url_mapping_repository.py # Content URL mapping repository
│   │   ├── content_summary_repository.py   # Content summary repository
│   │   ├── content_insight_repository.py   # Content insight repository
│   │   ├── content_implication_repository.py # Content implication repository
│   │   ├── insight_comment_repository.py   # Insight comment repository
│   │   └── implication_comment_repository.py # Implication comment repository
│   │
│   ├── routes/                             # API route definitions
│   │   ├── __init__.py
│   │   ├── user_routes.py                  # User API routes
│   │   ├── project_details_routes.py       # Project details API routes
│   │   ├── project_request_statistics_routes.py       # Project request stats routes
│   │   ├── project_modules_statistics_routes.py       # Project modules stats routes
│   │   ├── request_routes.py               # Request API routes
│   │   ├── global_keyword_routes.py        # Global keyword API routes
│   │   ├── global_base_url_routes.py       # Global base URL API routes
│   │   ├── content_repository_routes.py    # Content repository API routes
│   │   ├── content_summary_routes.py       # Content summary API routes
│   │   ├── content_insight_routes.py       # Content insight API routes
│   │   ├── content_implication_routes.py   # Content implication API routes
│   │   ├── insight_comment_routes.py       # Insight comment API routes
│   │   └── implication_comment_routes.py   # Implication comment API routes
│   │
│   ├── schemas/                            # Pydantic schemas for validation
│   │   ├── __init__.py
│   │   ├── user.py                         # User schemas
│   │   ├── project_details.py              # Project details schemas
│   │   ├── project_request_statistics.py   # Project request statistics schemas
│   │   ├── project_modules_statistics.py   # Project modules statistics schemas
│   │   ├── request.py                      # Request schemas
│   │   ├── global_keyword.py               # Global keyword schemas
│   │   ├── global_base_url.py              # Global base URL schemas
│   │   ├── keyword.py                      # Keyword schemas
│   │   ├── source_url.py                   # Source URL schemas
│   │   ├── insight_comment.py              # Insight comment schemas
│   │   └── implication_comment.py          # Implication comment schemas
│   │
│   └── seeders/                            # Database seeding utilities
│       ├── __init__.py
│       ├── main_seeder.py                  # Main seeder orchestrator
│       ├── user_seeder.py                  # User data seeder
│       ├── project_details_seeder.py       # Project details seeder
│       ├── project_request_statistics_seeder.py        # Project request stats seeder
│       ├── project_modules_statistics_seeder.py        # Project modules stats seeder
│       ├── request_seeder.py               # Request data seeder
│       ├── global_keyword_seeder.py        # Global keyword seeder
│       ├── global_base_url_seeder.py       # Global base URL seeder
│       └── data_files/                     # Seeder data files
│           ├── set_1.json                  # Dataset 1
│           ├── set_2.json                  # Dataset 2
│           └── set_3.json                  # Dataset 3
│
├── migrations/                             # Alembic database migrations
│   ├── __pycache__/                        # Python bytecode cache
│   ├── env.py                              # Alembic environment configuration
│   ├── script.py.mako                      # Migration script template
│   └── versions/                           # Migration version files
│       ├── 001_create_users_table.py       # Create users table
│       ├── 002_create_projects_details_table.py        # Create project details table
│       ├── 003_create_project_request_statistics_table.py      # Create project request stats table
│       ├── 004_create_project_modules_statistics_table.py      # Create project modules stats table
│       ├── 005_create_requests_table.py    # Create requests table
│       ├── 006_create_global_keywords_table.py         # Create global keywords table
│       ├── 007_create_global_base_urls_table.py        # Create global base URLs table
│       ├── 008_create_keywords_table.py    # Create keywords table
│       ├── 009_create_source_urls_table.py # Create source URLs table
│       ├── 010_create_content_repository_table.py      # Create content repository table
│       ├── 011_create_process_handling_table.py        # Create process handling table
│       ├── 012_create_content_url_mapping_table.py     # Create content URL mapping table
│       ├── 013_create_content_summary_table.py         # Create content summary table
│       ├── 014_create_content_insight_table.py         # Create content insight table
│       ├── 015_create_content_implication_table.py     # Create content implication table
│       ├── 016_create_content_analysis_mapping_table.py # Create content analysis mapping table
│       ├── 017_create_insight_comment_table.py         # Create insight comment table
│       ├── 018_create_implication_comment_table.py     # Create implication comment table
│       ├── 019_create_implication_qa_table.py          # Create implication Q&A table
│       └── 020_create_insight_qa_table.py  # Create insight Q&A table
│
└── documentation/                          # Project documentation
    ├── DATABASE_PATTERNS.md               # Database design patterns
    ├── MIGRATIONS.md                       # Migration guidelines
    ├── SEEDERS.md                          # Seeder documentation
    ├── phase_1_PROJECT_BLUEPRINT.md       # Phase 1 project blueprint
    └── phase_2_DATABASE_CHANGES_SESSION_LOG.md # Phase 2 database changes log
```

## File Count Summary

- **Total Directories**: 12
- **Total Files**: 100+
- **Python Files**: 80+
- **Configuration Files**: 5
- **Documentation Files**: 6
- **Migration Files**: 20
- **Seeder Data Files**: 3

## Key Components

### 1. Core Application (`app/`)
- **Models**: 20 SQLAlchemy models for database tables
- **Controllers**: 14 request handlers for API endpoints
- **Services**: 16 business logic services
- **Repositories**: 16 data access layer components
- **Routes**: 13 API route definitions
- **Schemas**: 10 Pydantic validation schemas
- **Seeders**: 8 database seeding utilities

### 2. Database Management
- **Migrations**: 20 Alembic migration files for database schema
- **Seeders**: Comprehensive data seeding with JSON data files

### 3. Configuration & Setup
- **Environment**: Template and configuration files
- **Dependencies**: Requirements and setup files
- **Documentation**: Comprehensive project documentation

### 4. Utility Scripts
- Database seeding scripts
- Multi-dataset processing
- Project request flow creation

## Architecture Pattern

The project follows a **layered architecture** pattern:

1. **Routes Layer**: API endpoint definitions
2. **Controllers Layer**: Request handling and validation
3. **Services Layer**: Business logic implementation
4. **Repositories Layer**: Data access abstraction
5. **Models Layer**: Database entity definitions
6. **Schemas Layer**: Data validation and serialization

This structure ensures:
- **Separation of Concerns**: Each layer has a specific responsibility
- **Maintainability**: Easy to modify and extend
- **Testability**: Each layer can be tested independently
- **Scalability**: Can handle growing complexity 