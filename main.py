from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn  # ✅ Add this import!
from config import settings

from rag_memory import RedisConversationMemory
from llm_client import LLMClient
from retriever import DocumentRetriever
from rag_schema import AskRequest,generate_session_id

from middelware import error_handler_middleware, logging_middleware,validate_query,validate_session_id,ValidationError

app = FastAPI()

# Add middleware
app.middleware("http")(error_handler_middleware)
app.middleware("http")(logging_middleware)

# Add CORS (already have import)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For dev; restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize retriever once when app starts (loads FAISS index)
print("Loading document retriever...")
retriever = DocumentRetriever()
print("Retriever ready!")

# Initialize Redis memory (NEW!)
print("Connecting to Redis memory...")
memory = RedisConversationMemory() 
print("Memory ready!")

try:
    llm=LLMClient()
    print("LLM Client initialized successfully!")
except Exception as e:
    print(f"❌ Error initializing LLM Client: {e}")
    llm = None  # Set to None or handle as needed

# Health check endpoint
@app.get("/health")
async def health_check():
    redis_health = memory.health_check()
    return {"status": "ok", "version": "1.0.0", "redis": redis_health}


# Fixed /ask endpoint
@app.post("/ask")
async def ask_question(request: AskRequest):

    query = request.query
    domain = request.domain
    category = request.category
    include_scores = request.include_scores
    k = request.k

    
    # Return results with scores
    if include_scores:
        results = retriever.search_with_scores(query, k=k)
        
        return {
            "query": query,
            "num_results": len(results),
            "results": results
        }
    
    # Return results without scores
    else:
        # Apply filters if provided
        if domain or category:
            docs = retriever.search_filter(query, domain, category, k=k)
        else:
            docs = retriever.search_documents(query, k=k)
        
        # Extract just the text content
        context = [doc.page_content for doc in docs]
        
        return {
            "query": query,
            "num_results": len(context),
            "context": context
        }

@app.post("/ask/llm")
async def ask_llm(request:AskRequest):
    try:
        validate_query(request.query)
        validate_session_id(request.session_id)
    except ValidationError as e:
        return {
            "error": "Validation Error",
            "message": str(e)
        }
    # 1. Generate session ID's if missing
    request.session_id = request.session_id or generate_session_id()
    print("Using session_id:", request.session_id)
    
    
    # 2. Get conversation history
    if memory:
        try: 
            history=[]
            history_for_llm = ""
            history = memory.get_history(request.session_id)
            history_for_llm = memory.format_for_llm(request.session_id)
        except Exception as e:
            print(f"❌ Error retrieving history from memory: {e}")       
    #3. save user messages
    if memory:
        try:
            memory.add_message(session_id=request.session_id, 
                               role="user", 
                               content=request.query)
            print(f"✅ User message saved to memory for session: {request.session_id}")
        except Exception as e:
            print(f"❌ Error saving user message to memory: {e}")

    # 4. Search documents (your existing code)
    if request.include_scores:
        search_results = retriever.search_with_scores(request.query, k=request.k)
        docs_for_llm= [
            {"content":r.get("content"),"metadata": r.get("meta_data",{})}
            for r in search_results
        ]
    else:
        search_results = retriever.search_documents(request.query, k=request.k)
        docs_for_llm= [
            {"content":doc.page_content,"metadata": doc.get("meta_data",{})}
            for doc in search_results
        ]
    # 5. Generate answer with LLM
    if llm:
        try:
            llm_response=llm.generate_answer(
                query=request.query,
                context_docs=docs_for_llm,
                conversation_history=history_for_llm
            )
            if llm_response["success"]:
                answer = llm_response["answer"]
                tokens_used = llm_response.get("tokens_used", 0)
                print(f"✅ LLM answer generated using {tokens_used} tokens.")
            else:
                print(f"❌ LLM answer generation failed: {llm_response.get('error', 'Unknown error')}") 
                
        except Exception as e:
            print(f"❌ Error generating LLM answer: {e}")
        
    else:
        print("❌ LLM Client is not initialized.")
    
     
    # 6. Save assistant response (uncomment when you have real answer)
    if memory and answer:  
        memory.add_message(
            session_id=request.session_id,
            role="assistant",
            content=answer
        )
        
    return {
        "query": request.query,
        "session_id": request.session_id,
        "is_new_session": len(history) == 0,
        "history_length": len(history),
        "answer": answer,
        "sources": search_results[:3],  # Top 3 sources
        "tokens_used": tokens_used,
        "model": settings.LLM_MODEL if llm else None
    }
    

    
@app.post("/ask/hybrid")
async def ask_hybrid(request: AskRequest):
    
    query = request.query
    domain = request.domain
    category = request.category
    include_scores = request.include_scores
    k = request.k

    results = retriever.hybrid_search(query, domain, category, k=k)
    return {
            "query": query,
            "results": results,
            "search_method": "hybrid"
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)