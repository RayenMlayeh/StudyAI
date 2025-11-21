"""
Study App - Main Streamlit Application
Upload PDF/PowerPoint → Choose: Quiz | Summary | Chat
"""

import streamlit as st
from pathlib import Path
import tempfile
import shutil
import os
from dotenv import load_dotenv

from src.document_loader import DocumentLoader
from src.document_processor import DocumentProcessor
from src.rag_engine import RAGEngine
from src.quiz_generator import QuizGenerator
from src.summarizer import CourseSummarizer
from src.chatbot import CourseChatbot

# Load environment variables
load_dotenv()

# Configuration
API_KEY = os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY")
MODEL = "x-ai/grok-4.1-fast"
VISION_MODEL = "x-ai/grok-4.1-fast"
TEMP_DIR = "./temp_images"

if not API_KEY:
    st.error("⚠️ API Key not found! Please set OPENROUTER_API_KEY in .env file")
    st.stop()

# Page config
st.set_page_config(
    page_title="Study Assistant",
    page_icon="📚",
    layout="wide"
)

# Initialize session state
if 'rag_engine' not in st.session_state:
    st.session_state.rag_engine = None
if 'quiz_questions' not in st.session_state:
    st.session_state.quiz_questions = None
if 'summary' not in st.session_state:
    st.session_state.summary = None
if 'documents_loaded' not in st.session_state:
    st.session_state.documents_loaded = False
if 'chatbot' not in st.session_state:
    st.session_state.chatbot = None
if 'all_chunks' not in st.session_state:
    st.session_state.all_chunks = []
if 'original_docs' not in st.session_state:
    st.session_state.original_docs = []


def process_uploaded_file(uploaded_file):
    """Process uploaded PDF or PowerPoint file"""
    
    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded_file.name).suffix) as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        tmp_path = tmp_file.name
    
    with st.spinner("📖 Loading document..."):
        # Initialize processors
        doc_loader = DocumentLoader(api_key=API_KEY, vision_model=VISION_MODEL)
        doc_processor = DocumentProcessor()
        
        # Load document
        if uploaded_file.name.endswith('.pdf'):
            text_docs = doc_loader.load_pdf(tmp_path)
            image_paths = doc_loader.extract_images_from_pdf(tmp_path, TEMP_DIR)
        elif uploaded_file.name.endswith('.pptx'):
            text_docs = doc_loader.load_powerpoint(tmp_path)
            image_paths = doc_loader.extract_images_from_pptx(tmp_path, TEMP_DIR)
        else:
            st.error("❌ Unsupported file type. Please upload PDF or PowerPoint.")
            return False
        
        st.info(f"📄 Loaded {len(text_docs)} pages/slides")
        
        # Process images
        image_docs = []
        if image_paths:
            with st.spinner(f"🖼️ Analyzing {len(image_paths)} images..."):
                image_docs = doc_loader.process_images_to_docs(image_paths)
        
        # Merge and chunk documents
        all_docs = doc_processor.merge_documents(text_docs, image_docs)
        chunks = doc_processor.split_documents(all_docs)
        
        st.success(f"✅ Created {len(chunks)} chunks from document")
        
        # Create vector store
        with st.spinner("🔍 Creating vector store..."):
            rag_engine = RAGEngine(api_key=API_KEY)
            success = rag_engine.create_vector_store(chunks)
            
            if success:
                st.session_state.rag_engine = rag_engine
                st.session_state.all_chunks = chunks
                st.session_state.original_docs = all_docs  # Save original merged documents for summary
                st.session_state.documents_loaded = True
                
                # Clean up temp file
                Path(tmp_path).unlink()
                
                return True
    
    return False


