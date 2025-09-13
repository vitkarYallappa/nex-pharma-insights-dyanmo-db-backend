"""
Insights Regenerate Service
Handles regeneration of insights with version management and QA creation
"""
import uuid
from typing import Dict, Any, Optional
from app.services.content_insight_service import ContentInsightService
from app.services.insight_qa_service import InsightQaService
from app.services.content_summary_service import ContentSummaryService
from app.use_cases.insights_api_client import InsightsApiClient, InsightsApiClientException
from app.core.logging import get_logger
from app.core.exceptions import ValidationException

logger = get_logger("insights_regenerate_service")


class InsightsRegenerateService:
    """Service for regenerating insights with version management"""

    def __init__(self):
        self.insight_service = ContentInsightService()
        self.qa_service = InsightQaService()
        self.summary_service = ContentSummaryService()
        self.api_client = InsightsApiClient()
        self.logger = logger

    async def regenerate_insight(
            self,
            content_id: str,
            question_text: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Regenerate insight for given content with version management
        Args:
            content_id: The content ID to regenerate insight for

            
        Returns:
            Dict containing the regenerated insight and QA data
        """
        generated_uuid = str(uuid.uuid4())
        try:
            self.logger.info(f"Starting insight regeneration for content_id: {content_id}")

            # Step 1: Fetch summary details from content summary by content_id
            self.logger.info(f"Fetching summary details for content_id: {content_id}")
            summary_entries = await self.summary_service.get_all_by_query(
                query_filters={"content_id": content_id},
                limit=1  # Get the most recent or preferred summary
            )

            if not summary_entries:
                self.logger.warning(f"No summary found for content_id: {content_id}")
                summary_text = f"No summary available for content_id: {content_id}"
            else:
                # Use the first (most relevant) summary
                summary_text = summary_entries[0].summary_text
                self.logger.info(f"Found summary for content_id: {content_id}, length: {len(summary_text)}")

            # Step 2: Call 8005 API with summary text and metadata fields
            self.logger.info(f"Making API call to regenerate insights for content_id: {content_id}")
            try:
                # api_response = await self.api_client.regenerate_insight_request(
                #     content_id=content_id,
                #     summary_text=summary_text,
                #     question_text=question_text
                # )

                # Extract regenerated text from API response
                regenerate_text = summary_text
                # api_response.get("regenerated_insight", "No insight generated"))
                self.logger.info(f"Successfully received regenerated insight from API for content_id: {content_id}")

            except InsightsApiClientException as e:
                self.logger.error(f"API call failed for content_id {content_id}: {str(e)}")
                # Fallback to default text if API fails
                regenerate_text = f"API call failed for content_id: {content_id}. Using fallback insight generation."

            # Step 3: Generate QA if question text is provided
            qa_entry = None
            if question_text and question_text.strip():
                # Generate answer (for now, we'll create a simple answer based on the insight)
                generated_answer = f"Based on the regenerated insight: {regenerate_text[:200]}..."
                qa_entry = await self.qa_service.create_insight_qa(
                    insight_id=generated_uuid,
                    question=question_text.strip(),
                    answer=generated_answer,
                    question_type="regeneration",
                    qa_metadata={
                        "content_id": content_id
                    }
                )

                self.logger.info(f"Created QA entry: {qa_entry.pk}")

            # Step 4: Prepare response
            result = {
                "generated_id": generated_uuid,
                "regenerated_text": regenerate_text,
                "content_id": content_id,
                "status": "draft"
            }

            self.logger.info(f"Insight regeneration completed successfully for content_id: {content_id}")
            return result

        except ValidationException:
            raise
        except Exception as e:
            self.logger.error(f"Insight regeneration failed for content_id {content_id}: {str(e)}")
            raise

    async def save_regenerate_insight(
            self,
            content_id: str,
            insight_id: str
    ) -> Dict[str, Any]:
        """
        Save regenerated insight by fetching QA details and adding to insights table

        Args:
            content_id: The content ID to regenerate insight for
            insight_id: The insight ID to fetch QA details for

        Returns:
            Dict containing the saved insight and QA data
        """
        try:
            self.logger.info(f"Starting save regenerate insight for content_id: {content_id}, insight_id: {insight_id}")

            # Step 1: Fetch QA details based on insight_id
            qa_details = await self.qa_service.get_all_insight_qa(insight_id=insight_id)

            if not qa_details:
                self.logger.warning(f"No QA details found for insight_id: {insight_id}")
                qa_text = "No QA details available"
                qa_metadata = {}
            else:
                # Combine all QA details into insight text
                qa_text_parts = []
                qa_metadata = {"qa_count": len(qa_details), "qa_entries": []}

                for qa in qa_details:
                    qa_text_parts.append(f"Q: {qa.question}\nA: {qa.answer}")
                    qa_metadata["qa_entries"].append({
                        "qa_id": qa.pk,
                        "question": qa.question,
                        "answer": qa.answer,
                        "question_type": qa.question_type
                    })

                qa_text = "\n\n".join(qa_text_parts)
                self.logger.info(f"Found {len(qa_details)} QA entries for insight_id: {insight_id}")

            # Step 2: Get existing insights to calculate version
            existing_insights = await self.insight_service.get_all_by_query(
                query_filters={"content_id": content_id}
            )

            current_count = len(existing_insights)
            new_version = current_count + 1
            self.logger.info(
                f"Found {current_count} existing insights for content_id: {content_id}, creating version {new_version}")

            # Step 3: Update all existing insights to set preferred_choice=False
            updated_count = 0
            for existing_insight in existing_insights:
                if existing_insight.preferred_choice:  # Only update if currently True
                    await self.insight_service.update_content_insight(
                        insight_id=existing_insight.pk,
                        update_data={"preferred_choice": False}
                    )
                    updated_count += 1

            self.logger.info(
                f"Updated {updated_count} existing insights to set preferred_choice=False for content_id: {content_id}")

            # Step 4: Create insight entry in insights table
            # Note: We need url_id and insight_content_file_path for the insight creation
            # For now, using placeholder values - these should be provided or fetched from content
            insight_entry = await self.insight_service.create_content_insight(
                url_id="regenerated_url_" + content_id,  # Placeholder - should be actual URL ID
                content_id=content_id,
                insight_text=qa_text,
                insight_content_file_path=f"insights/regenerated_{insight_id}.txt",  # Placeholder path
                insight_category="regenerated",
                confidence_score=0.8,  # Default confidence for regenerated insights
                version=new_version,
                is_canonical=False,
                preferred_choice=True,
                created_by="insights_regenerate_service"
            )

            # Step 5: Prepare response
            result = {
                "insight_id": insight_entry.pk,
                "content_id": content_id,
                "insight_text": qa_text,
                "version": new_version,
                "status": "saved"
            }

            self.logger.info(f"Insight regeneration completed successfully for content_id: {content_id}")
            return result

        except ValidationException:
            raise
        except Exception as e:
            self.logger.error(f"Insight regeneration failed for content_id {content_id}: {str(e)}")
            raise

    async def update_insight_status(
            self,
            content_id: str,
            insight_id: str
    ) -> Dict[str, Any]:
        """
        Save regenerated insight by fetching QA details and adding to insights table

        Args:
            content_id: The content ID to regenerate insight for
            insight_id: The insight ID to fetch QA details for

        Returns:
            Dict containing the saved insight and QA data
        """
        try:
            # Step 2: Get existing insights to calculate version
            existing_insights = await self.insight_service.get_all_by_query(
                query_filters={"content_id": content_id}
            )

            current_count = len(existing_insights)
            new_version = current_count + 1
            self.logger.info(
                f"Found {current_count} existing insights for content_id: {content_id}, creating version {new_version}")

            # Step 3: Update all existing insights to set preferred_choice=False
            updated_count = 0
            for existing_insight in existing_insights:
                if existing_insight.preferred_choice:  # Only update if currently True
                    await self.insight_service.update_content_insight(
                        insight_id=existing_insight.pk,
                        update_data={"preferred_choice": False}
                    )
                    updated_count += 1

            await self.insight_service.update_content_insight(
                insight_id=insight_id,
                update_data={"preferred_choice": True}
            )

            self.logger.info(
                f"Updated {updated_count} existing insights to set preferred_choice=False for content_id: {content_id}")

            # Step 5: Prepare response
            result = {
                "insight_id": insight_id,
                "content_id": content_id,
                "status": "updated"
            }

            self.logger.info(f"Insight regeneration completed successfully for content_id: {content_id}")
            return result

        except ValidationException:
            raise
        except Exception as e:
            self.logger.error(f"Insight regeneration failed for content_id {content_id}: {str(e)}")
            raise
