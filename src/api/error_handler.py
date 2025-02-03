from fastapi import Request
from fastapi.responses import JSONResponse
from src.exceptions.custom_exceptions import (
    NLPServiceException,
    ModelConnectionError,
    InvalidModelResponseError,
    ValidationError,
    JSONParsingError
)

async def nlp_exception_handler(request: Request, exc: NLPServiceException):
    """Handle custom NLP service exceptions"""
    status_code_mapping = {
        ModelConnectionError: 503,  # Service Unavailable
        InvalidModelResponseError: 502,  # Bad Gateway
        ValidationError: 400,  # Bad Request
        JSONParsingError: 502,  # Bad Gateway
        NLPServiceException: 500,  # Internal Server Error
    }
    
    # Get the appropriate status code based on exception type
    status_code = status_code_mapping.get(type(exc), 500)
    
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "type": exc.__class__.__name__,
                "code": getattr(exc, 'error_code', 'UNKNOWN_ERROR'),
                "message": str(exc)
            }
        }
    )