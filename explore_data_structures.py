"""
Educational script to explore and understand data structures in RAG pipeline.
This demonstrates what the SAVED FAISS index contains.
"""

from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
import numpy as np
import os


def explore_saved_index():
    """Load and explore the saved FAISS index"""
    print("=" * 80)
    print("STEP 1: LOADING SAVED FAISS INDEX")
    print("=" * 80)
    
    # Load the embedding model (same one used during creation)
    print("\n🔄 Loading embedding model...")
    embed = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    # Load the saved FAISS index
    print("🔄 Loading FAISS index from disk...")
    store = FAISS.load_local("faiss_index", embed, allow_dangerous_deserialization=True)
    
    print(f"\n✅ Index loaded successfully!")
    print(f"  Total vectors in index: {store.index.ntotal}")
    print(f"  Vector dimensions: {store.index.d}")
    
    # Check file sizes
    if os.path.exists("faiss_index/index.faiss") and os.path.exists("faiss_index/index.pkl"):
        faiss_size = os.path.getsize("faiss_index/index.faiss")
        pkl_size = os.path.getsize("faiss_index/index.pkl")
        
        print(f"\n📁 Index files:")
        print(f"  index.faiss: {faiss_size:,} bytes ({faiss_size/1024:.1f} KB)")
        print(f"  index.pkl: {pkl_size:,} bytes ({pkl_size/1024:.1f} KB)")
        print(f"  Total size: {(faiss_size + pkl_size)/1024:.1f} KB")
    
    return store, embed


def explore_stored_documents(store):
    """Explore the documents stored in the index"""
    print("\n" + "=" * 80)
    print("STEP 2: EXPLORING STORED DOCUMENTS")
    print("=" * 80)
    
    # Get all documents from the docstore
    docstore = store.docstore._dict
    all_docs = list(docstore.values())
    
    print(f"\n📄 Total documents/chunks stored: {len(all_docs)}")
    
    # Analyze chunk sizes
    chunk_sizes = [len(doc.page_content) for doc in all_docs]
    print(f"\n📊 Chunk size statistics:")
    print(f"  Minimum: {min(chunk_sizes)} characters")
    print(f"  Maximum: {max(chunk_sizes)} characters")
    print(f"  Average: {sum(chunk_sizes)/len(chunk_sizes):.0f} characters")
    print(f"  Total text: {sum(chunk_sizes):,} characters")
    
    # Show first 3 chunks
    print("\n--- First 3 Chunks in Index ---")
    for i, doc in enumerate(list(all_docs)[:3]):
        print(f"\nChunk {i+1}:")
        print(f"  Length: {len(doc.page_content)} chars")
        print(f"  Content preview: {doc.page_content[:100]}...")
        print(f"  Metadata: {doc.metadata}")
    
    return all_docs


def explore_metadata(all_docs):
    """Explore metadata across all documents"""
    print("\n" + "=" * 80)
    print("STEP 3: ANALYZING METADATA")
    print("=" * 80)
    
    # Collect unique domains and categories
    domains = {}
    categories = {}
    sources = {}
    
    for doc in all_docs:
        # Count domains
        domain = doc.metadata.get("domain", "unknown")
        domains[domain] = domains.get(domain, 0) + 1
        
        # Count categories
        category = doc.metadata.get("category", "unknown")
        categories[category] = categories.get(category, 0) + 1
        
        # Count sources (PDF files)
        source = doc.metadata.get("source", "unknown")
        source_name = source.split("/")[-1] if "/" in source else source
        sources[source_name] = sources.get(source_name, 0) + 1
    
    print("\n📊 Documents by Domain:")
    for domain, count in sorted(domains.items()):
        print(f"  {domain}: {count} chunks")
    
    print("\n📊 Documents by Category:")
    for category, count in sorted(categories.items()):
        print(f"  {category}: {count} chunks")
    
    print("\n📊 Documents by Source File:")
    for source, count in sorted(sources.items()):
        print(f"  {source}: {count} chunks")


