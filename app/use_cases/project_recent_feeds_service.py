"""
Project Recent Feeds Service - Use case for fetching recent content summary data
Fetches latest 3 projects, then for each project gets latest 2 content summaries,
and counts respective insights and implications
"""

from typing import List, Dict, Any, Optional
from app.services.project_service import ProjectService
from app.services.content_repository_service import ContentRepositoryService
from app.services.content_summary_service import ContentSummaryService
from app.services.content_insight_service import ContentInsightService
from app.services.content_implication_service import ContentImplicationService
from app.core.logging import get_logger
from app.core.exceptions import ValidationException

logger = get_logger("project_recent_feeds_service")

class ProjectRecentFeedsService:
    """Service for fetching recent content feeds with insights and implications count"""
    
    def __init__(self):
        self.project_service = ProjectService()
        self.content_repository_service = ContentRepositoryService()
        self.content_summary_service = ContentSummaryService()
        self.content_insight_service = ContentInsightService()
        self.content_implication_service = ContentImplicationService()
        self.logger = logger
    
    async def get_recent_feeds(self) -> Dict[str, Any]:
        """
        Get recent content feeds:
        1. Fetch latest 3 projects
        2. For each project, get latest 2 content summaries
        3. Count insights and implications for each content summary
        
        Returns:
            Dict containing projects with their content summaries and counts
        """
        try:
            self.logger.info("Starting recent feeds retrieval")
            
            # Step 1: Get latest 3 projects
            projects = await self.project_service.get_projects_by_query(limit=3)
            
            if not projects:
                self.logger.info("No projects found")
                return {
                    "projects": [],
                    "total_projects": 0,
                    "message": "No projects found"
                }
            
            recent_feeds = []
            
            # Step 2: Process each project
            for project in projects:
                project_id = project.get("pk") if hasattr(project, 'get') else project.pk
                project_dict = project.to_dict() if hasattr(project, 'to_dict') else project
                
                self.logger.info(f"Processing project: {project_id}")
                
                # Get content repository entries for this project (latest 2)
                # Note: DynamoDB Limit applies to items examined, not filtered results
                # So we query without limit and take the first 2 results
                query_filters = {"project_id": project_id}
                self.logger.info(f"Querying content repository with filters: {query_filters}")
                all_content_entries = await self.content_repository_service.get_all_by_query(
                    query_filters=query_filters,
                    limit=2
                )
                # Take only the first 2 entries
                content_entries = all_content_entries[:2]
                self.logger.info(f"Content repository query returned {len(all_content_entries)} total entries, using first {len(content_entries)} for project {project_id}")
                
                project_feed = {
                    "project_id": project_id,
                    "project_name": project_dict.get("name"),
                    "project_description": project_dict.get("description"),
                    "project_status": project_dict.get("status"),
                    "created_at": project_dict.get("created_at"),
                    "content_summaries": [],
                    "total_content_entries": len(content_entries)
                }
                
                # Step 3: Process each content entry
                for content_entry in content_entries:
                    content_id = content_entry.get("pk") if hasattr(content_entry, 'get') else content_entry.pk
                    content_dict = content_entry.to_dict() if hasattr(content_entry, 'to_dict') else content_entry
                    
                    self.logger.info(f"Processing content: {content_id} for project: {project_id}")
                    
                    # Get content summaries for this content
                    summaries = await self.content_summary_service.get_all_by_query(
                        query_filters={"content_id": content_id},
                        limit=2
                    )
                    
                    self.logger.info(f"Found {len(summaries)} summaries for content: {content_id}")
                    
                    for summary in summaries:
                        summary_id = summary.get("pk") if hasattr(summary, 'get') else summary.pk
                        summary_dict = summary.to_dict() if hasattr(summary, 'to_dict') else summary
                        
                        # Count insights for this content
                        insights = await self.content_insight_service.get_all_by_query(
                            query_filters={"content_id": content_id}
                        )
                        insights_count = len(insights)
                        
                        # Count implications for this content
                        implications = await self.content_implication_service.get_all_by_query(
                            query_filters={"content_id": content_id}
                        )
                        implications_count = len(implications)
                        
                        summary_feed ={
                                **content_dict,
                                "project_title": project_dict.get("name"),
                                "insights_count": insights_count,
                                "implications_count": implications_count
                            }
                        
                        # project_feed["content_summaries"].append(summary_feed)
                        recent_feeds.append(summary_feed)
                

            
            result = {
                "projects": recent_feeds,
                "total_projects": len(recent_feeds),
                "message": f"Retrieved recent feeds for {len(recent_feeds)} projects"
            }
            
            self.logger.info(f"Recent feeds retrieval completed: {len(recent_feeds)} projects processed")
            return result
            
        except ValidationException:
            raise
        except Exception as e:
            self.logger.error(f"Recent feeds retrieval failed: {str(e)}")
            raise
    
    async def get_project_recent_summary_with_counts(self, project_id: str, limit: int = 2) -> Dict[str, Any]:
        """
        Get recent content summaries for a specific project with insights/implications count
        
        Args:
            project_id: The project ID to fetch summaries for
            limit: Number of recent summaries to fetch (default: 2)
            
        Returns:
            Dict containing project info and content summaries with counts
        """
        try:
            if not project_id or not project_id.strip():
                raise ValidationException("Project ID is required")
            
            self.logger.info(f"Getting recent summaries for project: {project_id}")
            
            # Get project details
            project = await self.project_service.get_project_by_id(project_id.strip())
            project_dict = project.to_dict() if hasattr(project, 'to_dict') else project
            
            # Get content repository entries for this project
            # Note: DynamoDB Limit applies to items examined, not filtered results
            all_content_entries = await self.content_repository_service.get_all_by_query(
                query_filters={"project_id": project_id.strip()},
                limit=None
            )
            # Take only the requested number of entries
            content_entries = all_content_entries[:limit] if limit else all_content_entries
            
            summaries_with_counts = []
            
            for content_entry in content_entries:
                content_id = content_entry.get("pk") if hasattr(content_entry, 'get') else content_entry.pk
                content_dict = content_entry.to_dict() if hasattr(content_entry, 'to_dict') else content_entry
                
                # Get content summaries for this content
                summaries = await self.content_summary_service.get_all_by_query(
                    query_filters={"content_id": content_id},
                    limit=1  # Get latest summary for each content
                )
                
                for summary in summaries:
                    summary_dict = summary.to_dict() if hasattr(summary, 'to_dict') else summary
                    
                    # Count insights and implications
                    insights = await self.content_insight_service.get_all_by_query(
                        query_filters={"content_id": content_id}
                    )
                    implications = await self.content_implication_service.get_all_by_query(
                        query_filters={"content_id": content_id}
                    )
                    
                    summary_with_count = {
                        "summary_id": summary.get("pk") if hasattr(summary, 'get') else summary.pk,
                        "content_id": content_id,
                        "content_title": content_dict.get("title"),
                        "content_url": content_dict.get("canonical_url"),
                        "summary_text": summary_dict.get("summary_text"),
                        "confidence_score": summary_dict.get("confidence_score"),
                        "created_at": summary_dict.get("created_at"),
                        "insights_count": len(insights),
                        "implications_count": len(implications),
                        "total_analysis_count": len(insights) + len(implications)
                    }
                    
                    summaries_with_counts.append(summary_with_count)
            
            result = {
                "project": {
                    "project_id": project_id,
                    "name": project_dict.get("name"),
                    "description": project_dict.get("description"),
                    "status": project_dict.get("status"),
                    "created_at": project_dict.get("created_at")
                },
                "content_summaries": summaries_with_counts,
                "total_summaries": len(summaries_with_counts),
                "message": f"Retrieved {len(summaries_with_counts)} recent summaries for project {project_id}"
            }
            
            self.logger.info(f"Retrieved {len(summaries_with_counts)} summaries for project {project_id}")
            return result
            
        except ValidationException:
            raise
        except Exception as e:
            self.logger.error(f"Get project recent summaries failed: {str(e)}")
            raise
