"""
Project Request Creation Orchestrator Service
Handles the complete workflow for creating a project request with all related entities
Sequence: Project → Request → Keywords → Source URLs
"""

from typing import List, Dict, Any, Optional, Tuple, Union
from datetime import datetime
import uuid

from app.services.project_modules_statistics_service import ProjectModulesStatisticsService
from app.services.project_request_statistics_service import ProjectRequestStatisticsService
from app.services.project_service import ProjectService, ProjectNotFoundException
from app.services.requests_service import RequestsService, RequestsNotFoundException
from app.services.keywords_service import KeywordsService, KeywordsNotFoundException
from app.services.source_urls_service import SourceUrlsService, SourceUrlsNotFoundException
from app.models.project_model import ProjectModel
from app.models.requests_model import RequestsModel
from app.models.keywords_model import KeywordsModel
from app.models.source_urls_model import SourceUrlsModel
from app.models.project_request_statistics_model import ProjectRequestStatisticsModel
from app.models.project_modules_statistics_model import ProjectModulesStatisticsModel
from app.use_cases.content_repo_dummy_service import ContentRepoDummyService
from app.core.logging import get_logger
from app.core.exceptions import ValidationException

logger = get_logger("project_request_creation_orchestrator")

class ProjectRequestCreationException(Exception):
    """Exception raised during project request creation process"""
    pass

