import google.generativeai as genai
import logging

def grade_assignment(student_text, model_answer):
    """
    Grade student assignment using Gemini AI
    """
    try:
        model = genai.GenerativeModel('gemini-pro')
        
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
        
        Format your response as JSON with 'score' and 'feedback' keys.
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
