# ResumeCour Pipeline Diagram

## Complete System Workflow

Below is the complete data flow and processing pipeline for the ResumeCour AI Study Assistant.

```mermaid
graph TD
    A[👤 User] -->|Upload File| B[📤 File Upload<br/>PDF/PPTX]
    
    B --> C{Document Type?}
    C -->|PDF| D[📄 PyMuPDF<br/>Text Extraction]
    C -->|PPTX| E[📊 python-pptx<br/>Text Extraction]
    
    D --> F[🖼️ Image Extraction<br/>PyMuPDF]
    F --> G[🤖 Vision AI<br/>Grok 4.1 Fast]
    G -->|Image Text| H[📝 Document Collection]
    
    D -->|Text| H
    E -->|Text| H
    
    H --> I[✂️ Text Chunking<br/>RecursiveCharacterTextSplitter<br/>Size: 1500, Overlap: 300]
    
    I --> J[🧠 Embedding Generation<br/>qwen/qwen3-embedding-8b<br/>via OpenRouter]
    
    J --> K[💾 Vector Store<br/>ChromaDB<br/>Cosine Similarity]
    
    K --> L{User Choice}
    
    L -->|Quiz Mode| M[📝 Quiz Generator]
    L -->|Summary Mode| N[📖 Summarizer]
    L -->|Chat Mode| O[💬 Chatbot]
    
    M --> M1[🔍 Retrieval Strategy<br/>4 Query Types<br/>Top-5 per Type]
    M1 --> M2[🤖 Grok 4.1 Fast<br/>Temp: 0.3]
    M2 --> M3[✅ 10 Questions Generated<br/>Multiple Choice]
    M3 --> P[👤 User Answers]
    P --> Q[📊 Score & Feedback]
    
    N --> N1[📦 MAP Phase<br/>Process 5 Chunks<br/>Extract Key Info]
    N1 --> N2[🔗 REDUCE Phase<br/>Combine Summaries<br/>9 Sections]
    N2 --> N3[🤖 Grok 4.1 Fast<br/>Temp: 0.2<br/>Max Tokens: 8000]
    N3 --> R[📄 Comprehensive Guide]
    
    O --> O1[🔍 Retrieve Top-5 Chunks<br/>Based on Query]
    O1 --> O2[💭 Add Conversation History<br/>Last 3 Exchanges]
    O2 --> O3[🤖 Grok 4.1 Fast<br/>Temp: 0.7<br/>Max Tokens: 2000]
    O3 --> S[💬 Answer with Sources]
    S --> O4[📝 Update Memory]
    
    style A fill:#e1f5ff
    style B fill:#fff3e0
    style D fill:#e8f5e9
    style E fill:#e8f5e9
    style F fill:#f3e5f5
    style G fill:#fce4ec
    style I fill:#fff9c4
    style J fill:#ffebee
    style K fill:#e0f2f1
    style M fill:#e3f2fd
    style N fill:#fce4ec
    style O fill:#f1f8e9
    style M3 fill:#c8e6c9
    style R fill:#c8e6c9
    style S fill:#c8e6c9
```

## Detailed Component Flow

### 1. Document Processing Pipeline

```mermaid
sequenceDiagram
    participant User
    participant DocLoader
    participant PyMuPDF
    participant Vision
    participant Processor
    
    User->>DocLoader: Upload PDF/PPTX
    DocLoader->>PyMuPDF: Extract text
    PyMuPDF-->>DocLoader: Text content
    
    DocLoader->>PyMuPDF: Extract images
    PyMuPDF-->>DocLoader: Image files
    
    loop For each image
        DocLoader->>Vision: Analyze image (Base64)
        Vision-->>DocLoader: Image description
    end
    
    DocLoader->>Processor: All documents
    Processor->>Processor: Chunk text (1500 chars)
    Processor-->>User: Ready for processing
```

### 2. RAG Engine Pipeline

```mermaid
sequenceDiagram
    participant Chunks
    participant Embedder
    participant VectorDB
    participant Retriever
    participant LLM
    
    Chunks->>Embedder: Text chunks
    Embedder->>Embedder: Generate embeddings<br/>(qwen/qwen3-embedding-8b)
    Embedder->>VectorDB: Store vectors (ChromaDB)
    
    Note over VectorDB: Vector store ready
    
    Retriever->>VectorDB: Query embedding
    VectorDB-->>Retriever: Top-K similar chunks
    Retriever->>LLM: Context + Query
    LLM-->>Retriever: Generated response
```

### 3. Quiz Mode Pipeline

```mermaid
flowchart LR
    A[Quiz Request] --> B[Generate 4 Diverse Queries]
    B --> C1[Definitions Query]
    B --> C2[Formulas Query]
    B --> C3[Concepts Query]
    B --> C4[Examples Query]
    
    C1 --> D[Retriever: Top-5 Chunks]
    C2 --> D
    C3 --> D
    C4 --> D
    
    D --> E[Combine Context<br/>20 Chunks Total]
    E --> F[Grok 4.1 Fast<br/>Generate Questions]
    F --> G[10 Multiple Choice<br/>Questions]
    G --> H[User Answers]
    H --> I[Check Answers]
    I --> J[Score & Feedback]
    
    style A fill:#e3f2fd
    style G fill:#c8e6c9
    style J fill:#ffcc80
```

### 4. Summary Mode Pipeline (MAP-REDUCE)

