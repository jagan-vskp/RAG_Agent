from typing import List,Optional,Tuple,Dict
import os
from dotenv import load_dotenv
from groq import Groq
from config import settings

load_dotenv()  # Load environment variables from .env file

class LLMClient:
    """LLM client for answer generation"""
    
    def __init__(self,
                provider: str = settings.LLM_PROVIDER,
                model: str = settings.LLM_MODEL,
                temperature: float = 0.3,
                max_tokens: int = 1024):
        self.provider = provider
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.client = None
        #Initialize Groq client
        if self.provider == "groq":
            api_key = os.getenv("GROQ_API_KEY")
            if not api_key:
                raise ValueError("GROQ_API_KEY not set in environment variables")
            self.client = Groq(api_key=api_key)
        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider}")
        
    def build_prompt(
        self,query:str,
        context_docs:List[Dict],
        conversation_history:str
        ) ->str:
        
        """building a RAG prompt with context and history"""
        
        """how context docs looks
        context_docs = [
            {"content": "Privacy means...", "metadata": {"source": "privacy.pdf"}},
            {"content": "GDPR defines...", "metadata": {"source": "gdpr.pdf"}},
                        ]
        """
        
        """
        How context has to be passed to llm
        Document 1 (Source: privacy.pdf):
            Privacy means...

        Document 2 (Source: gdpr.pdf):
          GDPR defines...
        """
        
        #format the context docs

        context = "\n\n".join([f"Document {i+1} (source: {doc.get('metadata',{}).get('source','Unknown')}):\n{doc['content']}"
                              for i , doc in enumerate(context_docs[:5])
                              ])
        # Build prompt
        prompt = f"""You are a helpful AI assistant that answers questions based on provided documents. if the relevant information is not found in the documents,provide generalised answer.

IMPORTANT RULES:
1. Answer using the context documents below, if relevant information is not found in the documents, provide your answer based on your knowledge.
2. Cite sources using [Document X] notation
3. Be concise but complete


CONTEXT DOCUMENTS:
{context}

"""
        # Add conversation history if exists
        if conversation_history:
            prompt += f"""
CONVERSATION HISTORY:
{conversation_history}

"""
        
        prompt += f"""
USER QUESTION: {query}

YOUR ANSWER (following all rules above):"""
        
        return prompt
    
    def generate_answer(
        self,query:str,
        context_docs:List[Dict],
        conversation_history: str = ""
        ) -> str:
        try:
            #build prompt
            prompt = self.build_prompt(query, context_docs, conversation_history)
            
            #Call LLM API
            response =self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that answers questions based on provided documents."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            print("llm response:", response)
            answer = response.choices[0].message.content
            
            return {
                "answer": answer,
                # "model": self.model,
                "token_used": response.usage.total_tokens,
                "success":True            
                }
        except Exception as e:
            return {
                "answer": f"Error generating answer: {str(e)}",
                # "model": self.model,
                "tokens_used": 0,
                "success": False,
                "error": str(e)
            }
            
    def generate_answer_streaming(
        self,
        query: str,
        context_docs: List[Dict],
        conversation_history: str = ""
    ):
        """Generate answer with streaming (for real-time responses)."""
        
        prompt = self.build_prompt(query, context_docs, conversation_history)
        
        stream = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            stream=True
        )
        
        for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
