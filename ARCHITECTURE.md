# 🏗️ ResumeCour Architecture

## System Overview

ResumeCour is a RAG (Retrieval-Augmented Generation) application that processes educational documents and provides three AI-powered study modes: Quiz, Summary, and Chat.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          USER INTERFACE (Streamlit)                      │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐             │
│  │   📝 Quiz    │    │  📖 Summary  │    │   💬 Chat    │             │
│  │     Tab      │    │     Tab      │    │     Tab      │             │
│  └──────────────┘    └──────────────┘    └──────────────┘             │
└────────────────────────────┬────────────────────────────────────────────┘
                             │
                             │ File Upload (PDF/PPTX)
                             ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        DOCUMENT PROCESSING LAYER                         │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                    document_loader.py                             │  │
│  │  ┌────────────┐  ┌────────────┐  ┌─────────────────────────┐   │  │
│  │  │   PyMuPDF  │  │ python-pptx│  │  Vision Model (Grok)    │   │  │
│  │  │  (PDF Text)│  │ (PPTX Text)│  │  - Extract images       │   │  │
│  │  └────────────┘  └────────────┘  │  - Base64 encoding      │   │  │
│  │                                   │  - AI image analysis    │   │  │
│  │                                   └─────────────────────────┘   │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                             │                                            │
│                             │ Raw Documents                              │
│                             ▼                                            │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                 document_processor.py                             │  │
│  │  ┌────────────────────────────────────────────────────────────┐ │  │
│  │  │  RecursiveCharacterTextSplitter                            │ │  │
│  │  │  - Chunk size: 1500 characters                             │ │  │
│  │  │  - Overlap: 300 characters                                 │ │  │
│  │  │  - 9-level hierarchical separators                         │ │  │
│  │  │  - Detailed statistics output                              │ │  │
│  │  └────────────────────────────────────────────────────────────┘ │  │
│  └──────────────────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────────────────┘
                             │
                             │ Text Chunks (Documents)
                             ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         RAG PROCESSING LAYER                             │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                       rag_engine.py                               │  │
│  │                                                                   │  │
│  │  ┌───────────────────────────────────────────────────────────┐  │  │
│  │  │  Embedding Generation                                      │  │  │
│  │  │  Model: qwen/qwen3-embedding-8b (via OpenRouter)          │  │  │
│  │  │  - High-quality semantic embeddings                        │  │  │
│  │  │  - 8B parameters for nuanced understanding                 │  │  │
│  │  └───────────────────────────────────────────────────────────┘  │  │
│  │                             │                                     │  │
│  │                             ▼                                     │  │
│  │  ┌───────────────────────────────────────────────────────────┐  │  │
│  │  │  Vector Store (ChromaDB)                                   │  │  │
│  │  │  - In-memory vector database                               │  │  │
│  │  │  - Cosine similarity search                                │  │  │
│  │  │  - Persistent storage option                               │  │  │
│  │  └───────────────────────────────────────────────────────────┘  │  │
│  │                             │                                     │  │
│  │                             ▼                                     │  │
│  │  ┌───────────────────────────────────────────────────────────┐  │  │
│  │  │  Retrieval Methods                                         │  │  │
│  │  │  - retrieve_relevant_docs(query, k=5)                      │  │  │
│  │  │  - get_context_for_query(query, k=5)                       │  │  │
│  │  └───────────────────────────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────────────────┘
                             │
                   ┌─────────┼─────────┐
                   │         │         │
                   ▼         ▼         ▼
    ┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
    │   Quiz Module    │ │  Summary Module  │ │   Chat Module    │
    │ quiz_generator.py│ │  summarizer.py   │ │   chatbot.py     │
    └──────────────────┘ └──────────────────┘ └──────────────────┘
           │                     │                     │
           └─────────────────────┼─────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         LLM GENERATION LAYER                             │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                    OpenRouter API                                 │  │
│  │  ┌────────────────────────────────────────────────────────────┐ │  │
│  │  │  Model: x-ai/grok-4.1-fast                                 │ │  │
│  │  │  - Text generation (chat completion)                       │ │  │
│  │  │  - Vision analysis (image understanding)                   │ │  │
│  │  │  - Temperature: 0.2-0.7 (task-dependent)                   │ │  │
│  │  │  - Max tokens: 2000-8000                                   │ │  │
│  │  └────────────────────────────────────────────────────────────┘ │  │
│  └──────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. Document Processing Layer

#### document_loader.py
**Purpose**: Extract text and images from course materials

