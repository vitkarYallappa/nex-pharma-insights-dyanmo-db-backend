"""
Standardized Response Formatter
Provides consistent response structure across the application
"""

from typing import Any, Optional, Dict, List, Union
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from enum import Enum

class ResponseStatus(str, Enum):
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"

class ResponseMeta(BaseModel):
    """Metadata for paginated responses"""
    total: Optional[int] = None
    page: Optional[int] = None
    page_size: Optional[int] = None
    total_pages: Optional[int] = None
    has_next: Optional[bool] = None
    has_previous: Optional[bool] = None

class APIResponse(BaseModel):
    """Standard API response structure"""
    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat()
        }
    )
    
    status: ResponseStatus
    message: str
    data: Optional[Any] = None
    meta: Optional[ResponseMeta] = None
    timestamp: datetime
    request_id: Optional[str] = None
    errors: Optional[List[Dict[str, Any]]] = None

class ResponseFormatter:
    """Response formatter utility class"""
    
    @staticmethod
    def success(
        data: Any = None,
        message: str = "Operation completed successfully",
        meta: Optional[ResponseMeta] = None,
        request_id: Optional[str] = None
    ) -> APIResponse:
        """Format success response"""
        return APIResponse(
            status=ResponseStatus.SUCCESS,
            message=message,
            data=data,
            meta=meta,
            timestamp=datetime.utcnow(),
            request_id=request_id
        )
    
    @staticmethod
    def error(
        message: str = "An error occurred",
        errors: Optional[List[Dict[str, Any]]] = None,
        request_id: Optional[str] = None
    ) -> APIResponse:
        """Format error response"""
        return APIResponse(
            status=ResponseStatus.ERROR,
            message=message,
            data=None,
            errors=errors,
            timestamp=datetime.utcnow(),
            request_id=request_id
        )
    
    @staticmethod
    def warning(
        data: Any = None,
        message: str = "Warning",
        request_id: Optional[str] = None
    ) -> APIResponse:
        """Format warning response"""
        return APIResponse(
            status=ResponseStatus.WARNING,
            message=message,
            data=data,
            timestamp=datetime.utcnow(),
            request_id=request_id
        )
    
    @staticmethod
    def paginated(
        data: List[Any],
        total: int,
        page: int,
        page_size: int,
        message: str = "Data retrieved successfully",
        request_id: Optional[str] = None
    ) -> APIResponse:
        """Format paginated response"""
        total_pages = (total + page_size - 1) // page_size
        
        meta = ResponseMeta(
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_previous=page > 1
        )
        
        return APIResponse(
            status=ResponseStatus.SUCCESS,
            message=message,
            data=data,
            meta=meta,
            timestamp=datetime.utcnow(),
            request_id=request_id
        )
    
    @staticmethod
    def created(
        data: Any,
        message: str = "Resource created successfully",
        request_id: Optional[str] = None
    ) -> APIResponse:
        """Format creation response"""
        return APIResponse(
            status=ResponseStatus.SUCCESS,
            message=message,
            data=data,
            timestamp=datetime.utcnow(),
            request_id=request_id
        )
    
    @staticmethod
    def updated(
        data: Any,
        message: str = "Resource updated successfully",
        request_id: Optional[str] = None
    ) -> APIResponse:
        """Format update response"""
        return APIResponse(
            status=ResponseStatus.SUCCESS,
            message=message,
            data=data,
            timestamp=datetime.utcnow(),
            request_id=request_id
        )
    
    @staticmethod
    def deleted(
        message: str = "Resource deleted successfully",
        request_id: Optional[str] = None
    ) -> APIResponse:
        """Format deletion response"""
        return APIResponse(
            status=ResponseStatus.SUCCESS,
            message=message,
            data=None,
            timestamp=datetime.utcnow(),
            request_id=request_id
        )
    
    @staticmethod
    def not_found(
        resource: str = "Resource",
        request_id: Optional[str] = None
    ) -> APIResponse:
        """Format not found response"""
        return APIResponse(
            status=ResponseStatus.ERROR,
            message=f"{resource} not found",
            data=None,
            timestamp=datetime.utcnow(),
            request_id=request_id
        )
    
    @staticmethod
    def validation_error(
        errors: List[Dict[str, Any]],
        message: str = "Validation failed",
        request_id: Optional[str] = None
    ) -> APIResponse:
        """Format validation error response"""
        return APIResponse(
            status=ResponseStatus.ERROR,
            message=message,
            data=None,
            errors=errors,
            timestamp=datetime.utcnow(),
            request_id=request_id
        )

# Helper functions for common responses
def success_response(
    data: Any = None,
    message: str = "Operation completed successfully",
    meta: Optional[ResponseMeta] = None,
    request_id: Optional[str] = None
) -> Dict[str, Any]:
    """Quick success response as dict"""
    return ResponseFormatter.success(data, message, meta, request_id).dict()

def error_response(
    message: str = "An error occurred",
    errors: Optional[List[Dict[str, Any]]] = None,
    request_id: Optional[str] = None
) -> Dict[str, Any]:
    """Quick error response as dict"""
    return ResponseFormatter.error(message, errors, request_id).dict()

def paginated_response(
    data: List[Any],
    total: int,
    page: int,
    page_size: int,
    message: str = "Data retrieved successfully",
    request_id: Optional[str] = None
) -> Dict[str, Any]:
    """Quick paginated response as dict"""
    return ResponseFormatter.paginated(data, total, page, page_size, message, request_id).dict()

def safe_response_detail(response: APIResponse) -> Dict[str, Any]:
    """
    Safely serialize APIResponse for HTTPException detail
    Handles datetime serialization issues
    """
    try:
        return response.model_dump(mode='json') if hasattr(response, 'model_dump') else response.dict()
    except Exception:
        # Fallback to basic error info if serialization fails
        return {
            "status": response.status,
            "message": response.message,
            "errors": response.errors if hasattr(response, 'errors') else None,
            "timestamp": response.timestamp.isoformat() if hasattr(response, 'timestamp') else None,
            "request_id": response.request_id if hasattr(response, 'request_id') else None
        }

def to_response_format(item: Union[Any, Dict[str, Any]]) -> Dict[str, Any]:
    """
    Generic function to convert model objects or dictionaries to response format
    Handles both model objects with to_response() method and plain dictionaries
    """
    if hasattr(item, 'to_response') and callable(getattr(item, 'to_response')):
        return item.to_response()
    elif isinstance(item, dict):
        return item
    elif hasattr(item, 'to_dict') and callable(getattr(item, 'to_dict')):
        return item.to_dict()
    else:
        # Fallback: try to convert to dict if possible
        return item if isinstance(item, dict) else dict(item) if hasattr(item, '__dict__') else item