"""Global error handling middleware."""

from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError
from jose import JWTError

from app.schemas.response import ErrorResponse, ErrorDetail


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handle Pydantic validation errors.
    
    Args:
        request: FastAPI request
        exc: Validation exception
    
    Returns:
        JSON response with validation errors
    """
    errors = []
    for error in exc.errors():
        errors.append(
            ErrorDetail(
                field=".".join(str(loc) for loc in error["loc"][1:]),
                message=error["msg"],
                type=error["type"]
            )
        )
    
    error_response = ErrorResponse(
        success=False,
        message="Validation error",
        errors=errors
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=error_response.model_dump()
    )


async def integrity_error_handler(request: Request, exc: IntegrityError):
    """
    Handle database integrity errors.
    
    Args:
        request: FastAPI request
        exc: Integrity error
    
    Returns:
        JSON response with error message
    """
    error_response = ErrorResponse(
        success=False,
        message="Database integrity error. The resource may already exist.",
        errors=[
            ErrorDetail(
                message=str(exc.orig) if hasattr(exc, 'orig') else str(exc),
                type="integrity_error"
            )
        ]
    )
    
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content=error_response.model_dump()
    )


async def jwt_error_handler(request: Request, exc: JWTError):
    """
    Handle JWT errors.
    
    Args:
        request: FastAPI request
        exc: JWT error
    
    Returns:
        JSON response with error message
    """
    error_response = ErrorResponse(
        success=False,
        message="Invalid or expired token",
        errors=[
            ErrorDetail(
                message=str(exc),
                type="jwt_error"
            )
        ]
    )
    
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content=error_response.model_dump(),
        headers={"WWW-Authenticate": "Bearer"}
    )


async def generic_exception_handler(request: Request, exc: Exception):
    """
    Handle all other exceptions.
    
    Args:
        request: FastAPI request
        exc: Exception
    
    Returns:
        JSON response with error message
    """

    error_response = ErrorResponse(
        success=False,
        message="An unexpected error occurred",
        errors=[
            ErrorDetail(
                message="Internal server error",
                type="internal_error"
            )
        ]
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response.model_dump()
    )
