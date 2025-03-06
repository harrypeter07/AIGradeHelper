import google.generativeai as genai
import logging
import json
import re

def analyze_sentiment(text):
    """Analyze the sentiment of the text and return a confidence level"""
    try:
        model = genai.GenerativeModel('gemini-1.5-pro')
        prompt = f"""
        Analyze the sentiment and confidence of this academic text:
        {text}

        Provide a structured response with:
        1. Confidence level (0-1)
        2. Overall tone (positive/neutral/negative)
        3. Key sentiment indicators

        Format as: "Confidence: [0-1], Tone: [type], Indicators: [list]"
        """

        response = model.generate_content(prompt)
        text = response.text.strip()

        # Extract confidence
        confidence_match = re.search(r'Confidence:\s*(0\.\d+|1\.0|1)', text)
        confidence = float(confidence_match.group(1)) if confidence_match else 0.5

        # Extract tone
        tone_match = re.search(r'Tone:\s*(positive|neutral|negative)', text.lower())
        tone = tone_match.group(1) if tone_match else 'neutral'

        return {
            'confidence': confidence,
            'tone': tone
        }
    except Exception as e:
        logging.error(f"Error in sentiment analysis: {str(e)}")
        return {'confidence': 0.5, 'tone': 'neutral'}

def extract_score_from_text(text):
    """Extract score from AI response text"""
    score_patterns = [
        r"Score:\s*(\d+)",
        r"(\d+)/100",
        r"score of (\d+)",
        r"grade: (\d+)",
    ]

    for pattern in score_patterns:
        if match := re.search(pattern, text, re.IGNORECASE):
            score = int(match.group(1))
            return min(max(score, 0), 100)

    return None

def format_feedback(text):
    """Format the feedback text for better readability"""
    # Remove any technical formatting
    text = text.replace('```', '').strip()

    # Structure the feedback into sections
    sections = {
        'Strengths': [],
        'Areas for Improvement': [],
        'Suggestions': []
    }

    # Extract sections from the text
    current_section = None
    for line in text.split('\n'):
        line = line.strip()
        if not line:
            continue

        lower_line = line.lower()
        if 'strength' in lower_line or 'positive' in lower_line:
            current_section = 'Strengths'
        elif 'improve' in lower_line or 'weakness' in lower_line:
            current_section = 'Areas for Improvement'
        elif 'suggest' in lower_line or 'recommend' in lower_line:
            current_section = 'Suggestions'
        elif current_section and line[0] in ['-', '*', '•'] or line[0].isdigit():
            sections[current_section].append(line.lstrip('- *•1234567890. '))

    # Format the output
    formatted_text = []
    for section, points in sections.items():
        if points:
            formatted_text.append(f"<h3>{section}</h3>")
            formatted_text.append("<ul>")
            formatted_text.extend([f"<li>{point}</li>" for point in points])
            formatted_text.append("</ul>")

    return "\n".join(formatted_text)

def grade_assignment(student_text, model_answer=None):
    """
    Grade student assignment using Gemini AI
    Includes sentiment analysis and structured feedback
    """
    try:
        model_name = 'gemini-1.5-pro'
        model = genai.GenerativeModel(model_name)
        logging.info("Initialized Gemini model")

        # Analyze sentiment first
        sentiment = analyze_sentiment(student_text)

        if model_answer:
            prompt = f"""
            You are an expert teacher grading an assignment. 
            Compare the student's answer with the model answer and provide:

            1. A numerical score (0-100)
            2. Strengths:
               - List specific positive aspects
               - Highlight effective elements
            3. Areas for Improvement:
               - Identify gaps compared to model answer
               - Note any missing key points
            4. Suggestions:
               - Provide actionable recommendations
               - Reference the model answer where relevant

            Model Answer:
            {model_answer}

            Student Answer:
            {student_text}

            Begin with "Score: [number]" followed by detailed feedback in sections.
            """
        else:
            prompt = f"""
            You are an expert teacher grading an assignment.
            Analyze the following student submission and provide:

            1. A numerical score (0-100) based on:
               - Depth of understanding (40%)
               - Clarity of expression (30%)
               - Supporting evidence/examples (30%)
            2. Strengths:
               - List specific positive aspects
               - Highlight effective elements
            3. Areas for Improvement:
               - Identify potential enhancements
               - Note any unclear points
            4. Suggestions:
               - Provide actionable recommendations
               - Give specific examples for improvement

            Student Answer:
            {student_text}

            Begin with "Score: [number]" followed by detailed feedback in sections.
            """

        logging.info("Sending request to Gemini API")
        response = model.generate_content(prompt)
        response_text = response.text
        logging.info(f"Received response from Gemini API: {response_text[:100]}...")

        # Extract score and format feedback
        score = extract_score_from_text(response_text)
        if score is None:
            logging.error("Could not extract score from response")
            score = 0

        feedback = format_feedback(response_text)

        return {
            'score': score,
            'feedback': feedback,
            'sentiment': sentiment
        }

    except Exception as e:
        logging.error(f"Error in AI grading: {str(e)}")
        return {
            'score': 0,
            'feedback': f'Error occurred during grading. Please try again. Details: {str(e)}',
            'sentiment': {'confidence': 0.5, 'tone': 'neutral'}
        }