def explore_search_examples(store):
    """Show search examples across different domains"""
    print("\n" + "=" * 80)
    print("STEP 4: SEARCH EXAMPLES")
    print("=" * 80)
    
    queries = [
        ("What is data privacy?", None),  # No filter
        ("cricket rules", {"domain": "knowledge"}),  # Sports domain
        ("business ideas", {"domain": "business_ideas"}),  # Business domain
    ]
    
    for query, filter_dict in queries:
        print("\n" + "-" * 80)
        print(f"🔍 Query: '{query}'")
        if filter_dict:
            print(f"   Filter: {filter_dict}")
        
        # Search with or without filter
        if filter_dict:
            results = store.similarity_search(query, k=3, filter=filter_dict)
        else:
            results = store.similarity_search(query, k=3)
        
        print(f"\n📊 Found {len(results)} results:")
        for i, doc in enumerate(results, 1):
            print(f"\n  Result {i}:")
            print(f"    Domain: {doc.metadata.get('domain', 'N/A')}")
            print(f"    Category: {doc.metadata.get('category', 'N/A')}")
            print(f"    Source: {doc.metadata.get('source', 'N/A').split('/')[-1]}")
            print(f"    Content: {doc.page_content[:120]}...")


def explore_search_with_scores(store):
    """Show search with similarity scores"""
    print("\n" + "=" * 80)
    print("STEP 5: SEARCH WITH SIMILARITY SCORES")
    print("=" * 80)
    
    query = "How to start a business?"
    print(f"\n🔍 Query: '{query}'")
    
    results_with_scores = store.similarity_search_with_score(query, k=5)
    
    print(f"\n📊 Top 5 results with scores:")
    for i, (doc, score) in enumerate(results_with_scores, 1):
        confidence = (1 - min(score, 1)) * 100  # Convert to confidence %
        print(f"\n  Result {i}:")
        print(f"    Score: {score:.4f} (Confidence: {confidence:.1f}%)")
        print(f"    Domain: {doc.metadata.get('domain', 'N/A')}")
        print(f"    Category: {doc.metadata.get('category', 'N/A')}")
        print(f"    Content: {doc.page_content[:100]}...")


def explore_vector_representation(embed):
    """Show how queries are converted to vectors"""
    print("\n" + "=" * 80)
    print("STEP 6: VECTOR REPRESENTATIONS")
    print("=" * 80)
    
    sample_queries = [
        "What is data privacy?",
        "Cricket batting techniques",
        "Business startup ideas"
    ]
    
    print("\n🔢 Converting queries to vectors...")
    vectors = []
    
    for query in sample_queries:
        vector = embed.embed_query(query)
        vectors.append(vector)
        print(f"\nQuery: '{query}'")
        print(f"  Vector dimensions: {len(vector)}")
        print(f"  First 10 values: {[f'{v:.4f}' for v in vector[:10]]}")
        print(f"  Value range: [{min(vector):.4f}, {max(vector):.4f}]")
    
    # Show similarity between queries
    print("\n📊 Semantic Similarity between queries:")
    
    def cosine_similarity(v1, v2):
        return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
    
    for i in range(len(sample_queries)):
        for j in range(i + 1, len(sample_queries)):
            sim = cosine_similarity(vectors[i], vectors[j])
            print(f"  '{sample_queries[i][:30]}...' ↔ '{sample_queries[j][:30]}...': {sim:.4f}")


def main():
    """Run complete exploration"""
    print("\n" + "🚀" * 40)
    print("EXPLORING SAVED FAISS INDEX")
    print("🚀" * 40)
    
    # Load the saved index
    store, embed = explore_saved_index()
    
    # Explore stored documents
    all_docs = explore_stored_documents(store)
    
    # Analyze metadata
    explore_metadata(all_docs)
    
    # Show search examples
    explore_search_examples(store)
    
    # Show search with scores
    explore_search_with_scores(store)
    
    # Show vector representations
    explore_vector_representation(embed)
    
    print("\n" + "=" * 80)
    print("✅ EXPLORATION COMPLETE!")
    print("=" * 80)
    print("\nKey Insights:")
    print("1. Your index contains chunks from multiple PDFs across different domains")
    print("2. Each chunk has domain/category metadata for filtering")
    print("3. Vectors enable semantic search (meaning-based, not keyword-based)")
    print("4. You can filter searches by domain to get domain-specific results")
    print("5. Similarity scores help you understand result relevance")
    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()