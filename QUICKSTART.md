# 🚀 Quick Start Guide

This guide will get you up and running with ResumeCour in under 5 minutes.

## Prerequisites Checklist

- [ ] Python 3.8+ installed ([Download](https://www.python.org/downloads/))
- [ ] Git installed (optional, for cloning)
- [ ] OpenRouter API key ([Get one free](https://openrouter.ai))

## Installation (3 steps)

### Step 1: Get the Code

**Option A: Clone with Git**
```bash
git clone https://github.com/RayenMlayeh/ResumeCour.git
cd ResumeCour
```

**Option B: Download ZIP**
1. Download from GitHub
2. Extract the ZIP file
3. Open terminal in the extracted folder

### Step 2: Install Dependencies

**On Windows:**
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

**On Mac/Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Step 3: Configure API Key

**Option A: Environment Variable (Recommended)**
```bash
# Create .env file
cp .env.example .env

# Edit .env and add your key:
OPENROUTER_API_KEY=sk-or-v1-your-actual-key-here
```

**Option B: Direct in Code**
Edit `app.py` line 12:
```python
API_KEY = "sk-or-v1-your-actual-key-here"
```

## Run the App

```bash
streamlit run app.py
```

The app will automatically open in your browser at `http://localhost:8501`

## First Use Tutorial

### 1. Upload a Document

- Click **"Browse files"** or drag & drop
- Supported formats: PDF, PowerPoint (PPTX)
- Upload your own course materials

⏳ **Wait ~30 seconds** while it processes (you'll see a spinner)

### 2. Try Quiz Mode

- Click the **"📝 Quiz Mode"** tab
- Wait for 10 questions to generate (~30 seconds)
- Select your answers
- Click **"Submit Quiz"**
- See your score and feedback!

### 3. Try Summary Mode

- Click the **"📖 Summary Mode"** tab
- Wait for summary generation (~1-2 minutes)
- Read the comprehensive 9-section study guide
- Copy sections you need

### 4. Try Chat Mode

- Click the **"💬 Chat Mode"** tab
- Type a question like: "What are the main concepts?"
- Get instant answers with sources
- Ask follow-up questions!

## Troubleshooting

### "No module named 'streamlit'"
```bash
# Make sure virtual environment is activated
# Windows:
.venv\Scripts\activate

# Mac/Linux:
source .venv/bin/activate

# Then reinstall:
pip install -r requirements.txt
```

### "API Key Error"
- Check your API key is correct in `.env` or `app.py`
- Verify your OpenRouter account is active
- Try generating a new API key

### "Command 'streamlit' not found"
```bash
# Install streamlit explicitly:
pip install streamlit

# Or use full path:
python -m streamlit run app.py
```

### Port 8501 Already in Use
```bash
# Use a different port:
streamlit run app.py --server.port 8502
```

## Tips for Best Results

✅ **DO:**
- Use clear, text-rich PDF documents
- Upload one chapter or section at a time
- Wait for processing to complete before switching modes
- Ask specific questions in Chat mode

❌ **DON'T:**
- Upload scanned images without OCR
- Upload extremely large files (>100 pages)
- Submit multiple requests simultaneously
- Expect instant responses (AI takes time!)

## Next Steps

Once you're comfortable with the basics:

1. **Read the full [README.md](README.md)** for detailed features
2. **Check [ARCHITECTURE.md](ARCHITECTURE.md)** to understand how it works
3. **View [docs/PIPELINE_DIAGRAM.md](docs/PIPELINE_DIAGRAM.md)** for visual workflows
4. **Contribute!** See [CONTRIBUTING.md](CONTRIBUTING.md)

## Getting Help

- 📖 **Documentation**: Check README.md and ARCHITECTURE.md
- 🐛 **Bug Report**: Open an issue on GitHub
- 💡 **Feature Request**: Open an issue with "Feature:" prefix
- 💬 **Questions**: Open a discussion on GitHub

## Performance Expectations

| Operation | Expected Time |
|-----------|--------------|
| Upload & Process (10 pages) | ~15 seconds |
| Upload & Process (50 pages) | ~30-60 seconds |
| Quiz Generation | ~30 seconds |
| Summary Generation (50 pages) | ~1-2 minutes |
| Chat Response | ~3-5 seconds |
| Image Analysis (per image) | ~5-10 seconds |

## System Requirements

- **RAM**: 2GB minimum, 4GB recommended
- **Disk Space**: ~500MB (for models and dependencies)
- **Internet**: Stable connection required (API calls)
- **Browser**: Modern browser (Chrome, Firefox, Safari, Edge)

## Updating

To get the latest version:

```bash
cd ResumeCour
git pull origin main
pip install -r requirements.txt --upgrade
```

---

**You're all set! 🎉** Start learning smarter with ResumeCour!

Need help? Open an issue: https://github.com/RayenMlayeh/ResumeCour/issues