def show_quiz_mode():
    """Quiz mode: Generate and display quiz questions"""
    st.header("📝 Quiz Mode")
    
    if not st.session_state.documents_loaded:
        st.warning("⚠️ Please upload a document first")
        return
    
    # Generate quiz button
    if st.session_state.quiz_questions is None:
        if st.button("Generate 10 Questions", type="primary"):
            with st.spinner("🤔 Generating quiz questions..."):
                # Use retriever to get diverse content for quiz generation
                # This samples different parts of the course material
                sample_queries = [
                    "key definitions and concepts",
                    "important formulas and methods",
                    "theoretical concepts and principles",
                    "examples and applications"
                ]
                
                retrieved_chunks = []
                for query in sample_queries:
                    chunks = st.session_state.rag_engine.retrieve_relevant_docs(query, k=5)
                    retrieved_chunks.extend(chunks)
                
                # Remove duplicates and combine
                seen_content = set()
                unique_chunks = []
                for chunk in retrieved_chunks:
                    if chunk.page_content not in seen_content:
                        seen_content.add(chunk.page_content)
                        unique_chunks.append(chunk)
                
                context = "\n\n".join([chunk.page_content for chunk in unique_chunks[:20]])
                
                quiz_gen = QuizGenerator(api_key=API_KEY, model=MODEL)
                questions = quiz_gen.generate_quiz(context, num_questions=10)
                
                if questions:
                    st.session_state.quiz_questions = questions
                    st.rerun()
                else:
                    st.error("❌ Failed to generate quiz")
    
    # Display quiz
    if st.session_state.quiz_questions:
        st.success("✅ Quiz generated! Answer the questions below:")
        
        user_answers = []
        
        for i, q in enumerate(st.session_state.quiz_questions, 1):
            st.markdown(f"### Question {i}")
            st.write(q['question'])
            
            answer = st.radio(
                f"Select your answer:",
                options=q['options'],
                key=f"q{i}",
                index=None
            )
            
            if answer:
                user_answers.append(q['options'].index(answer))
            else:
                user_answers.append(-1)
            
            st.divider()
        
        # Submit button
        if st.button("Submit Quiz", type="primary"):
            if -1 in user_answers:
                st.warning("⚠️ Please answer all questions before submitting")
            else:
                quiz_gen = QuizGenerator(api_key=API_KEY, model=MODEL)
                results = quiz_gen.check_answers(st.session_state.quiz_questions, user_answers)
                
                # Display results
                st.balloons()
                st.success(f"🎯 Your Score: {results['score']:.1f}% ({results['correct_count']}/{results['total_questions']})")
                
                # Show detailed results
                with st.expander("📊 View Detailed Results"):
                    for result in results['results']:
                        q_num = result['question_num']
                        question = st.session_state.quiz_questions[q_num - 1]
                        
                        if result['correct']:
                            st.success(f"✅ Question {q_num}: Correct!")
                        else:
                            st.error(f"❌ Question {q_num}: Incorrect")
                            st.write(f"Your answer: {question['options'][result['user_answer']]}")
                            st.write(f"Correct answer: {question['options'][result['correct_answer']]}")
        
        # Reset quiz button
        if st.button("Generate New Quiz"):
            st.session_state.quiz_questions = None
            st.rerun()


def show_summary_mode():
    """Summary mode: Generate course summary"""
    st.header("📖 Summary Mode")
    
    if not st.session_state.documents_loaded:
        st.warning("⚠️ Please upload a document first")
        return
    
    # Generate summary button
    if st.session_state.summary is None:
        if st.button("Generate Study Guide", type="primary"):
            with st.spinner("📝 Generating comprehensive study guide..."):
                summarizer = CourseSummarizer(api_key=API_KEY, model=MODEL)
                # Use chunks with smaller batch size to avoid token limits
                summary = summarizer.generate_summary(st.session_state.all_chunks, batch_size=5)
                
                st.session_state.summary = summary
                st.rerun()
    
    # Display summary
    if st.session_state.summary:
        st.success("✅ Study guide generated!")
        
        st.markdown(st.session_state.summary)
        
        # Download button
        st.download_button(
            label="📥 Download as Text File",
            data=st.session_state.summary,
            file_name="study_guide.txt",
            mime="text/plain"
        )
        
        # Reset button
        if st.button("Generate New Summary"):
            st.session_state.summary = None
            st.rerun()


