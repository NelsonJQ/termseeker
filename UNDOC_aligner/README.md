# Project Overview

The UNDOC Aligner is a Python application designed to facilitate the conversion of documents from various formats (Word and PDF) into Markdown format. It also provides functionalities to access the UN Digital Library, extract relevant document symbols and metadata, and generate downloadable URLs for UN documents in multiple languages.

## Features

- Convert Word documents to Markdown format.
- Convert PDF documents (from local files or URLs) to Markdown format.
- Search the UN Digital Library by term and document symbol.
- Extract document symbols and metadata from search results.
- Generate downloadable PDF URLs for UN documents in all official languages.

## Installation

To set up the project, clone the repository and install the required dependencies:

```bash
git clone <repository-url>
cd UNDOC_aligner
pip install -r requirements.txt
```

## Usage

### Converting Documents

To convert a Word document to Markdown:

```python
from src.convert.word_to_markdown import convert_word_to_markdown

markdown_content = convert_word_to_markdown('path/to/document.docx')
print(markdown_content)
```

To convert a PDF document to Markdown:

```python
from src.convert.pdf_to_markdown import convert_pdf_to_markdown

markdown_content = convert_pdf_to_markdown('path/to/document.pdf')
print(markdown_content)
```

### Accessing the UN Digital Library

To search for documents in the UN Digital Library:

```python
from src.un_library.search import access_un_library_by_term_and_symbol

html_content = access_un_library_by_term_and_symbol('search term', 'document symbol')
print(html_content)
```

### Extracting Document Symbols and Metadata

To extract document symbols from HTML content:

```python
from src.un_library.extract import extract_document_symbols

symbols = extract_document_symbols(html_content)
print(symbols)
```

To extract metadata from HTML content:

```python
from src.un_library.extract import extract_metadata_UNLib

metadata = extract_metadata_UNLib(html_content)
print(metadata)
```

### Generating Document URLs

To get downloadable URLs for a UN document:

```python
from src.utils.document_urls import get_un_document_urls

urls = get_un_document_urls('UNEP/EA.5/HLS.1')
print(urls)
```

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any enhancements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.