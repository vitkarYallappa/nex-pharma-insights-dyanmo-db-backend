"""
Insights API Client
Handles HTTP requests to external services for insights regeneration
"""
import httpx
import json
from typing import Dict, Any, Optional
from app.core.logging import get_logger
from app.core.exceptions import ValidationException

logger = get_logger("insights_api_client")


class InsightsApiClientException(Exception):
    """Exception raised when API client operations fail"""
    pass


class InsightsApiClient:
    """API client for making requests to insights regeneration service"""

    def __init__(self, base_url: str = "http://localhost:8005"):
        self.base_url = base_url.rstrip('/')
        self.logger = logger
        self.timeout = 30.0  # 30 seconds timeout

    async def regenerate_insight_request(
        self,
        content_id: str,
        summary_text: str,
        question_text: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Make POST request to regenerate insights
        
        Args:
            content_id: The content ID for regeneration
            summary_text: The summary text from content summary
            question_text: Additional metadata field 1
            
        Returns:
            Dict containing the API response
        """
        try:
            self.logger.info(f"Making regenerate insight request for content_id: {content_id}")
            
            # Prepare request payload
            payload = {
                "content_id": content_id,
                "user_text": summary_text,
                "question_text": question_text
            }
            
            # Remove None values from payload
            payload = {k: v for k, v in payload.items() if v is not None}
            
            # Make HTTP POST request
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/regenerate-insights",
                    json=payload,
                    headers={
                        "Content-Type": "application/json",
                        "Accept": "application/json"
                    }
                )
                
                # Check if request was successful
                if response.status_code == 200:
                    result = response.json()
                    self.logger.info(f"Successfully received response for content_id: {content_id}")
                    return result
                else:
                    error_msg = f"API request failed with status {response.status_code}: {response.text}"
                    self.logger.error(error_msg)
                    raise InsightsApiClientException(error_msg)
                    
        except httpx.TimeoutException:
            error_msg = f"Request timeout for content_id: {content_id}"
            self.logger.error(error_msg)
            raise InsightsApiClientException(error_msg)
        except httpx.RequestError as e:
            error_msg = f"Request error for content_id {content_id}: {str(e)}"
            self.logger.error(error_msg)
            raise InsightsApiClientException(error_msg)
        except Exception as e:
            error_msg = f"Unexpected error in API request for content_id {content_id}: {str(e)}"
            self.logger.error(error_msg)
            raise InsightsApiClientException(error_msg)

    async def create_insight_request(
        self,
        insight_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Make POST request to create insight
        
        Args:
            insight_data: Dictionary containing insight creation data
            
        Returns:
            Dict containing the API response
        """
        try:
            self.logger.info(f"Making create insight request")
            
            # Make HTTP POST request
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/create-insight",
                    json=insight_data,
                    headers={
                        "Content-Type": "application/json",
                        "Accept": "application/json"
                    }
                )
                
                # Check if request was successful
                if response.status_code == 200 or response.status_code == 201:
                    result = response.json()
                    self.logger.info(f"Successfully created insight")
                    return result
                else:
                    error_msg = f"Create insight API request failed with status {response.status_code}: {response.text}"
                    self.logger.error(error_msg)
                    raise InsightsApiClientException(error_msg)
                    
        except httpx.TimeoutException:
            error_msg = f"Request timeout for create insight"
            self.logger.error(error_msg)
            raise InsightsApiClientException(error_msg)
        except httpx.RequestError as e:
            error_msg = f"Request error for create insight: {str(e)}"
            self.logger.error(error_msg)
            raise InsightsApiClientException(error_msg)
        except Exception as e:
            error_msg = f"Unexpected error in create insight API request: {str(e)}"
            self.logger.error(error_msg)
            raise InsightsApiClientException(error_msg) 