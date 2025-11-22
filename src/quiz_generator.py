from typing import List, Dict
from langchain_openai import ChatOpenAI


class QuizGenerator:
    """Generate multiple-choice quizzes from course material"""
    
    def __init__(self, api_key: str, model: str = "x-ai/grok-4.1-fast"):
        self.llm = ChatOpenAI(
            model=model,
            openai_api_key=api_key,
            openai_api_base="https://openrouter.ai/api/v1",
            temperature=0.7,
            max_tokens=4000
        )
    
    def detect_main_topic(self, context: str) -> str:
        """Detect the main topic of the course material"""
        prompt = f"""Analyze the following course material and identify the SINGLE main topic.
        
        Material:
        {context[:2000]}...
        
        Return ONLY the topic name (e.g., "Cybersecurity: Encryption", "Linear Algebra: Eigenvalues").
        Do not add any other text.
        
        Main Topic:"""
        
        try:
            response = self.llm.invoke(prompt)
            return response.content.strip()
        except Exception:
            return "General Course Material"

    def generate_quiz(self, context: str, num_questions: int = 10, topic: str = None) -> List[Dict]:
        """
        Generate multiple-choice questions from context
        
        Args:
            context: Course material text
            num_questions: Number of questions to generate
            topic: Main topic to focus on
            
        Returns:
            List of question dictionaries
        """
        topic_instruction = f"Focus ALL questions strictly on the topic: {topic}" if topic else "Focus on the main educational concepts."
        
        prompt = f"""Based on the following course material, generate {num_questions} multiple-choice questions.

        prompt = f"""Based on the following course material, generate {num_questions} multiple-choice questions.

Course Material:
{context}

Requirements:
- {topic_instruction}
- Generate questions in the SAME LANGUAGE as the course material
- **Question Variety**: Ensure a mix of question types:
    - 30% Knowledge (Definitions, Facts)
    - 40% Application (Scenarios, "How to", Examples)
    - 30% Analysis (Why, Causes, Implications)
- Each question must test understanding of KEY CONCEPTS or FORMULAS
- DO NOT ask about visual details (colors, shapes, layout, photos)
- DO NOT ask "What is mentioned in the text?" or "According to the document?" -> Ask direct conceptual questions
- Provide 4 options (A, B, C, D) for each question
- Only ONE option should be correct
- Questions should be clear and unambiguous
- **Explanation**: Provide a brief explanation for WHY the correct answer is right.

Format your response EXACTLY as follows (no extra text):

Q1: [Question text]
A) [Option 1]
B) [Option 2]
C) [Option 3]
D) [Option 4]
CORRECT: [A/B/C/D]
EXPLANATION: [Brief explanation]

Q2: [Question text]
...
"""
        
        try:
            response = self.llm.invoke(prompt)
            questions = self._parse_quiz_response(response.content)
            return questions[:num_questions]
            
        except Exception as e:
            print(f"Error generating quiz: {e}")
            return []
    
    def _parse_quiz_response(self, response: str) -> List[Dict]:
        """Parse LLM response into structured quiz format"""
        questions = []
        current_question = None
        current_options = []
        current_explanation = ""
        
        lines = response.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # New question
            if line.startswith(('Q', 'q')) and ':' in line:
                if current_question and current_options:
                    # Save previous question (if valid)
                    pass
                # Extract question text
                current_question = line.split(':', 1)[1].strip()
                current_options = []
                current_explanation = ""
            
            # Options
            elif line.startswith(('A)', 'B)', 'C)', 'D)')):
                option_text = line[2:].strip()
                current_options.append(option_text)
            
            # Correct answer
            elif line.startswith(('CORRECT:', 'Correct:', 'ANSWER:')):
                correct_letter = line.split(':', 1)[1].strip().upper()[0]
                correct_index = ord(correct_letter) - ord('A')
            
            # Explanation
            elif line.startswith(('EXPLANATION:', 'Explanation:')):
                current_explanation = line.split(':', 1)[1].strip()
                
                if current_question and len(current_options) == 4:
                    questions.append({
                        "question": current_question,
                        "options": current_options.copy(),
                        "correct_answer": correct_index,
                        "explanation": current_explanation
                    })
                
                current_question = None
                current_options = []
                current_explanation = ""
        
        return questions
    
    def format_quiz_for_display(self, questions: List[Dict]) -> str:
        """Format quiz questions for display"""
        output = "**Generated Quiz**\n\n"
        
        for i, q in enumerate(questions, 1):
            output += f"**Question {i}:** {q['question']}\n\n"
            
            for j, option in enumerate(q['options']):
                letter = chr(65 + j)  # A, B, C, D
                output += f"{letter}) {option}\n"
            
            output += "\n---\n\n"
        
        return output
    
    def check_answers(self, questions: List[Dict], user_answers: List[int]) -> Dict:
        """
        Check user answers and calculate score
        
        Args:
            questions: List of question dictionaries
            user_answers: List of user's selected answers (indices 0-3)
            
        Returns:
            Dictionary with score, correct answers, and feedback
        """
        if len(user_answers) != len(questions):
            return {"error": "Number of answers doesn't match number of questions"}
        
        correct_count = 0
        results = []
        
        for i, (question, user_answer) in enumerate(zip(questions, user_answers)):
            is_correct = user_answer == question['correct_answer']
            if is_correct:
                correct_count += 1
            
            results.append({
                "question_num": i + 1,
                "correct": is_correct,
                "user_answer": user_answer,
                "correct_answer": question['correct_answer']
            })
        
        score = (correct_count / len(questions)) * 100
        
        return {
            "score": score,
            "correct_count": correct_count,
            "total_questions": len(questions),
            "results": results
        }
