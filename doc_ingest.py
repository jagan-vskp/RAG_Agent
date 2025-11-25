from os import path
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings as SentenceTransformerEmbeddings



# List of PDFs with their domains
pdf_configs = [
    {"path": "/Users/jaganreddy/python_projects/ML_OPS/Docs_Rag/kohinoor.pdf", "domain": "data", "category": "history"},
    {"path": "/Users/jaganreddy/python_projects/ML_OPS/Docs_Rag/technical_analysis.pdf", "domain": "Finance", "category": "technical analysis"},
    {"path": "/Users/jaganreddy/python_projects/ML_OPS/Docs_Rag/Candlesticks.pdf", "domain": "stocks", "category": "technical analysis"},
    {"path": "/Users/jaganreddy/python_projects/ML_OPS/Docs_Rag/Data Privacy Policy.pdf", "domain": "data", "category": "privacy"},
    {"path": "/Users/jaganreddy/python_projects/ML_OPS/Docs_Rag/cricket.pdf", "domain": "knowledge", "category": "sports"},
    {"path": "/Users/jaganreddy/python_projects/ML_OPS/Docs_Rag/business_start.pdf", "domain": "business_start", "category": "policies"},
    {"path": "/Users/jaganreddy/python_projects/ML_OPS/Docs_Rag/business_ideas_india.pdf", "domain": "business_ideas", "category": "ideas"}
]

all_chunks=[]

for config in pdf_configs:
    print(config["path"])
    loader = PyPDFLoader(config["path"])
    docs = loader.load()
    
    #add custum metadata to each document
    for doc in docs:
        doc.metadata["domain"] = config["domain"]
        doc.metadata["category"] = config["category"]
    
    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=200)
    chunks = splitter.split_documents(docs)
        # Append to all_chunks
    all_chunks.extend(chunks)
embed = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
store = FAISS.from_documents(all_chunks, embed)
store.save_local("faiss_index")





