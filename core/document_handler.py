"""Document extraction utility for handling multiple file formats."""

import io
from docx import Document as DocxDocument
from PyPDF2 import PdfReader


def extract_text_from_docx(file_content):
    """Extract text from .docx (Word) files."""
    try:
        doc = DocxDocument(io.BytesIO(file_content))
        text = '\n'.join([para.text for para in doc.paragraphs])
        return text
    except Exception as e:
        raise ValueError(f"Error reading .docx file: {str(e)}")


def extract_text_from_pdf(file_content):
    """Extract text from .pdf files."""
    try:
        pdf_reader = PdfReader(io.BytesIO(file_content))
        text = ''
        for page in pdf_reader.pages:
            text += page.extract_text() + '\n'
        return text
    except Exception as e:
        raise ValueError(f"Error reading PDF file: {str(e)}")


def extract_text_from_txt(file_content):
    """Extract text from plain text files."""
    try:
        return file_content.decode('utf-8', errors='ignore')
    except Exception as e:
        raise ValueError(f"Error reading text file: {str(e)}")


def extract_text_from_file(uploaded_file):
    """
    Extract text from uploaded file based on file type.

    Supports: .txt, .docx, .pdf

    Args:
        uploaded_file: Django UploadedFile object

    Returns:
        str: Extracted text content

    Raises:
        ValueError: If file type is unsupported or extraction fails
    """
    filename = uploaded_file.name.lower()
    file_content = uploaded_file.read()

    if filename.endswith('.docx'):
        return extract_text_from_docx(file_content)
    elif filename.endswith('.pdf'):
        return extract_text_from_pdf(file_content)
    elif filename.endswith(('.txt', '.text')):
        return extract_text_from_txt(file_content)
    else:
        # Try as plain text by default
        try:
            return extract_text_from_txt(file_content)
        except:
            raise ValueError(
                f"Unsupported file type: {filename}. "
                "Supported formats: .txt, .docx, .pdf"
            )
