"""
Insights Regenerate Service
Handles regeneration of insights with version management and QA creation
"""

from typing import Dict, Any, Optional
from app.services.content_insight_service import ContentInsightService
from app.services.insight_qa_service import InsightQaService
from app.core.logging import get_logger
from app.core.exceptions import ValidationException

logger = get_logger("insights_regenerate_service")

class InsightsRegenerateService:
    """Service for regenerating insights with version management"""
    
    def __init__(self):
        self.insight_service = ContentInsightService()
        self.qa_service = InsightQaService()
        self.logger = logger
    
    async def regenerate_insight(
        self,
        content_id: str,
        metadata_field1: Optional[str] = None,
        metadata_field2: Optional[str] = None,
        metadata_field3: Optional[str] = None,
        question_text: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Regenerate insight for given content with version management
        
        Args:
            content_id: The content ID to regenerate insight for
            metadata_field1: Additional metadata field 1
            metadata_field2: Additional metadata field 2
            metadata_field3: Additional metadata field 3
            question_text: Optional question text for QA generation
            
        Returns:
            Dict containing the regenerated insight and QA data
        """
        try:
            self.logger.info(f"Starting insight regeneration for content_id: {content_id}")
            
            # Step 1: Count existing insights for this content to determine version
            existing_insights = await self.insight_service.get_all_by_query(
                query_filters={"content_id": content_id}
            )
            
            current_count = len(existing_insights)
            new_version = current_count + 1
            
            self.logger.info(f"Found {current_count} existing insights, creating version {new_version}")
            
            # Step 2: Create new insight with incremented version
            # We need to get URL ID from existing insights or create a default one
            url_id = existing_insights[0].url_id if existing_insights else "default-url-id"
            
            # Create file path for the new insight
            file_path = f"insights/{content_id}/regenerated_insight_v{new_version}.txt"

            regenerate_text = question_text.strip()

            # Prepare metadata
            insight_metadata = {}
            if metadata_field1:
                insight_metadata["field1"] = metadata_field1
            if metadata_field2:
                insight_metadata["field2"] = metadata_field2
            if metadata_field3:
                insight_metadata["field3"] = metadata_field3
            
            # Create the new insight
            new_insight = await self.insight_service.create_content_insight(
                url_id=url_id,
                content_id=content_id,
                insight_text=regenerate_text,
                insight_content_file_path=file_path,
                insight_category="regenerated",
                confidence_score=None,
                version=new_version,
                is_canonical=True,
                preferred_choice=True,
                created_by="regenerate_service"
            )
            
            self.logger.info(f"Created new insight: {new_insight.pk} with version {new_version}")
            
            # Step 3: Generate QA if question text is provided
            qa_entry = None
            if question_text and question_text.strip():
                # Generate answer (for now, we'll create a simple answer based on the insight)
                generated_answer = f"Based on the regenerated insight: {regenerate_text[:200]}..."
                
                qa_entry = await self.qa_service.create_insight_qa(
                    insight_id=new_insight.pk,
                    question=question_text.strip(),
                    answer=generated_answer,
                    question_type="regeneration",
                    qa_metadata={
                        "regeneration_version": new_version,
                        "content_id": content_id,
                        **insight_metadata
                    }
                )
                
                self.logger.info(f"Created QA entry: {qa_entry.pk}")
            
            # Step 4: Prepare response
            result = {
                "regenerated_insight": new_insight.to_response(),
                "version": new_version,
                "previous_insights_count": current_count,
                "qa_entry": qa_entry.to_response() if qa_entry else None,
                "metadata": insight_metadata,
                "content_id": content_id
            }
            
            self.logger.info(f"Insight regeneration completed successfully for content_id: {content_id}")
            return result
            
        except ValidationException:
            raise
        except Exception as e:
            self.logger.error(f"Insight regeneration failed for content_id {content_id}: {str(e)}")
            raise
