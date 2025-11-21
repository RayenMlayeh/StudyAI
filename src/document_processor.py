"""
Document Processing Utilities
Text chunking and document preparation
"""

from typing import List
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document


class DocumentProcessor:
    """Process and chunk documents for RAG pipeline"""
    
    def __init__(self, chunk_size: int = 1500, chunk_overlap: int = 300):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        # Enhanced separator hierarchy
        self.separators = [
            "\n\n\n",  # Multiple blank lines
            "\n\n",    # Paragraph breaks
            "\n",      # Single line breaks
            ". ",      # Sentences
            "! ",
            "? ",
            "; ",
            ", ",
            " ",       # Words
            ""         # Characters
        ]
    
    def split_documents(self, documents: List[Document]) -> List[Document]:
        """
        Split documents into smaller chunks for better RAG performance.
        
        Uses recursive character splitting with intelligent separators to maintain
        semantic coherence within chunks.
        
        Strategy:
        - Tries to split on paragraph breaks first (\n\n)
        - Then line breaks (\n)
        - Then sentences (.!?)
        - Then clauses (,;)
        - Finally spaces and characters
        
        Args:
            documents: List of Document objects to split
            
        Returns:
            List of chunked Document objects
        """
        if not documents:
            print("⚠️ No documents to split")
            return []
        
        # Calculate total content size
        total_chars = sum(len(doc.page_content) for doc in documents)
        print(f"\n📊 Document Statistics:")
        print(f"  Total documents: {len(documents)}")
        print(f"  Total characters: {total_chars:,}")
        print(f"  Average doc size: {total_chars // len(documents):,} chars")
        print(f"  Chunk size: {self.chunk_size} chars")
        print(f"  Chunk overlap: {self.chunk_overlap} chars")
        print(f"  Expected chunks: ~{total_chars // (self.chunk_size - self.chunk_overlap):,}")
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=self.separators,
            keep_separator=True,
            length_function=len
        )
        
        chunks = text_splitter.split_documents(documents)
        
        # Detailed output
        print(f"\n✓ Split {len(documents)} documents into {len(chunks)} chunks")
        print(f"  Splitting ratio: {len(chunks) / len(documents):.1f}x")
        
        if chunks:
            chunk_sizes = [len(doc.page_content) for doc in chunks]
            print(f"  Average chunk size: {sum(chunk_sizes) // len(chunk_sizes):,} chars")
            print(f"  Min chunk size: {min(chunk_sizes):,} chars")
            print(f"  Max chunk size: {max(chunk_sizes):,} chars")
            
            print(f"\n📝 Example chunk:")
            print(f"  Content: {chunks[0].page_content[:200]}...")
            print(f"  Length: {len(chunks[0].page_content)} chars")
            print(f"  Metadata: {chunks[0].metadata}")
        
        return chunks
    
    def merge_documents(self, text_docs: List[Document], image_docs: List[Document]) -> List[Document]:
        """
        Merge text and image documents
        
        Args:
            text_docs: Documents from text extraction
            image_docs: Documents from image analysis
            
        Returns:
            Combined list of documents
        """
        all_docs = text_docs + image_docs
        print(f"✓ Merged {len(text_docs)} text docs + {len(image_docs)} image docs = {len(all_docs)} total")
        return all_docs
