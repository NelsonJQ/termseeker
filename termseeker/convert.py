"""
Convert module for transforming documents to different formats
"""

import os
import tempfile
import requests
import pymupdf4llm
from pathlib import Path

def convert_pdf_to_markdown(url_or_path, cache_dir=None, file_name=None):
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
        
        # Create cache filename if caching is enabled
        cache_path = None
        if cache_dir and is_url:
            import hashlib
            # Create a hash of the URL to use as filename
            url_hash = hashlib.md5(url_or_path.encode()).hexdigest()
            cache_path = os.path.join(cache_dir, f"{url_hash}.md")
            print(cache_path)
            # Check if cached version exists
            if os.path.exists(cache_path):
                print(f"\t\tconvert.py -> using cached version from {cache_path}")
                with open(cache_path, 'r', encoding='utf-8') as f:
                    return f.read()
                
            elif file_name:
                # Use provided file_name for caching
                cache_path = os.path.join(cache_dir, f"{file_name}")
                if os.path.exists(cache_path):
                    print(f"\t\tconvert.py -> using cached version from {cache_path}")
                    with open(cache_path, 'r', encoding='utf-8') as f:
                        return f.read()
                
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
        
        # After successful conversion, save to cache if enabled
        if cache_path and markdown_content:
            os.makedirs(os.path.dirname(cache_path), exist_ok=True)
            with open(cache_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            print(f"\t\tconvert.py -> saved to cache: {cache_path}")

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
        
    # Create cache filename if caching is enabled
        cache_path = None
        if cache_dir and is_url:
            import hashlib
            # Create a hash of the URL to use as filename
            url_hash = hashlib.md5(url_or_path.encode()).hexdigest()
            cache_path = os.path.join(cache_dir, f"{url_hash}.md")
            
            # Check if cached version exists
            if os.path.exists(cache_path):
                print(f"\t\tconvert.py -> using cached version from {cache_path}")
                with open(cache_path, 'r', encoding='utf-8') as f:
                    return f.read()

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
