"""
RAG Agent Streamlit Frontend
A beautiful chat interface for your RAG Agent API
"""

import streamlit as st
import requests
from datetime import datetime
from typing import Optional
import json
import os

# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="RAG Agent Chat",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# CUSTOM CSS FOR BETTER UI
# ============================================================

st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stButton>button {
        width: 100%;
        background-color: #4CAF50;
        color: white;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #45a049;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
    }
    .user-message {
        background-color: #e3f2fd;
    }
    .assistant-message {
        background-color: #f5f5f5;
    }
    .source-badge {
        display: inline-block;
        padding: 0.2rem 0.5rem;
        border-radius: 4px;
        font-size: 0.8rem;
        font-weight: bold;
        margin-right: 0.5rem;
    }
    </style>
""", unsafe_allow_html=True)

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def get_source_icon(source_type: str) -> str:
    """Get emoji icon for source type"""
    icons = {
        "pdf": "📄",
        "txt": "📝",
        "md": "📋",
        "url": "🌐",
        "excel": "📊",
        "csv": "📈",
        "docx": "📃",
        "confluence": "🔗"
    }
    return icons.get(source_type.lower(), "📌")


def format_source_display(source: dict, index: int, include_scores: bool = True):
    """Format and display a single source with enhanced metadata"""
    
    # Get metadata
    metadata = source.get("metadata", {})
    source_type = metadata.get("source_type", "unknown")
    icon = get_source_icon(source_type)
    
    # Header with icon and type
    st.markdown(f"### {icon} Source {index} - {source_type.upper()}")
    
    # Source location
    source_path = metadata.get("source", "Unknown")
    
    if source_type == "url":
        st.markdown(f"🔗 **URL:** [{source_path}]({source_path})")
    else:
        filename = os.path.basename(source_path) if source_path != "Unknown" else "Unknown"
        st.markdown(f"📂 **File:** `{filename}`")
    
    # Metadata in columns
    cols = st.columns(3)
    
    with cols[0]:
        category = metadata.get("category", "N/A")
        st.caption(f"📁 **Category:** {category}")
    
    with cols[1]:
        domain = metadata.get("domain", "N/A")
        st.caption(f"🏷️ **Domain:** {domain}")
    
    with cols[2]:
        page = metadata.get("page")
        if page is not None:
            st.caption(f"📄 **Page:** {page}")
    
    # Content preview
    content = source.get("content", "")
    if isinstance(source, dict) and "page_content" in source:
        content = source["page_content"]
    
    st.markdown("**Content Preview:**")
    st.text_area(
        f"content_{index}",
        value=content[:500] + "..." if len(content) > 500 else content,
        height=120,
        disabled=True,
        label_visibility="collapsed"
    )
    
    # Relevance score
    if include_scores and "score" in source:
        score = source.get("score", 0.0)
        
        # Convert FAISS distance to similarity (lower distance = higher similarity)
        similarity = 1 / (1 + score)
        
        score_cols = st.columns([3, 1])
        
        with score_cols[0]:
            st.progress(similarity)
        
        with score_cols[1]:
            st.metric("", f"{similarity:.1%}")
        
        st.caption(f"📊 Distance: {score:.4f}")


def call_api(
    endpoint: str,
    method: str = "POST",
    data: Optional[dict] = None,
    base_url: str = "http://localhost:8080"
) -> dict:
    """
    Make API call to FastAPI backend
    
    Args:
        endpoint: API endpoint (e.g., "/ask/llm")
        method: HTTP method (GET, POST, etc.)
        data: Request payload
        base_url: Base URL of FastAPI server
        
    Returns:
        Response JSON or error dict
    """
    try:
        url = f"{base_url}{endpoint}"
        
        if method == "POST":
            response = requests.post(url, json=data, timeout=60)
        elif method == "GET":
            response = requests.get(url, timeout=30)
        else:
            return {"error": f"Unsupported method: {method}"}
        
        # Check if request was successful
        response.raise_for_status()
        return response.json()
        
    except requests.exceptions.Timeout:
        return {"error": "Request timed out. Please try again."}
    except requests.exceptions.ConnectionError:
        return {"error": "Cannot connect to API. Is the server running?"}
    except requests.exceptions.HTTPError as e:
        return {"error": f"HTTP Error: {response.status_code} - {response.text}"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}


def check_health(base_url: str) -> dict:
    """Check if API is healthy"""
    return call_api("/health", method="GET", base_url=base_url)


# ============================================================
# SESSION STATE INITIALIZATION
# ============================================================

# Initialize session state variables
if "messages" not in st.session_state:
    st.session_state.messages = []

if "session_id" not in st.session_state:
    st.session_state.session_id = None

if "api_url" not in st.session_state:
    st.session_state.api_url = "http://localhost:8080"

# ============================================================
# SIDEBAR - SETTINGS & CONFIGURATION
# ============================================================

with st.sidebar:
    st.title("⚙️ Settings")
    
    # API Configuration
    st.subheader("API Configuration")
    api_url = st.text_input(
        "API URL",
        value=st.session_state.api_url,
        help="URL of your FastAPI backend"
    )
    st.session_state.api_url = api_url
    
    # Health Check Button
    if st.button("🔍 Check API Health"):
        with st.spinner("Checking API health..."):
            health = check_health(api_url)
            
            if "error" in health:
                st.error(f"❌ API is down: {health['error']}")
            elif health.get("status") == "healthy":
                st.success("✅ API is healthy!")
                
                # Show component status
                components = health.get("components", {})
                st.json(components)
            else:
                st.warning("⚠️ API status unknown")
    
    st.divider()
    
    # Query Settings
    st.subheader("Query Settings")
    
    k_value = st.slider(
        "Number of documents to retrieve",
        min_value=1,
        max_value=10,
        value=3,
        help="How many relevant documents to search"
    )
    
    include_scores = st.checkbox(
        "Show relevance scores",
        value=True,
        help="Display similarity scores for retrieved documents"
    )
    
    st.divider()
    
    # Session Management
    st.subheader("Session Management")
    
    if st.session_state.session_id:
        st.info(f"**Session ID:**\n`{st.session_state.session_id}`")
        
        if st.button("🗑️ Clear Session"):
            st.session_state.messages = []
            st.session_state.session_id = None
            st.success("Session cleared!")
            st.rerun()
    else:
        st.warning("No active session")
    
    # Create New Session Button
    if st.button("➕ New Session"):
        with st.spinner("Creating new session..."):
            result = call_api("/session/new", method="POST", base_url=api_url)
            
            if "session_id" in result:
                st.session_state.session_id = result["session_id"]
                st.session_state.messages = []
                st.success(f"New session created!")
                st.rerun()
            else:
                st.error(f"Failed: {result.get('error', 'Unknown error')}")
    
    st.divider()
    
    # Statistics
    st.subheader("📊 Statistics")
    st.metric("Messages in conversation", len(st.session_state.messages))

# ============================================================
# MAIN CHAT INTERFACE
# ============================================================

# Title and Description
st.title("🤖 RAG Agent Chat")
st.markdown("""
Welcome to the RAG Agent! Ask me anything about your documents.
I'll search through the knowledge base and provide accurate answers.
""")

# Display conversation history
st.subheader("💬 Conversation")

for message in st.session_state.messages:
    role = message["role"]
    content = message["content"]
    
    with st.chat_message(role):
        st.write(content)
        
        # Show sources if available
        if role == "assistant" and "sources" in message:
            with st.expander("📚 Sources"):
                for i, source in enumerate(message["sources"], 1):
                    format_source_display(source, i, include_scores)
                    if i < len(message["sources"]):
                        st.divider()

# ============================================================
# USER INPUT
# ============================================================

st.divider()

# Create two columns for input and button
col1, col2 = st.columns([4, 1])

with col1:
    user_input = st.text_input(
        "Type your question here...",
        key="user_query",
        placeholder="e.g., What is data privacy?"
    )

with col2:
    send_button = st.button("🚀 Send", use_container_width=True)

# ============================================================
# HANDLE USER INPUT
# ============================================================

if send_button and user_input:
    # Add user message to chat
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })
    
    # Display user message immediately
    with st.chat_message("user"):
        st.write(user_input)
    
    # Call API
    with st.chat_message("assistant"):
        with st.spinner("🤔 Thinking..."):
            # Prepare request
            request_data = {
                "query": user_input,
                "k": k_value,
                "include_scores": include_scores,
                "session_id": st.session_state.session_id
            }
            
            # Call API
            response = call_api(
                "/ask/llm",
                method="POST",
                data=request_data,
                base_url=api_url
            )
            
            # Handle response
            if "error" in response:
                st.error(f"❌ Error: {response['error']}")
            else:
                # Extract data
                answer = response.get("answer", "No answer received")
                sources = response.get("sources", [])
                session_id = response.get("session_id")
                tokens = response.get("tokens_used", 0)
                model = response.get("model", "unknown")
                
                # Update session ID
                if session_id:
                    st.session_state.session_id = session_id
                
                # Display answer
                st.write(answer)
                
                # Show metadata
                st.caption(f"🤖 Model: {model} | 🎫 Tokens: {tokens}")
                
                # Show sources
                if sources:
                    with st.expander("📚 View Sources", expanded=True):
                        for i, source in enumerate(sources, 1):
                            format_source_display(source, i, include_scores)
                            if i < len(sources):
                                st.divider()
                
                # Add assistant message to history
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer,
                    "sources": sources,
                    "tokens": tokens,
                    "model": model
                })

# ============================================================
# FOOTER
# ============================================================

st.divider()
st.caption("Powered by RAG Agent API | Built with Streamlit")