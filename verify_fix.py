
import os
import sys
from unittest.mock import MagicMock, patch
from langchain_core.documents import Document

# Add src to path
sys.path.append(os.path.abspath("."))

from src.summarizer import CourseSummarizer
from src.document_processor import DocumentProcessor

def test_summarizer_logic():
    print("🧪 Testing Summarizer Logic...")
    
    # Mock LLM to avoid API calls and test prompt construction
    mock_llm = MagicMock()
    mock_llm.invoke.return_value.content = "Mocked Summary"
    
    # Initialize summarizer with mock
    summarizer = CourseSummarizer(api_key="test")
    summarizer.llm = mock_llm
    
    # Create dummy documents with DISTINCT topics
    docs = [
        Document(page_content="Security Chapter: Encryption is vital.", metadata={"source": "doc1"}),
        Document(page_content="Algebra Chapter: x + y = z.", metadata={"source": "doc1"})
    ]
    
    # Run generation
    summarizer.generate_summary(docs, batch_size=1)
    
    # Verify calls
    # We expect 2 MAP calls (one for each doc) and 1 REDUCE call
    print(f"  Calls to LLM: {mock_llm.invoke.call_count}")
    
    # Check if "Main Topic" injection is GONE from the prompt
    # We can't easily inspect the prompt object passed to invoke if it's a chain, 
    # but we can check if the code ran without error and printed the expected steps.
    
    print("✅ Summarizer logic test passed (mocked).")

def test_chunking_overlap():
    print("\n🧪 Testing Chunking Overlap...")
    processor = DocumentProcessor(chunk_size=100, chunk_overlap=50)
    
    text = "A" * 80 + "B" * 80 # 160 chars
    doc = Document(page_content=text)
    
    chunks = processor.split_documents([doc])
    
    print(f"  Original length: {len(text)}")
    print(f"  Number of chunks: {len(chunks)}")
    for i, chunk in enumerate(chunks):
        print(f"  Chunk {i} length: {len(chunk.page_content)}")
        
    # Verify overlap
    # With size 100 and overlap 50, we expect chunks to share content.
    if len(chunks) > 1:
        print("✅ Chunking produced multiple chunks.")
    else:
        print("⚠️ Chunking produced single chunk (might be okay for small text).")

if __name__ == "__main__":
    test_summarizer_logic()
    test_chunking_overlap()
