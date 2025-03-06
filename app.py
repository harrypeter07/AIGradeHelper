import os
import logging
from flask import Flask, render_template, request, jsonify, flash, redirect, url_for
from werkzeug.utils import secure_filename
from utils.pdf_processor import extract_text_from_pdf
from utils.ai_grader import grade_assignment
import google.generativeai as genai

# Configure logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")

# Configure Gemini AI
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    logging.error("GOOGLE_API_KEY not found in environment variables")
    raise ValueError("GOOGLE_API_KEY is required")

try:
    genai.configure(api_key=GOOGLE_API_KEY)
    # Verify configuration by listing available models
    model_list = genai.list_models()
    logging.info("Available models: %s", [m.name for m in model_list])
except Exception as e:
    logging.error(f"Error configuring Gemini AI: {str(e)}")
    raise

# Configure upload settings
UPLOAD_FOLDER = 'tmp/uploads'
ALLOWED_EXTENSIONS = {'pdf'}

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def clean_uploaded_file(filepath):
    """Safely clean up uploaded file"""
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
    except Exception as e:
        logging.error(f"Error cleaning up file {filepath}: {e}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_files():
    student_path = None
    model_path = None

    try:
        # Validate student assignment
        if 'student_assignment' not in request.files:
            flash('Student assignment is required')
            return redirect(url_for('index'))

        student_file = request.files['student_assignment']
        if student_file.filename == '':
            flash('No selected file')
            return redirect(url_for('index'))

        if not allowed_file(student_file.filename):
            flash('Invalid file type. Please upload PDF files only.')
            return redirect(url_for('index'))

        # Save and process student file
        student_filename = secure_filename(student_file.filename)
        student_path = os.path.join(app.config['UPLOAD_FOLDER'], student_filename)
        student_file.save(student_path)
        logging.info(f"Saved student file: {student_path}")

        # Extract text from student PDF
        student_text = extract_text_from_pdf(student_path)
        if not student_text.strip():
            raise ValueError("Could not extract text from student PDF. The file might be empty or corrupted.")

        # Process model answer if provided
        model_text = None
        if 'model_answer' in request.files:
            model_file = request.files['model_answer']
            if model_file.filename != '' and allowed_file(model_file.filename):
                model_filename = secure_filename(model_file.filename)
                model_path = os.path.join(app.config['UPLOAD_FOLDER'], model_filename)
                model_file.save(model_path)
                logging.info(f"Saved model answer file: {model_path}")

                model_text = extract_text_from_pdf(model_path)
                if not model_text.strip():
                    raise ValueError("Could not extract text from model answer PDF. The file might be empty or corrupted.")

        # Grade the assignment
        logging.info("Starting assignment grading")
        grade_result = grade_assignment(student_text, model_text)
        logging.info("Completed assignment grading")

        if grade_result['score'] == 0 and 'error' in grade_result.get('feedback', '').lower():
            raise ValueError(grade_result['feedback'])

        return render_template('results.html', 
                             score=grade_result['score'],
                             feedback=grade_result['feedback'],
                             sentiment=grade_result.get('sentiment', {'tone': 'neutral', 'confidence': 0.5}))

    except Exception as e:
        logging.error(f"Error processing files: {str(e)}")
        flash(f'Error processing files: {str(e)}')
        return redirect(url_for('index'))

    finally:
        # Clean up uploaded files
        if student_path:
            clean_uploaded_file(student_path)
        if model_path:
            clean_uploaded_file(model_path)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)