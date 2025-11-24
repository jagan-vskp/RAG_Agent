from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
import time
import re
from typing import Optional


class ValidationError(Exception):
    """Custom validation error."""
    pass


def validate_query(query: str) -> None:
    """Validate user query."""
    
    # Check length
    if len(query) < 3:
        raise ValidationError("Query too short (minimum 3 characters)")
    
    if len(query) > 500:
        raise ValidationError("Query too long (maximum 500 characters)")
    
    # Check for SQL injection patterns
    sql_patterns = ['DROP TABLE', 'DELETE FROM', 'INSERT INTO', 'UPDATE ', 'SELECT ']
    if any(pattern in query.upper() for pattern in sql_patterns):
        raise ValidationError("Query contains prohibited SQL keywords")
    
    # Check for script injection
    script_patterns = ['<script', 'javascript:', 'onerror=']
    if any(pattern in query.lower() for pattern in script_patterns):
        raise ValidationError("Query contains prohibited script content")


def validate_session_id(session_id: Optional[str]) -> None:
    """Validate session ID format."""
    
    if session_id is None:
        return  # Optional, will be generated
    
    # Check format (alphanumeric, underscores, hyphens only)
    if not re.match(r'^[a-zA-Z0-9_-]+$', session_id):
        raise ValidationError("Invalid session_id format")
    
    # Check length
    if len(session_id) > 100:
        raise ValidationError("session_id too long")


async def error_handler_middleware(request: Request, call_next):
    """Global error handling middleware."""
    
    try:
        response = await call_next(request)
        return response
        
    except ValidationError as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": "Validation Error",
                "message": str(e),
                "status_code": 400
            }
        )
    
    except HTTPException as e:
        return JSONResponse(
            status_code=e.status_code,
            content={
                "error": "HTTP Error",
                "message": e.detail,
                "status_code": e.status_code
            }
        )
    
    except Exception as e:
        # Log the error here
        print(f"Unexpected error: {e}")
        
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "Internal Server Error",
                "message": "An unexpected error occurred",
                "status_code": 500
            }
        )


async def logging_middleware(request: Request, call_next):
    """Log all requests."""
    
    start_time = time.time()
    
    # Log request
    print(f"→ {request.method} {request.url.path}")
    
    # Process request
    response = await call_next(request)
    
    # Log response
    duration = time.time() - start_time
    print(f"← {response.status_code} ({duration:.3f}s)")
    
    return response