def convert_pdf_to_markdown(source) -> str:
    """
    Convert a PDF to markdown text, supporting both local files and URLs

    Args:
        source: Local file path or URL to a PDF document

    Returns:
        Markdown content as a string
    """
    import pymupdf4llm
    import requests
    import tempfile
    import os

    # Check if the source is a URL
    if source.startswith('http://') or source.startswith('https://'):
        try:
            # Download the PDF from the URL
            response = requests.get(source, stream=True)

            # Check if the response is a PDF
            if response.headers.get('content-type') != 'application/pdf':
                raise ValueError(f"The URL did not return a PDF document: {source}")

            # Create a temporary file
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
                temp_path = temp_file.name
                # Write the PDF content to the temporary file
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        temp_file.write(chunk)

            # Process the temporary file
            try:
                markdown_content = pymupdf4llm.to_markdown(temp_path)
                return markdown_content
            finally:
                # Clean up the temporary file
                if os.path.exists(temp_path):
                    os.remove(temp_path)

        except Exception as e:
            raise Exception(f"Failed to process PDF from URL: {str(e)}")

    else:
        # Process a local file
        return pymupdf4llm.to_markdown(source)