**Key Functions**:
- `load_pdf(file_path)` - Extracts text from PDF files
- `load_powerpoint(file_path)` - Extracts text from PPTX files
- `extract_images_from_pdf(pdf_path)` - Extracts images using PyMuPDF
- `analyze_image_with_vision(image_path)` - Uses Grok Vision to analyze images
- `process_images_to_docs(images)` - Converts images to Document objects

**Technologies**:
- PyMuPDF (fitz) for PDF processing
- python-pptx for PowerPoint processing
- Base64 encoding for image API calls
- Grok 4.1 Fast for vision analysis

#### document_processor.py
**Purpose**: Split documents into optimal chunks for RAG

**Configuration**:
- Chunk size: 1500 characters
- Chunk overlap: 300 characters
- 9-level hierarchical separators (newlines, periods, commas, etc.)

**Key Functions**:
- `split_documents(documents)` - Splits documents into chunks
- Provides detailed statistics (total docs, chars, expected chunks)

**Technologies**:
- LangChain RecursiveCharacterTextSplitter

### 2. RAG Processing Layer

#### rag_engine.py
**Purpose**: Create vector store and retrieve relevant documents

**Workflow**:
1. **Embedding Generation**
   - Model: `qwen/qwen3-embedding-8b`
   - Converts text chunks to high-dimensional vectors
   - Captures semantic meaning

2. **Vector Storage**
   - ChromaDB in-memory database
   - Fast cosine similarity search
   - Optional persistence

3. **Retrieval**
   - `retrieve_relevant_docs(query, k=5)` - Returns top-k similar documents
   - `get_context_for_query(query, k=5)` - Returns combined text context

**Key Features**:
- Semantic search (not keyword-based)
- Configurable top-k retrieval
- Source metadata tracking

### 3. Application Modules

#### quiz_generator.py
**Purpose**: Generate multiple-choice questions from course material

**Strategy**:
1. Uses RAG retriever with 4 diverse query types:
   - Definitions and terminology
   - Mathematical formulas and equations
   - Core concepts and theories
   - Practical examples and applications
2. Retrieves top-5 chunks per query type (20 total)
3. Generates 10 questions with 4 options each
4. Includes correct answers and explanations

**Configuration**:
- Model: Grok 4.1 Fast
- Temperature: 0.3 (balanced creativity/accuracy)
- Max tokens: 4000

**Key Functions**:
- `generate_quiz(retriever)` - Creates quiz from retriever
- `check_answers(quiz, user_answers)` - Scores and provides feedback
- `format_quiz_for_display(quiz)` - Pretty formatting for UI

#### summarizer.py
**Purpose**: Generate comprehensive study guides using MAP-REDUCE

**Strategy**:
1. **MAP PHASE** (Batch Processing)
   - Process chunks in batches of 5 (7,500 chars per batch)
   - Extract information from each batch:
     - Key concepts and definitions
     - Important formulas and equations
     - Examples and applications
     - Source + page metadata
   - Anti-hallucination prompt: "Only extract information EXPLICITLY present"

2. **REDUCE PHASE** (Synthesis)
   - Combine all batch summaries
   - Generate 9-section comprehensive guide:
     1. Course Introduction & Objectives
     2. Key Concepts & Definitions
     3. Core Theories & Frameworks
     4. Important Formulas & Equations
     5. Examples & Case Studies
     6. Common Misconceptions
     7. Study Tips & Tricks
     8. Practice Questions & Exercises
     9. Summary & Review
   - Dynamic word counts based on document volume

**Configuration**:
- Model: Grok 4.1 Fast
- Temperature: 0.2 (high accuracy)
- Max tokens: 8000
- Batch size: 5 chunks

**Optimization**:
- Token-efficient batching prevents API limits
- No content truncation (chunks already optimal)
- Source tracking prevents hallucination

#### chatbot.py
**Purpose**: Interactive Q&A with conversation memory

**Strategy**:
1. Retrieve top-5 relevant chunks for query
2. Include conversation history (last 3 exchanges)
3. Generate contextual answer with sources
4. Update conversation memory

**Configuration**:
- Model: Grok 4.1 Fast
- Temperature: 0.7 (more conversational)
- Max tokens: 2000

**Key Functions**:
- `chat(query, retriever)` - Answer with context
- `reset_conversation()` - Clear history

### 4. User Interface (app.py)

**Streamlit Application**:
- File upload widget
- 3 tabs (Quiz, Summary, Chat)
- Session state management
- Real-time progress indicators

