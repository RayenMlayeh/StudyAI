"""
Quiz Generator Module
Creates multiple-choice questions from course material
"""

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
    
    def generate_quiz(self, context: str, num_questions: int = 10) -> List[Dict]:
        """
        Generate multiple-choice questions from context
        
        Args:
            context: Course material text
            num_questions: Number of questions to generate
            
        Returns:
            List of question dictionaries with format:
            {
                "question": str,
                "options": [str, str, str, str],
                "correct_answer": int (0-3)
            }
        """
        prompt = f"""Based on the following course material, generate {num_questions} multiple-choice questions.

Course Material:
{context}

Requirements:
- Each question should test understanding of key concepts
- Provide 4 options (A, B, C, D) for each question
- Only ONE option should be correct
- Questions should be clear and unambiguous
- Cover different topics from the material

Format your response EXACTLY as follows (no extra text):

Q1: [Question text]
A) [Option 1]
B) [Option 2]
C) [Option 3]
D) [Option 4]
CORRECT: [A/B/C/D]

Q2: [Question text]
A) [Option 1]
B) [Option 2]
C) [Option 3]
D) [Option 4]
CORRECT: [A/B/C/D]

(Continue for all {num_questions} questions)
"""
        
        try:
            response = self.llm.invoke(prompt)
            questions = self._parse_quiz_response(response.content)
            return questions[:num_questions]
            
        except Exception as e:
            print(f"✗ Error generating quiz: {e}")
            return []
    
    def _parse_quiz_response(self, response: str) -> List[Dict]:
        """Parse LLM response into structured quiz format"""
        questions = []
        current_question = None
        current_options = []
        
        lines = response.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # New question
            if line.startswith(('Q', 'q')) and ':' in line:
                if current_question and current_options:
                    # Save previous question
                    pass
                # Extract question text
                current_question = line.split(':', 1)[1].strip()
                current_options = []
            
            # Options
            elif line.startswith(('A)', 'B)', 'C)', 'D)')):
                option_text = line[2:].strip()
                current_options.append(option_text)
            
            # Correct answer
            elif line.startswith(('CORRECT:', 'Correct:', 'ANSWER:')):
                correct_letter = line.split(':', 1)[1].strip().upper()[0]
                correct_index = ord(correct_letter) - ord('A')
                
                if current_question and len(current_options) == 4:
                    questions.append({
                        "question": current_question,
                        "options": current_options.copy(),
                        "correct_answer": correct_index
                    })
                
                current_question = None
                current_options = []
        
        return questions
    
    def format_quiz_for_display(self, questions: List[Dict]) -> str:
        """Format quiz questions for display"""
        output = "📝 **Generated Quiz**\n\n"
        
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
