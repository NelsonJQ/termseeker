def convert_word_to_markdown(file_path) -> str:
    from docx import Document

    # Read the Word document
    doc = Document(file_path)
    markdown_content = []

    for para in doc.paragraphs:
        markdown_content.append(para.text)

    # Join the content into a single Markdown string
    return '\n\n'.join(markdown_content)