```mermaid
flowchart TD
    A[All Chunks] --> B[Split into Batches<br/>5 Chunks per Batch]
    
    B --> C1[Batch 1]
    B --> C2[Batch 2]
    B --> C3[Batch 3]
    B --> CN[Batch N]
    
    C1 --> D1[MAP: Extract Info<br/>Key Concepts, Formulas, Examples]
    C2 --> D2[MAP: Extract Info]
    C3 --> D3[MAP: Extract Info]
    CN --> DN[MAP: Extract Info]
    
    D1 --> E[Combine All Summaries]
    D2 --> E
    D3 --> E
    DN --> E
    
    E --> F[REDUCE: Synthesize<br/>9-Section Guide]
    F --> G[1. Introduction & Objectives]
    F --> H[2. Key Concepts & Definitions]
    F --> I[3. Core Theories & Frameworks]
    F --> J[4. Formulas & Equations]
    F --> K[5. Examples & Case Studies]
    F --> L[6. Common Misconceptions]
    F --> M[7. Study Tips & Tricks]
    F --> N[8. Practice Questions]
    F --> O[9. Summary & Review]
    
    G --> P[Comprehensive Study Guide]
    H --> P
    I --> P
    J --> P
    K --> P
    L --> P
    M --> P
    N --> P
    O --> P
    
    style A fill:#fff3e0
    style E fill:#ffcc80
    style P fill:#c8e6c9
```

### 5. Chat Mode Pipeline

```mermaid
flowchart TD
    A[User Question] --> B[Retrieve Top-5<br/>Relevant Chunks]
    B --> C[Get Conversation<br/>History]
    C --> D[Combine:<br/>Context + History + Question]
    D --> E[Grok 4.1 Fast<br/>Generate Answer]
    E --> F[Answer with Sources]
    F --> G[Update Conversation<br/>Memory]
    G --> H{More Questions?}
    H -->|Yes| A
    H -->|No| I[End Session]
    
    style A fill:#f1f8e9
    style F fill:#c8e6c9
    style G fill:#ffcc80
```

## Key Technical Specifications

### Models Used
| Component | Model | Provider | Purpose |
|-----------|-------|----------|---------|
| Text Generation | x-ai/grok-4.1-fast | OpenRouter | Quiz, Summary, Chat |
| Vision Analysis | x-ai/grok-4.1-fast | OpenRouter | Image understanding |
| Embeddings | qwen/qwen3-embedding-8b | OpenRouter | Semantic search |

### Processing Parameters
| Parameter | Value | Purpose |
|-----------|-------|---------|
| Chunk Size | 1500 chars | Optimal context window |
| Chunk Overlap | 300 chars | Prevent info loss |
| Batch Size (Summary) | 5 chunks | Token optimization |
| Top-K Retrieval | 5 documents | Balance precision/recall |
| Temperature (Quiz) | 0.3 | Balanced creativity |
| Temperature (Summary) | 0.2 | High accuracy |
| Temperature (Chat) | 0.7 | Conversational |

### Performance Metrics
| Operation | Time | Tokens |
|-----------|------|--------|
| Document Upload & Process | 30-60s | - |
| Image Analysis (per image) | 5-10s | 500-1k |
| Quiz Generation | ~30s | 3k-5k |
| Summary Generation | 1-2min | 15k-25k |
| Chat Response | 3-5s | 1k-2k |

## Anti-Hallucination Measures

```mermaid
flowchart LR
    A[Input] --> B[Explicit Instructions<br/>'Only extract EXPLICIT info']
    B --> C[Source Tracking<br/>Page Numbers]
    C --> D[MAP-REDUCE<br/>Smaller Batches]
    D --> E[Low Temperature<br/>0.2 for Summaries]
    E --> F[Verified Output]
    
    style A fill:#ffebee
    style F fill:#c8e6c9
```

## Session State Management

```mermaid
graph TD
    A[User Session Start] --> B{File Uploaded?}
    B -->|No| C[Show Upload Widget]
    B -->|Yes| D[Store in Session State]
    
    D --> E[rag_engine: RAGEngine]
    D --> F[all_chunks: List]
    D --> G[quiz_questions: Dict]
    D --> H[summary: String]
    D --> I[chatbot: Chatbot]
    
    E --> J{Mode Selected}
    F --> J
    G --> J
    H --> J
    I --> J
    
    J -->|Quiz| K[Use/Generate quiz_questions]
    J -->|Summary| L[Use/Generate summary]
    J -->|Chat| M[Use chatbot + rag_engine]
    
    style A fill:#e3f2fd
    style E fill:#fff9c4
    style F fill:#fff9c4
    style G fill:#fff9c4
    style H fill:#fff9c4
    style I fill:#fff9c4
```

## Error Handling Flow

```mermaid
flowchart TD
    A[Operation Start] --> B{Try Operation}
    B -->|Success| C[Return Result]
    B -->|Error| D{Error Type?}
    
    D -->|File Error| E[Show: Invalid file format]
    D -->|API Error| F[Show: API connection issue]
    D -->|Token Error| G[Show: Document too large]
    D -->|Other| H[Show: Generic error + log]
    
    E --> I[Log Error]
    F --> I
    G --> I
    H --> I
    
    I --> J[Allow Retry]
    
    style A fill:#e3f2fd
    style C fill:#c8e6c9
    style D fill:#fff9c4
    style I fill:#ffcc80
```

---

**Legend:**
- 🔵 Blue: User interaction
- 🟢 Green: Successful output
- 🟡 Yellow: Processing stage
- 🟠 Orange: Decision point
- 🔴 Red: AI model inference

