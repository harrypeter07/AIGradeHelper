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
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY", "your-api-key")
genai.configure(api_key=GOOGLE_API_KEY)

# Configure upload settings
UPLOAD_FOLDER = '/tmp/uploads'
ALLOWED_EXTENSIONS = {'pdf'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_files():
    if 'student_assignment' not in request.files or 'model_answer' not in request.files:
        flash('Both files are required')
        return redirect(url_for('index'))
    
    student_file = request.files['student_assignment']
    model_file = request.files['model_answer']
    
    if student_file.filename == '' or model_file.filename == '':
        flash('No selected files')
        return redirect(url_for('index'))
    
    if not (allowed_file(student_file.filename) and allowed_file(model_file.filename)):
        flash('Invalid file type. Please upload PDF files only.')
        return redirect(url_for('index'))
    
    try:
        # Save and process files
        student_filename = secure_filename(student_file.filename)
        model_filename = secure_filename(model_file.filename)
        
        student_path = os.path.join(app.config['UPLOAD_FOLDER'], student_filename)
        model_path = os.path.join(app.config['UPLOAD_FOLDER'], model_filename)
        
        student_file.save(student_path)
        model_file.save(model_path)
        
        # Extract text from PDFs
        student_text = extract_text_from_pdf(student_path)
        model_text = extract_text_from_pdf(model_path)
        
        # Grade the assignment
        grade_result = grade_assignment(student_text, model_text)
        
        # Clean up files
        os.remove(student_path)
        os.remove(model_path)
        
        return render_template('results.html', 
                             score=grade_result['score'],
                             feedback=grade_result['feedback'])
    
    except Exception as e:
        logging.error(f"Error processing files: {str(e)}")
        flash('An error occurred while processing the files')
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
