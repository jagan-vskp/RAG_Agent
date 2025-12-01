from datetime import datetime
import uuid
from pydantic import BaseModel
from typing import Optional
from langchain_community.vectorstores import Redis


class AskRequest(BaseModel):
    query: str
    domain: Optional[str] = None
    category: Optional[str] = None
    include_scores: bool = True
    session_id: Optional[str] = None
    k: Optional[int] = 4
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "What is data privacy?",
                "domain": "compliance",
                "category": "GDPR",
                "session_id": "optional-will-be-generated-if-missing",
                "k": 4,
                "include_scores": True
            }
        }
        
def generate_session_id(prefix: str = "session") -> str:
    """
    Generate a unique session ID.
    
    Format: {prefix}_{uuid}_{timestamp}
    Example: session_a1b2c3d4_20241124_103045
    
    Args:
        prefix: Optional prefix for the session ID (default: "session")
        
    Returns:
        Unique session ID string
    """
    # Generate UUID (universally unique identifier)
    unique_id = str(uuid.uuid4())[:8]  # First 8 characters
    
    # Get timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Combine
    session_id = f"{prefix}_{unique_id}_{timestamp}"
    
    return session_id
    
def generate_user_session_id(user_id: Optional[str] = None) -> str:
    """
    Generate session ID for a specific user.
    
    Args:
        user_id: Optional user identifier
        
    Returns:
        Session ID string
    """
    import uuid
    from datetime import datetime
    
    if user_id:
        unique_id = str(uuid.uuid4())[:8]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"user_{user_id}_{unique_id}_{timestamp}"
    else:
        return generate_session_id(prefix="anonymous")