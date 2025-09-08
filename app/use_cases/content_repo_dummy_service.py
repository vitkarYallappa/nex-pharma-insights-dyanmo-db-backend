"""
Content Repository Dummy Service
Generates dummy content data for projects using random JSON sets
Based on populate_content_data.py logic
"""

import json
import os
import hashlib
import random
from typing import Dict, List, Any, Optional
from urllib.parse import urlparse

from app.services.content_repository_service import ContentRepositoryService
from app.services.content_url_mapping_service import ContentUrlMappingService
from app.services.content_implication_service import ContentImplicationService
from app.services.content_insight_service import ContentInsightService
from app.services.content_summary_service import ContentSummaryService
from app.core.logging import get_logger

logger = get_logger("content_repo_dummy_service")

class ContentRepoDummyService:
    """Service to generate dummy content data for projects"""
    
    def __init__(self):
        self.content_repo_service = ContentRepositoryService()
        self.url_mapping_service = ContentUrlMappingService()
        self.implication_service = ContentImplicationService()
        self.insight_service = ContentInsightService()
        self.summary_service = ContentSummaryService()
        
        # Define the JSON file paths
        self.json_sets = [
            "app/use_cases/seeder/set_1.json",
            "app/use_cases/seeder/set_2.json", 
            "app/use_cases/seeder/set_3.json"
        ]
    
    def generate_content_hash(self, content: str) -> str:
        """Generate a hash for content"""
        return hashlib.md5(content.encode()).hexdigest()
    
    def parse_html_list(self, html_content: str) -> List[str]:
        """Parse HTML list content into individual items"""
        if not html_content:
            return []
        
        # Remove <ul> and </ul> tags
        content = html_content.replace('<ul>', '').replace('</ul>', '')
        
        # Split by <li> tags and clean up
        items = []
        for item in content.split('<li>'):
            if item.strip():
                # Remove </li> tag and clean up
                clean_item = item.replace('</li>', '').strip()
                if clean_item:
                    items.append(clean_item)
        
        return items
    
    def load_random_json_set(self) -> List[Dict[str, Any]]:
        """Randomly select and load one of the JSON data sets"""
        try:
            # Randomly select a JSON file
            selected_file = random.choice(self.json_sets)
            
            # Get the absolute path
            current_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            json_path = os.path.join(current_dir, selected_file)
            
            logger.info(f"Loading dummy data from: {selected_file}")
            
            with open(json_path, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
            
            logger.info(f"Loaded {len(json_data)} items from {selected_file}")
            return json_data
            
        except Exception as e:
            logger.error(f"Error loading JSON data: {str(e)}")
            # Return fallback data if file loading fails
            return self._get_fallback_data()
    
    def _get_fallback_data(self) -> List[Dict[str, Any]]:
        """Provide fallback data if JSON files are not available"""
        return [
            {
                "id": "FALLBACK_001",
                "title": "Pharmaceutical Innovation Drives Market Growth",
                "url": "https://example.com/pharma-innovation-growth",
                "insights": "<ul><li>Novel drug approvals increase by 25% year-over-year</li><li>Precision medicine approaches show improved patient outcomes</li><li>Digital health integration accelerates clinical development</li></ul>",
                "implications": "<ul><li>Market expansion creates new investment opportunities</li><li>Regulatory frameworks adapt to emerging technologies</li><li>Healthcare delivery models evolve with innovation</li></ul>",
                "summary": "Pharmaceutical innovation continues to drive significant market growth through novel therapeutic approaches and digital health integration."
            }
        ]
    
    async def create_content_repository_entry(self, project_id: str, request_id: str, 
                                            item_data: Dict[str, Any]) -> str:
        """Create content repository entry and return content_id"""
        try:
            # Generate content hash from title and URL
            content_text = f"{item_data['title']}{item_data['url']}"
            content_hash = self.generate_content_hash(content_text)
            
            content_repo = await self.content_repo_service.create_content_repository(
                request_id=request_id,
                project_id=project_id,
                canonical_url=item_data['url'],
                title=item_data['title'],
                content_hash=content_hash,
                source_type="web_article",
                relevance_type="primary",
                version=1,
                is_canonical=True
            )
            
            logger.info(f"Created content repository entry: {content_repo.pk}")
            return content_repo.pk
            
        except Exception as e:
            logger.error(f"Error creating content repository entry: {str(e)}")
            raise
    
    async def create_url_mapping_entry(self, content_id: str, url: str, title: str) -> str:
        """Create URL mapping entry and return url_id"""
        try:
            # Extract domain from URL
            parsed_url = urlparse(url)
            source_domain = parsed_url.netloc
            
            url_mapping = await self.url_mapping_service.create_content_url_mapping(
                discovered_url=url,
                title=title,
                content_id=content_id,
                source_domain=source_domain,
                is_canonical=True,
                dedup_confidence=None,
                dedup_method="content_hash"
            )
            
            logger.info(f"Created URL mapping entry: {url_mapping.pk}")
            return url_mapping.pk
            
        except Exception as e:
            logger.error(f"Error creating URL mapping entry: {str(e)}")
            raise
    
    async def create_insights(self, url_id: str, content_id: str, insights_html: str) -> List[str]:
        """Create insight entries and return list of insight_ids"""
        insight_ids = []
        
        try:
            insights_ids = []
            # insights_list = self.parse_html_list(insights_html)

            file_path = f"insights/{content_id}/insight_1.txt"

            insight = await self.insight_service.create_content_insight(
                url_id=url_id,
                content_id=content_id,
                insight_text=insights_html,
                insight_content_file_path=file_path,
                insight_category="analysis",
                confidence_score=None,
                version=1,
                is_canonical=True,
                preferred_choice=True,
                created_by="dummy_data_service"
            )

            logger.info(f"Created insight entry: {insight.pk}")
            insights_ids.append(insight.pk)
            return insights_ids
            
        except Exception as e:
            logger.error(f"Error creating insights: {str(e)}")
            raise
    
    async def create_implications(self, url_id: str, content_id: str, implications_html: str) -> List[str]:
        """Create implication entries and return list of implication_ids"""
        implication_ids = []
        
        try:
            # implications_list = self.parse_html_list(implications_html)

            file_path = f"implications/{content_id}/implication_1.txt"

            implication = await self.implication_service.create_content_implication(
                url_id=url_id,
                content_id=content_id,
                implication_text=implications_html,
                implication_content_file_path=file_path,
                implication_type="business_impact",
                priority_level="high",
                confidence_score=None,
                version=1,
                is_canonical=True,
                preferred_choice=True,
                created_by="dummy_data_service"
            )

            implication_ids.append(implication.pk)
            logger.info(f"Created implication entry: {implication.pk}")
            
            return implication_ids
            
        except Exception as e:
            logger.error(f"Error creating implications: {str(e)}")
            raise
    
    async def create_summary(self, url_id: str, content_id: str, summary_text: str) -> str:
        """Create summary entry and return summary_id"""
        try:
            # Create file path
            file_path = f"summaries/{content_id}/summary.txt"
            
            summary = await self.summary_service.create_content_summary(
                url_id=url_id,
                content_id=content_id,
                summary_text=summary_text,
                summary_content_file_path=file_path,
                confidence_score=None,
                version=1,
                is_canonical=True,
                preferred_choice=True,
                created_by="dummy_data_service"
            )
            
            logger.info(f"Created summary entry: {summary.pk}")
            return summary.pk
            
        except Exception as e:
            logger.error(f"Error creating summary: {str(e)}")
            raise
    
    async def generate_dummy_content(self, project_id: str, request_id: str) -> Dict[str, Any]:
        """
        Main method to generate dummy content for a project request
        Randomly selects a JSON set and populates all content tables
        """
        try:
            logger.info(f"Starting dummy content generation for project {project_id}, request {request_id}")
            
            # Load random JSON data set
            json_data = self.load_random_json_set()
            
            results = {
                "project_id": project_id,
                "request_id": request_id,
                "items_processed": 0,
                "content_entries": [],
                "total_insights": 0,
                "total_implications": 0,
                "total_summaries": 0,
                "errors": []
            }
            
            for i, item in enumerate(json_data):
                logger.info(f"Processing item {i+1}/{len(json_data)}: {item.get('id', 'Unknown ID')}")
                
                try:
                    # 1. Create content repository entry
                    content_id = await self.create_content_repository_entry(project_id, request_id, item)
                    
                    # 2. Create URL mapping entry
                    url_id = await self.create_url_mapping_entry(content_id, item['url'], item['title'])
                    
                    # 3. Create insights
                    insight_ids = []
                    if 'insights' in item and item['insights']:
                        insight_ids = await self.create_insights(url_id, content_id, item['insights'])
                        results["total_insights"] += len(insight_ids)
                    
                    # 4. Create implications
                    implication_ids = []
                    if 'implications' in item and item['implications']:
                        implication_ids = await self.create_implications(url_id, content_id, item['implications'])
                        results["total_implications"] += len(implication_ids)
                    
                    # 5. Create summary
                    summary_id = None
                    if 'summary' in item and item['summary']:
                        summary_id = await self.create_summary(url_id, content_id, item['summary'])
                        results["total_summaries"] += 1
                    
                    # Track successful entry
                    results["content_entries"].append({
                        "item_id": item.get('id'),
                        "content_id": content_id,
                        "url_id": url_id,
                        "insights_count": len(insight_ids),
                        "implications_count": len(implication_ids),
                        "has_summary": summary_id is not None
                    })
                    
                    results["items_processed"] += 1
                    logger.info(f"Successfully processed item {item['id']}")
                    
                except Exception as e:
                    error_msg = f"Error processing item {item.get('id', 'Unknown')}: {str(e)}"
                    logger.error(error_msg)
                    results["errors"].append(error_msg)
                    continue
            
            logger.info(f"Dummy content generation completed. Processed {results['items_processed']} items")
            logger.info(f"Created {results['total_insights']} insights, {results['total_implications']} implications, {results['total_summaries']} summaries")
            
            return results
            
        except Exception as e:
            logger.error(f"Error in dummy content generation: {str(e)}")
            raise
