# AI Assignment Grader

An AI-powered assignment grading system leveraging Gemini AI with robust error handling and advanced feedback capabilities.

## Features

- PDF assignment submission and processing
- AI-powered grading with detailed feedback
- Sentiment analysis of submissions
- Beautiful, responsive UI with Google Material Design
- Structured feedback presentation with strengths and improvements
- Print-friendly reports

## Setup

1. Environment Variables Required:
   - `GOOGLE_API_KEY`: Your Google API key for Gemini AI
   - `SESSION_SECRET`: Secret key for Flask sessions

2. Dependencies:
   - Python 3.11
   - Flask
   - Google Generative AI
   - PyPDF2
   - Other dependencies in requirements.txt

## Usage

1. Upload a student assignment (PDF)
2. Optionally upload a model answer (PDF)
3. Get instant feedback with:
   - Numerical score
   - Sentiment analysis
   - Structured feedback
   - Actionable suggestions

## Development

The project uses Flask for the web framework and Gemini AI for grading assignments. The UI is built with Bootstrap and custom CSS for a modern, responsive design.

### Project Structure

```
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── main.js
├── templates/
│   ├── base.html
│   ├── index.html
│   └── results.html
├── utils/
│   ├── ai_grader.py
│   └── pdf_processor.py
├── app.py
└── main.py
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request
