import google.generativeai as genai
import logging

def grade_assignment(student_text, model_answer=None):
    """
    Grade student assignment using Gemini AI
    Can work with or without model answer
    """
    try:
        model = genai.GenerativeModel('gemini-pro')

        if model_answer:
            prompt = f"""
            You are an expert teacher grading an assignment. 
            Compare the student's answer with the model answer and:
            1. Assign a score between 0-100
            2. Provide detailed constructive feedback
            3. Highlight areas for improvement

            Model Answer:
            {model_answer}

            Student Answer:
            {student_text}
            """
        else:
            prompt = f"""
            You are an expert teacher grading an assignment.
            Analyze the following student submission and:
            1. Evaluate the clarity, completeness, and accuracy of the answer
            2. Assign a score between 0-100 based on:
               - Depth of understanding (40%)
               - Clarity of expression (30%)
               - Supporting evidence/examples (30%)
            3. Provide detailed constructive feedback
            4. Highlight areas for improvement

            Student Answer:
            {student_text}
            """

        response = model.generate_content(prompt)
        result = eval(response.text)  # Safely evaluate the JSON response

        return {
            'score': result['score'],
            'feedback': result['feedback']
        }

    except Exception as e:
        logging.error(f"Error in AI grading: {str(e)}")
        return {
            'score': 0,
            'feedback': 'Error occurred during grading. Please try again.'
        }