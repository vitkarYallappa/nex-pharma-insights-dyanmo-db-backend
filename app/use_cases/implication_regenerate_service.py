"""
Implication Regenerate Service
Handles regeneration of implications with version management and QA creation
"""

from typing import Dict, Any, Optional
from app.services.content_implication_service import ContentImplicationService
from app.services.implication_qa_service import ImplicationQaService
from app.core.logging import get_logger
from app.core.exceptions import ValidationException

logger = get_logger("implication_regenerate_service")

class ImplicationRegenerateService:
    """Service for regenerating implications with version management"""
    
    def __init__(self):
        self.implication_service = ContentImplicationService()
        self.qa_service = ImplicationQaService()
        self.logger = logger
    
    async def regenerate_implication(
        self,
        content_id: str,
        metadata_field1: Optional[str] = None,
        metadata_field2: Optional[str] = None,
        metadata_field3: Optional[str] = None,
        question_text: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Regenerate implication for given content with version management
        
        Args:
            content_id: The content ID to regenerate implication for
            metadata_field1: Additional metadata field 1
            metadata_field2: Additional metadata field 2
            metadata_field3: Additional metadata field 3
            question_text: Optional question text for QA generation
            
        Returns:
            Dict containing the regenerated implication and QA data
        """
        try:
            self.logger.info(f"Starting implication regeneration for content_id: {content_id}")
            
            # Step 1: Count existing implications for this content to determine version
            existing_implications = await self.implication_service.get_all_by_query(
                query_filters={"content_id": content_id}
            )
            
            current_count = len(existing_implications)
            new_version = current_count + 1
            
            self.logger.info(f"Found {current_count} existing implications, creating version {new_version}")
            
            # Step 2: Create new implication with incremented version
            # We need to get URL ID from existing implications or create a default one
            url_id = existing_implications[0].url_id if existing_implications else "default-url-id"
            
            # Create file path for the new implication
            file_path = f"implications/{content_id}/regenerated_implication_v{new_version}.txt"
            
            # Prepare metadata
            implication_metadata = {}
            if metadata_field1:
                implication_metadata["field1"] = metadata_field1
            if metadata_field2:
                implication_metadata["field2"] = metadata_field2
            if metadata_field3:
                implication_metadata["field3"] = metadata_field3

            regenerate_text = question_text.strip()

            # Create the new implication
            new_implication = await self.implication_service.create_content_implication(
                url_id=url_id,
                content_id=content_id,
                implication_text=regenerate_text,
                implication_content_file_path=file_path,
                implication_type="regenerated",
                priority_level="high",
                confidence_score=None,
                version=new_version,
                is_canonical=True,
                preferred_choice=True,
                created_by="regenerate_service"
            )
            
            self.logger.info(f"Created new implication: {new_implication.pk} with version {new_version}")
            
            # Step 3: Generate QA if question text is provided
            qa_entry = None
            if question_text and question_text.strip():
                # Generate answer (for now, we'll create a simple answer based on the implication)
                generated_answer = f"Based on the regenerated implication: {regenerate_text[:200]}..."
                
                qa_entry = await self.qa_service.create_implication_qa(
                    implication_id=new_implication.pk,
                    question=question_text.strip(),
                    answer=generated_answer,
                    question_type="regeneration",
                    qa_metadata={
                        "regeneration_version": new_version,
                        "content_id": content_id,
                        **implication_metadata
                    }
                )
                
                self.logger.info(f"Created QA entry: {qa_entry.pk}")
            
            # Step 4: Prepare response
            result = {
                "regenerated_implication": new_implication.to_response(),
                "version": new_version,
                "previous_implications_count": current_count,
                "qa_entry": qa_entry.to_response() if qa_entry else None,
                "metadata": implication_metadata,
                "content_id": content_id
            }
            
            self.logger.info(f"Implication regeneration completed successfully for content_id: {content_id}")
            return result
            
        except ValidationException:
            raise
        except Exception as e:
            self.logger.error(f"Implication regeneration failed for content_id {content_id}: {str(e)}")
            raise
