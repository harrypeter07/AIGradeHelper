import google.generativeai as genai
import logging
import json
import re

def extract_score_from_text(text):
    """Extract score from AI response text"""
    # Look for patterns like "Score: 85" or "85/100" or just "85"
    score_patterns = [
        r"Score:\s*(\d+)",
        r"(\d+)/100",
        r"score of (\d+)",
        r"grade: (\d+)",
    ]

    for pattern in score_patterns:
        if match := re.search(pattern, text, re.IGNORECASE):
            score = int(match.group(1))
            return min(max(score, 0), 100)  # Ensure score is between 0 and 100

    return None

def format_feedback(text):
    """Format the feedback text for better readability"""
    # Remove any JSON-like structures or technical formatting
    text = re.sub(r'{.*}', '', text, flags=re.DOTALL)

    # Clean up the text
    text = text.replace('```', '').strip()

    return text

def grade_assignment(student_text, model_answer=None):
    """
    Grade student assignment using Gemini AI
    Can work with or without model answer
    """
    try:
        # Initialize Gemini with the correct model name
        model = genai.GenerativeModel('gemini-1.0-pro')

        if model_answer:
            prompt = f"""
            You are an expert teacher grading an assignment. 
            Compare the student's answer with the model answer and provide:

            1. A numerical score (0-100)
            2. Detailed constructive feedback with specific examples
            3. Clear suggestions for improvement

            Model Answer:
            {model_answer}

            Student Answer:
            {student_text}

            Begin your response with "Score: [number]" followed by your detailed feedback.
            """
        else:
            prompt = f"""
            You are an expert teacher grading an assignment.
            Analyze the following student submission and provide:

            1. A numerical score (0-100) based on:
               - Depth of understanding (40%)
               - Clarity of expression (30%)
               - Supporting evidence/examples (30%)
            2. Detailed constructive feedback
            3. Specific areas of strength
            4. Clear suggestions for improvement

            Student Answer:
            {student_text}

            Begin your response with "Score: [number]" followed by your detailed feedback.
            """

        response = model.generate_content(prompt)
        response_text = response.text

        # Extract score from response
        score = extract_score_from_text(response_text)
        if score is None:
            logging.error("Could not extract score from response")
            score = 0

        # Format feedback
        feedback = format_feedback(response_text)

        return {
            'score': score,
            'feedback': feedback
        }

    except Exception as e:
        logging.error(f"Error in AI grading: {str(e)}")
        return {
            'score': 0,
            'feedback': f'Error occurred during grading. Please try again. Details: {str(e)}'
        }