from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings as SentenceTransformerEmbeddings

from rank_bm25 import BM25Okapi
from sentence_transformers import CrossEncoder
import numpy as np


class DocumentRetriever:
    def __init__(self,index_path: str = "faiss_index",model_name: str = "all-MiniLM-L6-v2",ranker="rank-bm25"):
        self.embed = SentenceTransformerEmbeddings(model_name=model_name)
        self.store = FAISS.load_local(index_path, self.embed, allow_dangerous_deserialization=True)
        self._build_bm25_index()
        self.reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
    
    def _build_bm25_index(self):
        """build key word search"""
        #get all documents from FAISS store
        all_docs=list(self.store.docstore._dict.values())
        tokenized_docs = [doc.page_content.lower().split() for doc in all_docs]
        
        # Create BM25 index
        self.bm25 = BM25Okapi(tokenized_docs)
        self.all_docs = all_docs

    def hybrid_search(self, query, domain=None, category=None, k=4):
        """build hybrid search using both bm25 and faiss"""
        
        """Semantic search with Faiss"""
        faiss_results = self.store.similarity_search_with_score(query, k=10, filter={"domain": domain, "category": category})

        #2. Keyword search with BM25
        query_tokens = query.lower().split()
        bm25_scores = self.bm25.get_scores(query_tokens)
        
        #get top 10 from BM25
        top_bm25_indicies = np.argsort(bm25_scores)[-10:][::-1]
        
        #combine results with weighted score
        combined_scores = {}
        
        #add faiss results 70% weight
        for doc, score in faiss_results:
            doc_id =id(doc)
            #convert distance score to similarity score
            similarity_score=1/(1+score)
            combined_scores[doc_id]={"docs":doc,"score":similarity_score*0.7,"source":"semantic"}
            
        #add bm25 results 30% weight
        for idx in top_bm25_indicies:
            doc =self.all_docs[idx]
            doc_id =id(doc)
            
            if doc_id in combined_scores:
                combined_scores[doc_id]["score"] += bm25_scores[idx]*0.3
                combined_scores[doc_id]["source"] +="both"
            else:
                combined_scores[doc_id]={"docs":doc,
                                         "score":bm25_scores[idx]*0.3,
                                         "source":"keyword"}
        #sort combined results
        sorted_results = sorted(combined_scores.values(), 
                                key=lambda x: x["score"], reverse=True)[:k]
        
        return[
            {
                'content': item['docs'].page_content,
                'metadata': item['docs'].metadata,
                'score': float(item['score']),
                'search_method': item['source']

            } for item in sorted_results
        ]    
        
    def rerank_results(self,query,k=5,retrieval_k=20):
        
        # Get initial retrieval results from Faiss
        initial_results = self.store.similarity_search_with_score(query, k=retrieval_k)
        
        # Prepare pairs for reranking
        pairs = [(query,doc.page_content) for doc in initial_results]
        reranked_scores = self.reranker.predict(pairs)
        
        # Combine documents with their reranked scores
        stored_docs = list(zip(initial_results,reranked_scores))
        
        # Sort based on reranked scores
        sorted_docs = sorted(stored_docs, key=lambda x: x[1], reverse=True)
        
        # Return top-k reranked results
        top_k_docs = sorted_docs[:k]
        
        return [
            {
                'content': doc.page_content,
                'metadata': doc.metadata,
                "faiss_rank":i,
                'rerank_score': float(score)
            } for i, (doc, score) in enumerate(top_k_docs)
        ]
           
        
    def search_documents(self, query, k=4):
        results = self.store.similarity_search(query, k=k)
        return results

    def search_filter(self, query, domain, category, k=4):
        results = self.store.similarity_search(query, k=k, filter={"domain": domain,"category": category})
        return results
    def search_with_scores(self, query, k=4):
        results = self.store.similarity_search_with_score(query, k=k)
        
        formatted_results = []
        for doc, score in results:
            formatted_results.append({"content": doc.page_content,
                                      "metadata": doc.metadata, 
                                      "score": float(score),
                                      })
        return formatted_results


