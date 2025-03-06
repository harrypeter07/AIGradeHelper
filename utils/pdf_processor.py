import PyPDF2
import logging
import os

def extract_text_from_pdf(pdf_path):
    """
    Extract text content from a PDF file with enhanced error handling
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    try:
        text = ""
        with open(pdf_path, 'rb') as file:
            # Try to read the PDF
            try:
                pdf_reader = PyPDF2.PdfReader(file)
            except Exception as e:
                raise ValueError(f"Invalid or corrupted PDF file: {str(e)}")

            # Check if PDF has pages
            if len(pdf_reader.pages) == 0:
                raise ValueError("The PDF file is empty (no pages found)")

            # Extract text from each page
            for page in pdf_reader.pages:
                try:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                except Exception as e:
                    logging.warning(f"Error extracting text from page: {str(e)}")
                    continue

        # Check if any text was extracted
        if not text.strip():
            raise ValueError("Could not extract any text from the PDF. The file might be scanned or contain only images.")

        return text

    except Exception as e:
        logging.error(f"Error extracting text from PDF: {str(e)}")
        raise ValueError(f"Error processing PDF file: {str(e)}")