**Session State**:
- `rag_engine` - Initialized RAG engine
- `all_chunks` - All document chunks
- `quiz_questions` - Generated quiz
- `summary` - Generated summary
- `chatbot` - Chat instance

## Data Flow

### Quiz Mode Flow
```
User uploads PDF
    → document_loader extracts text + images
    → document_processor chunks text
    → rag_engine creates vector store
    → quiz_generator retrieves diverse concepts
    → Grok generates 10 questions
    → User answers questions
    → quiz_generator scores and provides feedback
```

### Summary Mode Flow
```
User uploads PDF
    → document_loader extracts text + images
    → document_processor chunks text (1500 chars each)
    → summarizer processes in batches of 5 chunks
    → MAP: Extract info from each batch (anti-hallucination)
    → REDUCE: Combine into 9-section study guide
    → Display comprehensive summary
```

### Chat Mode Flow
```
User uploads PDF
    → document_loader extracts text + images
    → document_processor chunks text
    → rag_engine creates vector store
    → User asks question
    → rag_engine retrieves top-5 relevant chunks
    → chatbot includes conversation history
    → Grok generates answer with sources
    → Update conversation memory
```

## Key Design Decisions

### 1. Model Selection
- **Grok 4.1 Fast**: Fast, accurate, supports vision
- **Qwen 3 Embedding 8B**: High-quality semantic embeddings
- **OpenRouter**: Single API for multiple models

### 2. Chunking Strategy
- **1500 characters**: Optimal balance (context vs. precision)
- **300 overlap**: Prevents information loss at boundaries
- **Hierarchical separators**: Respects document structure

### 3. Token Optimization
- **Batch size 5**: Prevents API token limits
- **No truncation**: Chunks already optimal size
- **Targeted retrieval**: Only retrieve what's needed (k=5)

### 4. Anti-Hallucination Measures
- **Explicit instructions**: "Only extract information EXPLICITLY present"
- **Source tracking**: Include page numbers and sources
- **MAP-REDUCE**: Process in smaller, verifiable batches
- **Low temperature**: 0.2 for summaries (high accuracy)

### 5. Memory Management
- **Session state**: Persist data across interactions
- **Conversation history**: Last 3 exchanges for context
- **Lazy loading**: Only create vector store when needed

## Performance Characteristics

### Scalability
- **Documents**: Tested up to 50 pages
- **Images**: No practical limit (processed sequentially)
- **Concurrent users**: Streamlit handles session isolation

### Speed
- **Initial processing**: ~30-60 seconds (50 pages)
- **Quiz generation**: ~30 seconds
- **Summary generation**: ~1-2 minutes (MAP-REDUCE)
- **Chat response**: ~3-5 seconds

### Token Usage
- **Quiz**: ~3,000-5,000 tokens
- **Summary**: ~15,000-25,000 tokens (batch optimized)
- **Chat**: ~1,000-2,000 tokens per exchange
- **Vision**: ~500-1,000 tokens per image

## Security Considerations

### API Keys
- Stored in `.env` file (gitignored)
- Never committed to version control
- Can be configured per-user

### Data Privacy
- All processing in-memory (no persistence by default)
- No data sent to external services (except OpenRouter API)
- Vector store can be deleted after session

### Input Validation
- File type checking (PDF, PPTX only)
- Size limits enforced by Streamlit
- Error handling for malformed documents

## Future Enhancements

### Potential Improvements
1. **Caching**: Cache embeddings for repeated documents
2. **Export**: Export quizzes/summaries to PDF
3. **Analytics**: Track usage statistics
4. **Multi-language**: Support non-English documents
5. **Advanced retrieval**: Hybrid search (keyword + semantic)
6. **Fine-tuning**: Custom embeddings for domain-specific documents
7. **Collaboration**: Share quizzes/summaries with classmates
8. **Progress tracking**: Track quiz scores over time

### Scalability Improvements
1. **Persistent vector store**: Save ChromaDB to disk
2. **Background processing**: Async document processing
3. **Batch API calls**: Process multiple requests together
4. **Model caching**: Cache frequently used model responses
5. **Distributed processing**: Process large documents in parallel

## Conclusion

ResumeCour is a production-ready RAG application that demonstrates best practices in:
- Document processing and chunking
- Semantic search and retrieval
- Token-efficient LLM usage
- Anti-hallucination techniques
- User experience design

The architecture is modular, scalable, and easy to extend with new features.
