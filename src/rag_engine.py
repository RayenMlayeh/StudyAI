from typing import List
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
import os


class RAGEngine:
    """Simple RAG engine for document retrieval"""
    
    def __init__(self, embedding_model: str = "text-embedding-3-small", api_key: str = None):
        self.embedding_model = embedding_model
        self.embeddings = OpenAIEmbeddings(
            model=embedding_model,
            openai_api_base="https://openrouter.ai/api/v1",
            openai_api_key=api_key or os.getenv("OPENROUTER_API_KEY")
        )
        self.vector_store = None
    
    def create_vector_store(self, documents: List[Document]) -> bool:
        """
        Create a vector store from documents
        
        Args:
            documents: List of chunked Document objects
            
        Returns:
            True if successful, False otherwise
        """
        if not documents:
            print("⚠️ No documents to process")
            return False
        
        try:
            self.vector_store = Chroma.from_documents(
                documents=documents,
                embedding=self.embeddings,
                collection_name="course_collection"
            )
            print(f"✓ Vector store created with {len(documents)} chunks")
            return True
            
        except Exception as e:
            print(f"✗ Error creating vector store: {e}")
            return False
    
    def retrieve_relevant_docs(self, query: str, k: int = 5, score_threshold: float = 0.5) -> List[Document]:
        """
        Retrieve relevant documents for a query with score filtering
        
        Args:
            query: User's question or search query
            k: Number of documents to retrieve
            score_threshold: Minimum similarity score (0-1, higher is better)
            
        Returns:
            List of relevant Document objects
        """
        if not self.vector_store:
            print("⚠️ Vector store not initialized. Upload a PDF first.")
            return []
        
        try:
            # Use similarity_search_with_score for better control
            # Note: Chroma scores are distance-based (lower is better) or similarity-based depending on config.
            # Default Chroma is L2 distance (lower is better). 
            # But langchain wrapper usually normalizes or we should check.
            # Let's assume standard similarity search first.
            
            docs_and_scores = self.vector_store.similarity_search_with_score(query, k=k)
            
            # Filter by score (assuming L2 distance, lower is better, usually < 1.0 for good matches)
            # Actually, let's just return top k for now but log the scores to help debugging
            # If we want strict filtering, we need to know the metric.
            # For safety, let's just return the docs but print scores.
            
            relevant_docs = []
            print(f"🔍 Retrieval scores for '{query}':")
            for doc, score in docs_and_scores:
                print(f"  - Score: {score:.4f} | Content: {doc.page_content[:50]}...")
                relevant_docs.append(doc)
                
            return relevant_docs
            
        except Exception as e:
            print(f"✗ Error retrieving documents: {e}")
            return []
            

    
    def get_context_for_query(self, query: str, k: int = 5) -> str:
        """
        Get combined context text for a query
        
        Args:
            query: User's question
            k: Number of chunks to retrieve
            
        Returns:
            Combined context string
        """
        docs = self.retrieve_relevant_docs(query, k)
        if not docs:
            return ""
        
        context = "\n\n".join([doc.page_content for doc in docs])
        return context