def show_chat_mode():
    """Chat mode: Interactive Q&A"""
    st.header("💬 Chat Mode")
    
    if not st.session_state.documents_loaded:
        st.warning("⚠️ Please upload a document first")
        return
    
    # Initialize chatbot
    if st.session_state.chatbot is None:
        st.session_state.chatbot = CourseChatbot(api_key=API_KEY, model=MODEL)
    
    # Display chat history
    for msg in st.session_state.chatbot.get_conversation_history():
        with st.chat_message("user"):
            st.write(msg['question'])
        with st.chat_message("assistant"):
            st.write(msg['answer'])
    
    # Chat input
    question = st.chat_input("Ask a question about the course material...")
    
    if question:
        # Display user question
        with st.chat_message("user"):
            st.write(question)
        
        # Get answer
        with st.chat_message("assistant"):
            with st.spinner("🤔 Thinking..."):
                # Retrieve relevant context
                context = st.session_state.rag_engine.get_context_for_query(question, k=5)
                
                # Generate answer
                answer = st.session_state.chatbot.chat(question, context)
                st.write(answer)
    
    # Clear chat button
    if st.button("🗑️ Clear Chat History"):
        st.session_state.chatbot.reset_conversation()
        st.rerun()


def main():
    """Main application"""
    
    st.title("📚 Study Assistant")
    st.markdown("Upload your course material and choose: **Quiz** | **Summary** | **Chat**")
    
    # Sidebar for file upload
    with st.sidebar:
        st.header("📁 Upload Document")
        
        uploaded_file = st.file_uploader(
            "Choose a PDF or PowerPoint file",
            type=['pdf', 'pptx'],
            help="Upload your course material (lecture notes, slides, etc.)"
        )
        
        if uploaded_file:
            if not st.session_state.documents_loaded:
                if st.button("Process Document", type="primary"):
                    success = process_uploaded_file(uploaded_file)
                    if success:
                        st.rerun()
            else:
                st.success("✅ Document loaded!")
                st.info(f"📄 File: {uploaded_file.name}")
                
                if st.button("Upload New Document"):
                    # Reset state
                    st.session_state.rag_engine = None
                    st.session_state.quiz_questions = None
                    st.session_state.summary = None
                    st.session_state.documents_loaded = False
                    st.session_state.chatbot = None
                    st.session_state.all_chunks = []
                    st.session_state.original_docs = []
                    
                    # Clean up temp files
                    if Path(TEMP_DIR).exists():
                        shutil.rmtree(TEMP_DIR)
                    
                    st.rerun()
    
    # Main content area
    if st.session_state.documents_loaded:
        # Mode selection tabs
        tab1, tab2, tab3 = st.tabs(["📝 Quiz", "📖 Summary", "💬 Chat"])
        
        with tab1:
            show_quiz_mode()
        
        with tab2:
            show_summary_mode()
        
        with tab3:
            show_chat_mode()
    
    else:
        # Welcome message
        st.info("👈 Upload a document from the sidebar to get started")
        
        st.markdown("""
        ### How to use:
        
        1. **Upload** your course material (PDF or PowerPoint)
        2. **Choose** a mode:
           - **📝 Quiz**: Get 10 multiple-choice questions to test your knowledge
           - **📖 Summary**: Generate a comprehensive study guide
           - **💬 Chat**: Ask questions about the material
        
        ### Features:
        
        - 🖼️ **Image Analysis**: Extracts text from diagrams, charts, and formulas
        - 🔍 **Smart Search**: Finds relevant information quickly
        - 🤖 **AI-Powered**: Uses advanced language models for accurate answers
        """)


if __name__ == "__main__":
    main()
