"""Standard API response schemas."""

from typing import Generic, Optional, TypeVar
from pydantic import BaseModel, Field


# Generic type for response data
T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    """
    Standard API response wrapper.

    Provides consistent response format across all endpoints.
    """

    success: bool = Field(..., description="Request success status")
    message: Optional[str] = Field(None, description="Response message")
    data: Optional[T] = Field(None, description="Response data")

    model_config = {
        "json_schema_extra": {
            "example": {
                "success": True,
                "message": "Operation completed successfully",
                "data": {"key": "value"},
            }
        }
    }


class ErrorDetail(BaseModel):
    """Error detail schema."""

    field: Optional[str] = Field(None, description="Field that caused the error")
    message: str = Field(..., description="Error message")
    type: Optional[str] = Field(None, description="Error type")

    model_config = {
        "json_schema_extra": {
            "example": {
                "field": "email",
                "message": "Invalid email format",
                "type": "value_error",
            }
        }
    }


class ErrorResponse(BaseModel):
    """
    Standard error response.

    Used for all error responses across the API.
    """

    success: bool = Field(default=False, description="Always false for errors")
    message: str = Field(..., description="Error message")
    errors: Optional[list[ErrorDetail]] = Field(None, description="Detailed errors")

    model_config = {
        "json_schema_extra": {
            "example": {
                "success": False,
                "message": "Validation error",
                "errors": [
                    {
                        "field": "email",
                        "message": "Invalid email format",
                        "type": "value_error",
                    }
                ],
            }
        }
    }


class PaginatedResponse(BaseModel, Generic[T]):
    """
    Paginated response wrapper.

    Used for endpoints that return paginated data.
    """

    success: bool = Field(default=True, description="Request success status")
    data: list[T] = Field(..., description="List of items")
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number")
    limit: int = Field(..., description="Items per page")
    pages: int = Field(..., description="Total number of pages")

    model_config = {
        "json_schema_extra": {
            "example": {
                "success": True,
                "data": [{"id": 1}, {"id": 2}],
                "total": 100,
                "page": 1,
                "limit": 20,
                "pages": 5,
            }
        }
    }
