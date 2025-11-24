import redis
from typing import Optional, List, Tuple,Dict
import json
from datetime import datetime, timedelta


class RedisConversationMemory:
    """Redis-based conversation memory for RAG agents."""
    def __init__(
        self,
        redis_url: Optional[str] = None,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        password: Optional[str] = None,
        ttl: int = 86400,  # 24 hours
        max_messages: int = 20
    ):
        """
        Initialize Redis connection.
        
        For LOCAL use (what you need now):
            memory = RedisConversationMemory()
        
        For PRODUCTION use (later):
            memory = RedisConversationMemory(redis_url="redis://...")
        
        Args:
            redis_url: Full Redis URL (for production)
            host: Redis host (for local, default: localhost)
            port: Redis port (for local, default: 6379)
            db: Redis database number (default: 0)
            password: Redis password if needed (optional)
            ttl: Session expiry in seconds (default: 24h)
            max_messages: Max messages per session (default: 20)
        """
        self.ttl = ttl
        self.max_messages = max_messages
        try:
            if redis_url:
                self.client = redis.from_url(redis_url, decode_responses=True)
            else:
                self.client= redis.Redis(host=host, port=port, db=db, password=password, decode_responses=True)
                
            self.client.ping()
            print("✅ Redis connection successful!")
        except redis.RedisError as e:
            print(f"❌ Redis connection error: {e}")
            raise
        
    def _get_key(self,session_id:str)->str:
        """Generate redis key for this session"""
        return f'chat:session:{session_id}'
    
    def add_message(self,session_id:str,role: str,content:str):
        """add message to chat history"""
        key = self._get_key(session_id)
        #get history messages of the session 
        messages = self.get_history(session_id)
        
        ##Add new messages to session id
        new_message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
        messages.append(new_message)
        
        #keep only last n messages
        if len(messages)>self.max_messages:
            messages = messages[-self.max_messages:]  
            
        self.client.setex(key,self.ttl,json.dumps(messages))
        print(f"📝 Adding messages to session: {session_id}")
        
    def get_history(self,session_id:str)->List[dict]:
        """
        Get conversation history.
        
        Args:
            session_id: Unique session identifier
            
        Returns:
            List of message dictionaries
        """
        key = self._get_key(session_id)
        data = self.client.get(key)
        if data is None:
            return []
        try:
            messages = json.loads(data)
            return messages
        except json.JSONDecodeError:
            print("❌ Error decoding JSON from Redis")
            return []
    
    def format_for_llm(self, session_id: str) -> str:
        """
        Format history for LLM prompt.
        
        Args:
            session_id: Unique session identifier
            
        Returns:
            Formatted conversation string
        """
        messages = self.get_history(session_id)
        
        if not messages:
            return ""
        
        formatted = []
        for msg in messages:
            role = "User" if msg["role"] == "user" else "Assistant"
            formatted.append(f"{role}: {msg['content']}")
        
        return "\n".join(formatted)
    def clear_session(self, session_id: str) -> bool:
        """
        Clear a session's history.
        
        Args:
            session_id: Unique session identifier
            
        Returns:
            True if deleted, False if didn't exist
        """
        key = self._get_key(session_id)
        result = self.client.delete(key)
        return result > 0
    
    def get_active_sessions(self) -> List[str]:
        """
        Get all active session IDs.
        
        Returns:
            List of session IDs
        """
        pattern = "chat:session:*"
        keys = self.client.keys(pattern)
        return [key.replace("chat:session:", "") for key in keys]
    
    def get_session_info(self, session_id: str) -> Dict:
        """
        Get session metadata.
        
        Args:
            session_id: Unique session identifier
            
        Returns:
            Dictionary with session info
        """
        key = self._get_key(session_id)
        
        if not self.client.exists(key):
            return {
                "exists": False,
                "session_id": session_id
            }
        
        ttl = self.client.ttl(key)
        messages = self.get_history(session_id)
        
        return {
            "exists": True,
            "session_id": session_id,
            "message_count": len(messages),
            "ttl_seconds": ttl,
            "ttl_hours": round(ttl / 3600, 2),
            "first_message": messages[0] if messages else None,
            "last_message": messages[-1] if messages else None
        }



    def health_check(self) -> Dict:
            """
            Check Redis health and stats.
            
            Returns:
                Health status dictionary
            """
            try:
                self.client.ping()
                active_sessions = self.get_active_sessions()
                info = self.client.info()
                
                return {
                    "status": "healthy",
                    "active_sessions": len(active_sessions),
                    "redis_version": info.get("redis_version"),
                    "used_memory_human": info.get("used_memory_human"),
                    "connected_clients": info.get("connected_clients")
                }
            except Exception as e:
                return {
                    "status": "unhealthy",
                    "error": str(e)
                }


def test_redis_memory(redis_url: Optional[str] = None, host: str = "localhost", port: int = 6379) -> dict:
    """Test the RedisConversationMemory class"""
    try:
        client= redis.from_url(redis_url, decode_responses=True) if redis_url else redis.Redis(host=host, port=port, decode_responses=True)
        client.ping()
        print("✅ Redis connection successful!")
    except redis.RedisError as e:
        print(f"❌ Redis connection error: {e}")
        return {"status": "error", "message": str(e)}
test_redis_memory()