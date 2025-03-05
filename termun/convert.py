"""
Convert module for transforming documents to different formats
"""

import os
import tempfile
import requests
import pymupdf4llm
from pathlib import Path

def convert_pdf_to_markdown(url_or_path):
    """
    Convert a PDF document to Markdown format.
    
    Parameters:
    -----------
    url_or_path : str
        URL or file path to the PDF document
    output_format : str, optional
        Output format (default is "markdown")
        
    Returns:
    --------
    str
        The document content in Markdown format
    """
    try:
        # Determine if input is URL or local file
        is_url = url_or_path.startswith(('http://', 'https://'))
        
        # Create temporary file if input is URL
        if is_url:
            # Download the file
            response = requests.get(url_or_path, stream=True)
            if response:
                print("\t\tconvert.py -> got response")
            response.raise_for_status()
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
                temp_path = temp_file.name
                for chunk in response.iter_content(chunk_size=8192):
                    temp_file.write(chunk)
            file_path = temp_path
        else:
            file_path = url_or_path
        
        # Use pymupdf4llm (assumed to be installed) to convert PDF to markdown
        try:
            print("\t\tconvert.py -> using pymupdf4llm")
            markdown_content = pymupdf4llm.to_markdown(file_path)
            if markdown_content:
                print("\t\tconvert.py -> got markdown content")
        except ImportError:
            # Fallback if pymupdf4llm is not available
            print("\t\tconvert.py -> fallback to fitz")
            import fitz  # PyMuPDF
            doc = fitz.open(file_path)
            markdown_content = ""
            for page in doc:
                markdown_content += page.get_text("markdown") + "\n\n"
            doc.close()
        
        # Clean up temporary file if created
        if is_url and os.path.exists(file_path):
            os.unlink(file_path)
            
        return markdown_content
    
    except Exception as e:
        print(f"Error converting PDF to Markdown: {e}")
        return ""

def convert_docx_to_markdown(url_or_path):
    """
    Convert a DOCX document to Markdown format.
    
    Parameters:
    -----------
    url_or_path : str
        URL or file path to the DOCX document
        
    Returns:
    --------
    str
        The document content in Markdown format
    """
    try:
        # Determine if input is URL or local file
        is_url = url_or_path.startswith(('http://', 'https://'))
        
        # Create temporary file if input is URL
        if is_url:
            # Download the file
            response = requests.get(url_or_path, stream=True)
            response.raise_for_status()
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as temp_file:
                temp_path = temp_file.name
                for chunk in response.iter_content(chunk_size=8192):
                    temp_file.write(chunk)
            file_path = temp_path
        else:
            file_path = url_or_path
        
        # Convert DOCX to markdown using python-docx
        from docx import Document
        doc = Document(file_path)
        
        markdown = []
        for para in doc.paragraphs:
            markdown.append(para.text)
        
        # Clean up temporary file if created
        if is_url and os.path.exists(file_path):
            os.unlink(file_path)
            
        return "\n\n".join(markdown)
    
    except Exception as e:
        print(f"Error converting DOCX to Markdown: {e}")
        return ""
