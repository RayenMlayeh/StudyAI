# 📚 ResumeCour - AI Study Assistant

> Transform your course materials into interactive learning experiences with AI-powered quizzes, summaries, and Q&A chat.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/streamlit-1.31.0+-red.svg)](https://streamlit.io/)
[![LangChain](https://img.shields.io/badge/langchain-0.2.0+-green.svg)](https://python.langchain.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🎯 Features

### 📝 Quiz Mode
- **Generate 10 multiple-choice questions** from your course material
- Uses **RAG retrieval** to extract diverse concepts (definitions, formulas, examples)
- Instant scoring and detailed feedback
- Perfect for exam preparation

### 📖 Summary Mode
- Creates **comprehensive study guides** with 9 structured sections:
  - Course Introduction & Objectives
  - Key Concepts & Definitions
  - Core Theories & Frameworks
  - Important Formulas & Equations
  - Examples & Case Studies
  - Common Misconceptions
  - Study Tips & Tricks
  - Practice Questions & Exercises
  - Summary & Review
- Uses **MAP-REDUCE strategy** for scalable document processing
- Token-optimized with batch processing (5 chunks per batch)

### 💬 Chat Mode
- **Interactive Q&A** with your course material
- Maintains conversation context (last 3 exchanges)
- RAG-powered with top-5 relevant chunks retrieval
- Real-time answers with source references

### 🖼️ Vision Analysis
- **Automatic image extraction** from PDFs
- AI-powered analysis of diagrams, charts, and formulas
- Converts visual content to searchable text
- Powered by Grok Vision model

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      📤 File Upload                          │
│              (PDF, PowerPoint, Images)                       │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   📑 Document Loading                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ Text Extract │  │ Image Extract│  │ Vision Model │     │
│  │   (PyMuPDF)  │  │   (PyMuPDF)  │  │  (Grok 4.1)  │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   ✂️ Text Chunking                          │
│  Recursive Character Splitter (1500 chars, 300 overlap)     │
│  9-level hierarchical separators                            │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  🧠 Embedding Generation                     │
│  Model: qwen/qwen3-embedding-8b via OpenRouter              │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  💾 Vector Store (ChromaDB)                  │
│  Semantic search with cosine similarity                      │
└────────────────────────┬────────────────────────────────────┘
                         │
             ┌───────────┼───────────┐
             │           │           │
             ▼           ▼           ▼
    ┌────────────┐ ┌──────────┐ ┌─────────┐
    │ 📝 Quiz    │ │ 📖 Summary│ │💬 Chat  │
    │   Mode     │ │   Mode    │ │  Mode   │
    └────────────┘ └──────────┘ └─────────┘
         │              │             │
         ▼              ▼             ▼
    ┌────────────────────────────────────┐
    │      🤖 Grok 4.1 Fast LLM          │
    │   (Text Generation & Vision)       │
    └────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- OpenRouter API key (get one at [openrouter.ai](https://openrouter.ai))

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/RayenMlayeh/ResumeCour.git
cd ResumeCour
```

2. **Create a virtual environment**
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up your API key**

Create a `.env` file in the project root:
```env
OPENROUTER_API_KEY=your_api_key_here
```

Or edit `app.py` directly (line 12):
```python
API_KEY = "your_api_key_here"
```

### Running the App

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## 📖 Usage Guide

### 1️⃣ Upload Your Course Material
- Click **"Browse files"** or drag & drop
- Supported formats: **PDF**, **PowerPoint** (PPTX)
- Files with images are automatically analyzed

### 2️⃣ Choose Your Mode

#### Quiz Mode
1. Click on the **"📝 Quiz Mode"** tab
2. Wait for questions to generate (~30 seconds)
3. Select your answers
4. Submit to see your score and feedback

#### Summary Mode
1. Click on the **"📖 Summary Mode"** tab
2. Wait for processing (~1-2 minutes for large documents)
3. Review the 9-section study guide
4. Copy sections or export as needed

#### Chat Mode
1. Click on the **"💬 Chat Mode"** tab
2. Type your question in the input box
3. Get instant answers with source references
4. Ask follow-up questions (context maintained)

## 📁 Project Structure

```
ResumeCour/
├── app.py                      # Main Streamlit application
├── src/
│   ├── __init__.py
│   ├── document_loader.py      # PDF/PPTX loading & vision analysis
│   ├── document_processor.py   # Text chunking with statistics
│   ├── rag_engine.py           # Vector store & retrieval
│   ├── quiz_generator.py       # Quiz generation with scoring
│   ├── summarizer.py           # MAP-REDUCE summarization
│   └── chatbot.py              # Interactive Q&A with memory
├── docs/                       # Documentation files
├── notebooks/                  # Jupyter development notebooks
├── requirements.txt            # Python dependencies
├── pyproject.toml              # Project configuration
├── .gitignore                  # Git ignore patterns
└── README.md                   # This file
```

## 🛠️ Technologies

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **UI Framework** | Streamlit | Web interface |
| **LLM** | x-ai/grok-4.1-fast | Text generation & vision |
| **Embeddings** | qwen/qwen3-embedding-8b | Semantic search |
| **API Provider** | OpenRouter | Model access |
| **RAG Framework** | LangChain | Document processing pipeline |
| **Vector DB** | ChromaDB | Semantic search storage |
| **PDF Processing** | PyMuPDF (fitz) | Text & image extraction |
| **PPTX Processing** | python-pptx | PowerPoint parsing |

## ⚙️ Configuration

### Model Settings
Located in `app.py`:
```python
MODEL = "x-ai/grok-4.1-fast"           # Text generation & vision
EMBEDDING_MODEL = "qwen/qwen3-embedding-8b"  # Embeddings
TEMPERATURE = 0.2                       # Lower = more focused
```

### Chunking Parameters
Located in `src/document_processor.py`:
```python
CHUNK_SIZE = 1500        # Characters per chunk
CHUNK_OVERLAP = 300      # Overlap between chunks
```

### Retrieval Settings
Located in `src/rag_engine.py` and `app.py`:
```python
k = 5                    # Top-k documents to retrieve
```

## 💡 Tips & Best Practices

- ✅ **Upload clear, text-rich documents** for best results
- ✅ **PDF files with images** are automatically analyzed with vision AI
- ✅ **Larger documents** may take 1-2 minutes to process
- ✅ **Quiz questions** are generated from diverse concepts across your material
- ✅ **Chat mode** remembers your last 3 questions for better context
- ✅ **Summaries** use MAP-REDUCE to handle documents of any size
- ⚠️ **API rate limits** may apply - wait a few seconds between large requests

## 🐛 Troubleshooting

### "404 Model not found"
- Check your API key is valid
- Verify the model name in `app.py` matches OpenRouter's available models

### "Token limit exceeded"
- The app uses chunking to prevent this (batch_size=5)
- Try splitting very large documents into smaller sections

### Images not extracted
- Ensure PyMuPDF is installed: `pip install PyMuPDF`
- Check that your PDF contains embedded images (not scanned pages)

### Slow processing
- Large documents take longer (1-2 min for 50+ pages)
- Vision analysis adds ~5-10 seconds per image
- Consider using smaller documents for faster testing

## 📊 Performance Metrics

- **Quiz Generation**: ~30 seconds (10 questions)
- **Summary Generation**: ~1-2 minutes (50 pages)
- **Chat Response**: ~3-5 seconds per query
- **Image Analysis**: ~5-10 seconds per image
- **Token Usage**: 
  - Quiz: ~3,000-5,000 tokens
  - Summary: ~15,000-25,000 tokens (batch optimized)
  - Chat: ~1,000-2,000 tokens per exchange

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **OpenRouter** for providing access to powerful AI models
- **LangChain** for the excellent RAG framework
- **Streamlit** for the intuitive web framework
- **x.ai** for the Grok model
- **Alibaba Cloud** for the Qwen embedding model

## 📧 Contact

Rayen Mlayeh - [@RayenMlayeh](https://github.com/RayenMlayeh)

Project Link: [https://github.com/RayenMlayeh/ResumeCour](https://github.com/RayenMlayeh/ResumeCour)

---
