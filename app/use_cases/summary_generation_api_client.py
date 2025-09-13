import requests
import json
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class SummaryGenerationAPIClient:
    """
    API client for making summary generation requests to the market intelligence service.
    """
    
    def __init__(self, base_url: str = "http://localhost:8005"):
        """
        Initialize the API client.
        
        Args:
            base_url (str): Base URL for the market intelligence API
        """
        self.base_url = base_url
        self.endpoint = f"{base_url}/api/v1/market-intelligence-requests"
        self.headers = {
            'Content-Type': 'application/json'
        }
    
    def generate_summary(self, project_id: str, request_id: str, keywords: List[str], 
                        base_urls: List[Dict[str, str]], date_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Main method to generate summary by making API call to market intelligence service.
        
        Args:
            project_id (str): The project ID
            request_id (str): The request ID
            keywords (List[str]): List of keywords for content extraction
            base_urls (List[Dict[str, str]]): List of source URLs with metadata
            date_config (Optional[Dict[str, Any]]): Date configuration for filtering
            
        Returns:
            Dict[str, Any]: API response containing the summary generation result
            
        Raises:
            Exception: If API call fails or returns error response
        """
        try:
            # Build the request payload
            payload = self._build_request(project_id, request_id, keywords, base_urls, date_config)
            
            # Make the API call
            response = self._make_api_call(payload)
            
            logger.info(f"Summary generation request successful for project {project_id}, request {request_id}")
            return response
            
        except Exception as e:
            logger.error(f"Failed to generate summary for project {project_id}, request {request_id}: {str(e)}")
            raise
    
    def _build_request(self, project_id: str, request_id: str, keywords: List[str], 
                      base_urls: List[Dict[str, str]], date_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Request builder method to construct the API payload.
        
        Args:
            project_id (str): The project ID
            request_id (str): The request ID
            keywords (List[str]): List of keywords for content extraction
            base_urls (List[Dict[str, str]]): List of source URLs with metadata
            date_config (Optional[Dict[str, Any]]): Date configuration for filtering
            
        Returns:
            Dict[str, Any]: Constructed request payload
        """
        # Transform base_urls to the expected format
        sources = []
        for url_info in base_urls:
            source = {
                "url": url_info.get("url", ""),
                "name": url_info.get("name", url_info.get("url", "").split("//")[-1].split("/")[0]),
                "type": url_info.get("type", "medical_literature")
            }
            sources.append(source)
        
        # Build the config object
        config = {
            "keywords": keywords,
            "sources": sources,
            "extraction_mode": "summary",
            "quality_threshold": 0.8,
            "metadata": {
                "requestId": request_id
            }
        }
        
        # Add date configuration if provided
        if date_config:
            config["date_config"] = date_config
        
        # Build the complete payload
        payload = {
            "project_id": project_id,
            "project_request_id": request_id,
            "user_id": "debug_user",  # This could be made configurable
            "priority": "high",
            "processing_strategy": "table",
            "config": config
        }
        
        return payload
    
    def _make_api_call(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        API call method to handle HTTP request to market intelligence endpoint.
        
        Args:
            payload (Dict[str, Any]): Request payload to send
            
        Returns:
            Dict[str, Any]: Parsed API response
            
        Raises:
            requests.RequestException: If HTTP request fails
            ValueError: If response cannot be parsed as JSON
            Exception: If API returns error response
        """
        try:
            # Convert payload to JSON string
            json_payload = json.dumps(payload)
            
            logger.info(f"Making API call to {self.endpoint}")
            logger.debug(f"Request payload: {json_payload}")
            
            # Make the POST request
            response = requests.post(
                self.endpoint,
                headers=self.headers,
                data=json_payload,
                timeout=30  # 30 second timeout
            )
            
            # Check if request was successful
            response.raise_for_status()
            
            # Parse response JSON
            try:
                response_data = response.json()
            except json.JSONDecodeError:
                # If response is not JSON, return the text content
                response_data = {"response": response.text}
            
            logger.info(f"API call successful. Status code: {response.status_code}")
            logger.debug(f"Response data: {response_data}")
            
            return response_data
            
        except requests.exceptions.Timeout:
            logger.error("API call timed out")
            raise Exception("API request timed out after 30 seconds")
            
        except requests.exceptions.ConnectionError:
            logger.error(f"Failed to connect to API endpoint: {self.endpoint}")
            raise Exception(f"Failed to connect to API endpoint: {self.endpoint}")
            
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error occurred: {e}")
            logger.error(f"Response content: {response.text}")
            raise Exception(f"API request failed with status {response.status_code}: {response.text}")
            
        except Exception as e:
            logger.error(f"Unexpected error during API call: {str(e)}")
            raise


# Convenience function for direct usage
def generate_summary(project_id: str, request_id: str, keywords: List[str], 
                    base_urls: List[Dict[str, str]], date_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Convenience function to generate summary using the API client.
    
    Args:
        project_id (str): The project ID
        request_id (str): The request ID
        keywords (List[str]): List of keywords for content extraction
        base_urls (List[Dict[str, str]]): List of source URLs with metadata
        date_config (Optional[Dict[str, Any]]): Date configuration for filtering
        
    Returns:
        Dict[str, Any]: API response containing the summary generation result
    """
    client = SummaryGenerationAPIClient()
    return client.generate_summary(project_id, request_id, keywords, base_urls, date_config)
