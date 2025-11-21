"""
Chatbot Module
Interactive chat interface for Q&A about course material
"""

from typing import List, Dict
from langchain_openai import ChatOpenAI


class CourseChatbot:
    """Interactive chatbot for answering questions about course material"""
    
    def __init__(self, api_key: str, model: str = "x-ai/grok-4.1-fast"):
        self.llm = ChatOpenAI(
            model=model,
            openai_api_key=api_key,
            openai_api_base="https://openrouter.ai/api/v1",
            temperature=0.3,
            max_tokens=2000
        )
        self.conversation_history: List[Dict[str, str]] = []
    
    def chat(self, question: str, context: str) -> str:
        """
        Answer a question based on course material
        
        Args:
            question: User's question
            context: Relevant course material from RAG retrieval
            
        Returns:
            Answer text
        """
        # Build conversation context
        conversation = ""
        if self.conversation_history:
            conversation = "\n".join([
                f"User: {msg['question']}\nAssistant: {msg['answer']}"
                for msg in self.conversation_history[-3:]  # Last 3 exchanges
            ])
        
        prompt = f"""You are a helpful study assistant. Answer the student's question based on the course material provided.

Course Material:
{context}

{f"Previous Conversation:{conversation}" if conversation else ""}

Student's Question: {question}

Instructions:
- Answer in the SAME LANGUAGE as the student's question (if they ask in French, respond in French; if English, respond in English)
- Answer clearly and concisely
- Use information from the course material
- If the answer isn't in the material, say so politely
- Explain concepts in simple terms
- Use examples when helpful

Answer:
"""
        
        try:
            response = self.llm.invoke(prompt)
            answer = response.content
            
            # Save to history
            self.conversation_history.append({
                "question": question,
                "answer": answer
            })
            
            return answer
            
        except Exception as e:
            return f"Sorry, I encountered an error: {str(e)}"
    
    def reset_conversation(self):
        """Clear conversation history"""
        self.conversation_history = []
    
    def get_conversation_history(self) -> List[Dict[str, str]]:
        """Get the conversation history"""
        return self.conversation_history.copy()