class ProjectRequestCreationOrchestrator:
    """
    Orchestrator service for creating complete project requests
    Handles the sequence: Project → Request → Keywords → Source URLs
    """
    
    def __init__(self):
        self.project_service = ProjectService()
        self.project_request_statistics_service =  ProjectRequestStatisticsService()
        self.project_modules_statistics_service = ProjectModulesStatisticsService()
        self.requests_service = RequestsService()
        self.keywords_service = KeywordsService()
        self.source_urls_service = SourceUrlsService()
        self.content_dummy_service = ContentRepoDummyService()
        self.logger = logger
    
    async def create_complete_project_request(
        self,
        project_data: Dict[str, Any],
        request_data: Dict[str, Any],
        keywords: List[str],
        base_urls: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Create a complete project request with all related entities
        
        Args:
            project_data: Project information (name, description, etc.)
            request_data: Request information (title, description, time_range, etc.)
            keywords: List of keyword strings
            base_urls: List of base URL dictionaries with source_type, source_name, url
            
        Returns:
            Dict containing all created entities with their IDs
            
        Raises:
            ProjectRequestCreationException: If any step in the process fails
        """
        
        orchestration_id = str(uuid.uuid4())[:8]
        self.logger.info(f"[{orchestration_id}] Starting project request creation orchestration")
        
        created_entities: Dict[str, Any] = {
            "project": None,
            "request": None,
            "keywords": [],
            "source_urls": [],
            "project_request_statistics": None,
            "project_modules_statistics": None,
            "dummy_content": None,
            "orchestration_id": orchestration_id,
            "created_at": datetime.utcnow().isoformat()
        }
        
        try:
            # Step 1: Create Project
            self.logger.info(f"[{orchestration_id}] Step 1: Creating project")
            project = await self._create_project(project_data, orchestration_id)
            created_entities["project"] = project.to_response()
            self.logger.info(f"[{orchestration_id}] Project created successfully: {project.pk}")
            
            # Step 2: Create Request
            self.logger.info(f"[{orchestration_id}] Step 2: Creating request")
            request = await self._create_request(request_data, project.pk, orchestration_id)
            created_entities["request"] = request.to_response()
            self.logger.info(f"[{orchestration_id}] Request created successfully: {request.pk}")
            
            # Step 3: Create Keywords (one by one)
            self.logger.info(f"[{orchestration_id}] Step 3: Creating {len(keywords)} keywords")
            created_keywords = await self._create_keywords(keywords, request.pk, orchestration_id)
            created_entities["keywords"] = [kw.to_response() for kw in created_keywords]
            self.logger.info(f"[{orchestration_id}] Keywords created successfully: {len(created_keywords)} items")
            
            # Step 4: Create Source URLs (one by one)
            self.logger.info(f"[{orchestration_id}] Step 4: Creating {len(base_urls)} source URLs")
            created_urls = await self._create_source_urls(base_urls, request.pk, orchestration_id)
            created_entities["source_urls"] = [url.to_response() for url in created_urls]
            self.logger.info(f"[{orchestration_id}] Source URLs created successfully: {len(created_urls)} items")
            
            # Step 5: Create Project Request Statistics (initial zero data)
            self.logger.info(f"[{orchestration_id}] Step 5: Creating project request statistics")
            request_stats = await self._create_project_request_statistics(project.pk, orchestration_id)
            created_entities["project_request_statistics"] = request_stats.to_response()
            self.logger.info(f"[{orchestration_id}] Project request statistics created: {request_stats.pk}")
            
            # Step 6: Create Project Modules Statistics (initial zero data)
            self.logger.info(f"[{orchestration_id}] Step 6: Creating project modules statistics")
            modules_stats = await self._create_project_modules_statistics(project.pk, orchestration_id)
            created_entities["project_modules_statistics"] = modules_stats.to_response()
            self.logger.info(f"[{orchestration_id}] Project modules statistics created: {modules_stats.pk}")
            
            # Step 7: Generate Dummy Content Data
            self.logger.info(f"[{orchestration_id}] Step 7: Generating dummy content data")
            try:
               pass
            except Exception as content_error:
                self.logger.warning(f"[{orchestration_id}] Dummy content generation failed: {str(content_error)}")
                # Don't fail the entire process if dummy content generation fails
                created_entities["dummy_content"] = {
                    "error": str(content_error),
                    "items_processed": 0,
                    "total_insights": 0,
                    "total_implications": 0,
                    "total_summaries": 0
                }
            
            # Success summary
            self.logger.info(
                f"[{orchestration_id}] Orchestration completed successfully - "
                f"Project: {project.pk}, Request: {request.pk}, "
                f"Keywords: {len(created_keywords)}, URLs: {len(created_urls)}, "
                f"Request Stats: {request_stats.pk}, Module Stats: {modules_stats.pk}"
            )
            
            return created_entities
            
        except Exception as e:
            self.logger.error(f"[{orchestration_id}] Orchestration failed: {str(e)}")
            # Note: In a production system, you might want to implement rollback logic here
            # For now, we'll let the caller handle cleanup if needed
            raise ProjectRequestCreationException(f"Project request creation failed: {str(e)}")
    
    async def _create_project(self, project_data: Dict[str, Any], orchestration_id: str) -> ProjectModel:
        """Create project with validation and logging"""
        try:
            self.logger.debug(f"[{orchestration_id}] Creating project with data: {project_data}")
            
            # Validate required fields
            if not project_data.get("name"):
                raise ValidationException("Project name is required")
            if not project_data.get("created_by"):
                raise ValidationException("Project creator is required")
            
            project = await self.project_service.create_project(
                name=project_data["name"],
                created_by=project_data["created_by"],
                description=project_data.get("description"),
                status=project_data.get("status", "active"),
                project_metadata=project_data.get("project_metadata", {}),
                module_config=project_data.get("module_config", {})
            )
            
            self.logger.debug(f"[{orchestration_id}] Project created with ID: {project.pk}")
            return project
            
        except Exception as e:
            self.logger.error(f"[{orchestration_id}] Project creation failed: {str(e)}")
            raise
    
    async def _create_request(self, request_data: Dict[str, Any], project_id: str, orchestration_id: str) -> RequestsModel:
        """Create request with validation and logging"""
        try:
            self.logger.debug(f"[{orchestration_id}] Creating request for project {project_id}")
            
            # Validate required fields
            if not request_data.get("title"):
                raise ValidationException("Request title is required")
            if not request_data.get("created_by"):
                raise ValidationException("Request creator is required")
            
            request = await self.requests_service.create_request(
                project_id=project_id,
                title=request_data["title"],
                created_by=request_data["created_by"],
                description=request_data.get("description"),
                time_range=request_data.get("time_range", {}),
                priority=request_data.get("priority", "medium"),
                status=request_data.get("status", "pending"),
                estimated_completion=request_data.get("estimated_completion")
            )
            
            self.logger.debug(f"[{orchestration_id}] Request created with ID: {request.pk}")
            return request
            
        except Exception as e:
            self.logger.error(f"[{orchestration_id}] Request creation failed: {str(e)}")
            raise
    
    async def _create_keywords(self, keywords: List[str], request_id: str, orchestration_id: str) -> List[KeywordsModel]:
        """Create keywords one by one with validation and logging"""
        created_keywords = []
        
        try:
            self.logger.debug(f"[{orchestration_id}] Creating keywords for request {request_id}")
            
            for i, keyword_text in enumerate(keywords, 1):
                if not keyword_text or not keyword_text.strip():
                    self.logger.warning(f"[{orchestration_id}] Skipping empty keyword at position {i}")
                    continue
                
                try:
                    keyword = await self.keywords_service.create_keyword(
                        keyword=keyword_text.strip(),
                        request_id=request_id,
                        keyword_type="user_defined"  # Default type for user-provided keywords
                    )
                    created_keywords.append(keyword)
                    self.logger.debug(f"[{orchestration_id}] Keyword {i}/{len(keywords)} created: {keyword.pk} - '{keyword_text}'")
                    
                except Exception as keyword_error:
                    self.logger.error(f"[{orchestration_id}] Failed to create keyword '{keyword_text}': {str(keyword_error)}")
                    # Continue with other keywords instead of failing the entire process
                    continue
            
            self.logger.debug(f"[{orchestration_id}] Keywords creation completed: {len(created_keywords)}/{len(keywords)} successful")
            return created_keywords
            
        except Exception as e:
            self.logger.error(f"[{orchestration_id}] Keywords creation process failed: {str(e)}")
            raise
    
    async def _create_source_urls(self, base_urls: List[Dict[str, Any]], request_id: str, orchestration_id: str) -> List[SourceUrlsModel]:
        """Create source URLs one by one with validation and logging"""
        created_urls = []
        
        try:
            self.logger.debug(f"[{orchestration_id}] Creating source URLs for request {request_id}")
            
            for i, url_data in enumerate(base_urls, 1):
                if not url_data.get("url") or not url_data["url"].strip():
                    self.logger.warning(f"[{orchestration_id}] Skipping empty URL at position {i}")
                    continue
                
                try:
                    source_url = await self.source_urls_service.create_source_url(
                        request_id=request_id,
                        url=url_data["url"].strip(),
                        source_name=url_data.get("source_name"),
                        source_type=url_data.get("source_type"),
                        country_region=url_data.get("country_region"),
                        is_active=url_data.get("is_active", True),
                        url_metadata=url_data.get("url_metadata", {})
                    )
                    created_urls.append(source_url)
                    self.logger.debug(f"[{orchestration_id}] Source URL {i}/{len(base_urls)} created: {source_url.pk} - '{url_data['url']}'")
                    
                except Exception as url_error:
                    self.logger.error(f"[{orchestration_id}] Failed to create source URL '{url_data.get('url', 'unknown')}': {str(url_error)}")
                    # Continue with other URLs instead of failing the entire process
                    continue
            
            self.logger.debug(f"[{orchestration_id}] Source URLs creation completed: {len(created_urls)}/{len(base_urls)} successful")
            return created_urls
            
        except Exception as e:
            self.logger.error(f"[{orchestration_id}] Source URLs creation process failed: {str(e)}")
            raise
    
    async def create_project_request_from_payload(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convenience method to create project request from a single payload
        Extracts and organizes data for the orchestration process
        
        Args:
            payload: Complete payload containing project, request, keywords, and base_urls data
            
        Returns:
            Dict containing all created entities
        """
        
        try:
            # Check if we should use existing project or create new one
            project_id = payload.get("project_id")
            
            # Extract project data (only used if creating new project)
            project_data = {
                "name": payload.get("title", "Unnamed Project"),  # Use title as project name
                "description": payload.get("description"),
                "created_by": payload.get("created_by"),
                "status": "active",
                "project_metadata": {
                    "source": "project_request_creation",
                    "priority": payload.get("priority", "medium")
                },
                "module_config": {}
            }
            
            # Extract request data
            request_data = {
                "title": payload.get("title"),
                "description": payload.get("description"),
                "created_by": payload.get("created_by"),
                "time_range": payload.get("time_range", {}),
                "priority": payload.get("priority", "medium"),
                "status": "pending"
            }
            
            # Extract keywords and base_urls
            keywords = payload.get("keywords", [])
            base_urls = payload.get("base_urls", [])
            
            # Validate payload
            if not payload.get("title"):
                raise ValidationException("Title is required")
            if not payload.get("created_by"):
                raise ValidationException("Creator ID is required")
            
            # Execute orchestration
            if project_id:
                # Use existing project
                return await self.create_request_for_existing_project(
                    project_id=project_id,
                    request_data=request_data,
                    keywords=keywords,
                    base_urls=base_urls
                )
            else:
                # Create new project and request
                return await self.create_complete_project_request(
                    project_data=project_data,
                    request_data=request_data,
                    keywords=keywords,
                    base_urls=base_urls
                )
            
        except Exception as e:
            self.logger.error(f"Failed to process payload: {str(e)}")
            raise ProjectRequestCreationException(f"Invalid payload: {str(e)}")
    
    async def create_request_for_existing_project(
        self,
        project_id: str,
        request_data: Dict[str, Any],
        keywords: List[str],
        base_urls: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Create a request for an existing project with keywords and source URLs
        
        Args:
            project_id: ID of existing project
            request_data: Request information (title, description, time_range, etc.)
            keywords: List of keyword strings
            base_urls: List of base URL dictionaries with source_type, source_name, url
            
        Returns:
            Dict containing all created entities with their IDs
            
        Raises:
            ProjectRequestCreationException: If any step in the process fails
        """
        
        orchestration_id = str(uuid.uuid4())[:8]
        self.logger.info(f"[{orchestration_id}] Starting request creation for existing project: {project_id}")
        
        created_entities: Dict[str, Any] = {
            "project": None,
            "request": None,
            "keywords": [],
            "source_urls": [],
            "project_request_statistics": None,
            "project_modules_statistics": None,
            "orchestration_id": orchestration_id,
            "created_at": datetime.utcnow().isoformat()
        }
        
        try:
            # Step 1: Verify project exists and get project info
            self.logger.info(f"[{orchestration_id}] Step 1: Verifying existing project")
            project = await self.project_service.get_project_by_id(project_id)
            created_entities["project"] = project.to_response()
            self.logger.info(f"[{orchestration_id}] Project verified: {project.pk}")
            
            # Step 2: Create Request
            self.logger.info(f"[{orchestration_id}] Step 2: Creating request")
            request = await self._create_request(request_data, project.pk, orchestration_id)
            created_entities["request"] = request.to_response()
            self.logger.info(f"[{orchestration_id}] Request created successfully: {request.pk}")
            
            # Step 3: Create Keywords (one by one)
            self.logger.info(f"[{orchestration_id}] Step 3: Creating {len(keywords)} keywords")
            created_keywords = await self._create_keywords(keywords, request.pk, orchestration_id)
            created_entities["keywords"] = [kw.to_response() for kw in created_keywords]
            self.logger.info(f"[{orchestration_id}] Keywords created successfully: {len(created_keywords)} items")
            
            # Step 4: Create Source URLs (one by one)
            self.logger.info(f"[{orchestration_id}] Step 4: Creating {len(base_urls)} source URLs")
            created_urls = await self._create_source_urls(base_urls, request.pk, orchestration_id)
            created_entities["source_urls"] = [url.to_response() for url in created_urls]
            self.logger.info(f"[{orchestration_id}] Source URLs created successfully: {len(created_urls)} items")
            
            # Step 5: Create Project Request Statistics (initial zero data) - Note: Only if not exists
            self.logger.info(f"[{orchestration_id}] Step 5: Creating/updating project request statistics")
            request_stats = await self._create_or_update_project_request_statistics(project.pk, orchestration_id)
            created_entities["project_request_statistics"] = request_stats.to_response()
            self.logger.info(f"[{orchestration_id}] Project request statistics handled: {request_stats.pk}")
            
            # Step 6: Create Project Modules Statistics (initial zero data) - Note: Only if not exists
            self.logger.info(f"[{orchestration_id}] Step 6: Creating/updating project modules statistics")
            modules_stats = await self._create_or_update_project_modules_statistics(project.pk, orchestration_id)
            created_entities["project_modules_statistics"] = modules_stats.to_response()
            self.logger.info(f"[{orchestration_id}] Project modules statistics handled: {modules_stats.pk}")
            
            # Success summary
            self.logger.info(
                f"[{orchestration_id}] Request creation for existing project completed successfully - "
                f"Project: {project.pk}, Request: {request.pk}, "
                f"Keywords: {len(created_keywords)}, URLs: {len(created_urls)}, "
                f"Request Stats: {request_stats.pk}, Module Stats: {modules_stats.pk}"
            )
            
            return created_entities
            
        except ProjectNotFoundException as e:
            self.logger.error(f"[{orchestration_id}] Request creation for existing project failed: {str(e)}")
            raise ProjectRequestCreationException(f"Request creation for existing project failed: {str(e)}")
        except Exception as e:
            self.logger.error(f"[{orchestration_id}] Request creation for existing project failed: {str(e)}")
            raise ProjectRequestCreationException(f"Request creation for existing project failed: {str(e)}")
    
    async def _create_project_request_statistics(self, project_id: str, orchestration_id: str) -> ProjectRequestStatisticsModel:
        """Create initial project request statistics with zero data"""
        try:
            self.logger.debug(f"[{orchestration_id}] Creating project request statistics for project {project_id}")
            
            # Create initial statistics with zero values
            request_stats = await self.project_request_statistics_service.create_project_request_statistics(
                project_id=project_id,
                total_requests=1,  # Starting with 1 since we just created a request
                completed_requests=0,
                pending_requests=1,  # The request we just created is pending
                failed_requests=0,
                average_processing_time=0,
                last_activity_at=datetime.utcnow().isoformat(),
                statistics_metadata={
                    "created_by_orchestrator": True,
                    "orchestration_id": orchestration_id
                }
            )
            
            self.logger.debug(f"[{orchestration_id}] Project request statistics created with ID: {request_stats.pk}")
            return request_stats
            
        except Exception as e:
            self.logger.error(f"[{orchestration_id}] Project request statistics creation failed: {str(e)}")
            raise
    
    async def _create_project_modules_statistics(self, project_id: str, orchestration_id: str) -> ProjectModulesStatisticsModel:
        """Create initial project modules statistics with zero data"""
        try:
            self.logger.debug(f"[{orchestration_id}] Creating project modules statistics for project {project_id}")
            
            # Create initial statistics with zero values
            modules_stats = await self.project_modules_statistics_service.create_project_modules_statistics(
                project_id=project_id,
                total_insights=0,  # Starting with zero insights
                total_implication=0  # Starting with zero implications
            )
            
            self.logger.debug(f"[{orchestration_id}] Project modules statistics created with ID: {modules_stats.pk}")
            return modules_stats
            
        except Exception as e:
            self.logger.error(f"[{orchestration_id}] Project modules statistics creation failed: {str(e)}")
            raise
    
    async def _create_or_update_project_request_statistics(self, project_id: str, orchestration_id: str) -> ProjectRequestStatisticsModel:
        """Create or update project request statistics for existing projects"""
        try:
            self.logger.debug(f"[{orchestration_id}] Checking project request statistics for existing project {project_id}")
            
            # Try to get existing statistics first
            try:
                existing_stats = await self.project_request_statistics_service.get_project_request_statistics_by_query(
                    project_id=project_id,
                    limit=1
                )
                
                if existing_stats:
                    # Update existing statistics (increment total_requests and pending_requests)
                    stats = existing_stats[0]
                    current_total = stats.total_requests or 0
                    current_pending = stats.pending_requests or 0
                    
                    updated_stats = await self.project_request_statistics_service.update_project_request_statistics(
                        stats.pk,
                        {
                            "total_requests": current_total + 1,
                            "pending_requests": current_pending + 1,
                            "last_activity_at": datetime.utcnow().isoformat()
                        }
                    )
                    
                    self.logger.debug(f"[{orchestration_id}] Updated existing project request statistics: {updated_stats.pk}")
                    return updated_stats
                    
            except Exception:
                # If no existing statistics found, create new ones
                pass
            
            # Create new statistics if none exist
            return await self._create_project_request_statistics(project_id, orchestration_id)
            
        except Exception as e:
            self.logger.error(f"[{orchestration_id}] Project request statistics handling failed: {str(e)}")
            raise
    
    async def _create_or_update_project_modules_statistics(self, project_id: str, orchestration_id: str) -> ProjectModulesStatisticsModel:
        """Create or update project modules statistics for existing projects"""
        try:
            self.logger.debug(f"[{orchestration_id}] Checking project modules statistics for existing project {project_id}")
            
            # Try to get existing statistics first
            try:
                existing_stats = await self.project_modules_statistics_service.get_project_modules_statistics_by_query(
                    project_id=project_id,
                    limit=1
                )
                
                if existing_stats:
                    # Return existing statistics (no need to update for modules stats)
                    stats = existing_stats[0]
                    self.logger.debug(f"[{orchestration_id}] Using existing project modules statistics: {stats.pk}")
                    return stats
                    
            except Exception:
                # If no existing statistics found, create new ones
                pass
            
            # Create new statistics if none exist
            return await self._create_project_modules_statistics(project_id, orchestration_id)
            
        except Exception as e:
            self.logger.error(f"[{orchestration_id}] Project modules statistics handling failed: {str(e)}")
            raise
