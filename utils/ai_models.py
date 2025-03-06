import os
import logging
import google.generativeai as genai
from openai import OpenAI
from typing import Dict, List, Optional, Tuple

class AIModelManager:
    """Manages multiple AI models for assignment grading"""
    
    def __init__(self):
        self.models = {}
        self.setup_models()
        
    def setup_models(self):
        """Initialize available AI models"""
        # Setup Gemini
        try:
            genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))
            self.models['gemini'] = {
                'name': 'gemini-1.5-pro',
                'type': 'gemini',
                'weight': 1.0,
                'enabled': True
            }
            logging.info("Gemini model initialized successfully")
        except Exception as e:
            logging.error(f"Failed to initialize Gemini: {str(e)}")
            self.models['gemini'] = {'enabled': False}

        # Setup OpenAI
        try:
            openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024
            self.models['openai'] = {
                'name': 'gpt-4o',
                'client': openai_client,
                'type': 'openai',
                'weight': 1.0,
                'enabled': True
            }
            logging.info("OpenAI model initialized successfully")
        except Exception as e:
            logging.error(f"Failed to initialize OpenAI: {str(e)}")
            self.models['openai'] = {'enabled': False}

    def get_enabled_models(self) -> List[Dict]:
        """Return list of enabled models"""
        return [model for model in self.models.values() if model.get('enabled', False)]

    async def grade_with_model(self, model: Dict, student_text: str, model_answer: Optional[str] = None) -> Tuple[float, str]:
        """Grade assignment using specific model"""
        try:
            if model['type'] == 'gemini':
                return await self._grade_with_gemini(model, student_text, model_answer)
            elif model['type'] == 'openai':
                return await self._grade_with_openai(model, student_text, model_answer)
            else:
                raise ValueError(f"Unsupported model type: {model['type']}")
        except Exception as e:
            logging.error(f"Error grading with {model['type']}: {str(e)}")
            return 0, f"Error with {model['type']} grading: {str(e)}"

    async def _grade_with_gemini(self, model: Dict, student_text: str, model_answer: Optional[str]) -> Tuple[float, str]:
        """Grade using Gemini model"""
        prompt = self._create_grading_prompt(student_text, model_answer)
        gemini_model = genai.GenerativeModel(model['name'])
        response = await gemini_model.generate_content(prompt)
        
        # Extract score and feedback from response
        response_text = response.text
        score = self._extract_score(response_text)
        feedback = self._format_feedback(response_text)
        
        return score, feedback

    async def _grade_with_openai(self, model: Dict, student_text: str, model_answer: Optional[str]) -> Tuple[float, str]:
        """Grade using OpenAI model"""
        prompt = self._create_grading_prompt(student_text, model_answer)
        response = await model['client'].chat.completions.create(
            model=model['name'],
            messages=[
                {"role": "system", "content": "You are an expert teacher grading assignments."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "text"}
        )
        
        response_text = response.choices[0].message.content
        score = self._extract_score(response_text)
        feedback = self._format_feedback(response_text)
        
        return score, feedback

    def _create_grading_prompt(self, student_text: str, model_answer: Optional[str]) -> str:
        """Create grading prompt based on available answer"""
        if model_answer:
            return f"""
            Compare the student's answer with the model answer and provide:
            1. A numerical score (0-100)
            2. Detailed constructive feedback
            3. Suggestions for improvement

            Model Answer:
            {model_answer}

            Student Answer:
            {student_text}

            Begin your response with "Score: [number]" followed by your detailed feedback.
            """
        else:
            return f"""
            Analyze the following student submission and provide:
            1. A numerical score (0-100) based on:
               - Understanding (40%)
               - Expression (30%)
               - Evidence (30%)
            2. Detailed feedback
            3. Improvement suggestions

            Student Answer:
            {student_text}

            Begin your response with "Score: [number]" followed by your detailed feedback.
            """

    def _extract_score(self, text: str) -> float:
        """Extract numerical score from model response"""
        import re
        patterns = [
            r"Score:\s*(\d+)",
            r"(\d+)/100",
            r"score of (\d+)",
            r"grade: (\d+)",
        ]
        
        for pattern in patterns:
            if match := re.search(pattern, text, re.IGNORECASE):
                score = float(match.group(1))
                return min(max(score, 0), 100)
        return 0

    def _format_feedback(self, text: str) -> str:
        """Format feedback for consistency"""
        text = text.replace('```', '').strip()
        # Remove score line from feedback
        lines = text.split('\n')
        feedback_lines = [line for line in lines if not line.strip().lower().startswith('score:')]
        return '\n'.join(feedback_lines).strip()

model_manager = AIModelManager()
