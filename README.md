# Project Overview

 TermHunter is a Python application designed to facilitate the terminology work by searching for candidate terms in UN languages in official UN documents. The application uses the UN Digital Library search results in one or multiple languages (Arabic, Spanish, French, Russian, Chinese).

## Features

- Convert Word documents to Markdown format.
- Convert PDF documents (from local files or URLs) to Markdown format.
- Search the UN Digital Library by term and document symbol.
- Extract document symbols and metadata from search results.
- Generate downloadable PDF URLs for UN documents in all official languages.

## Google Colab

You can test the installation and execution of the `termun` library using Google Colab. Click the link below to open the notebook:

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/NelsonJQ/termun/blob/main/playground_termHunter.ipynb)

## Installation

To set up the project, clone the repository and install the required dependencies:

```bash
git clone <repository-url>
cd UNDOC_aligner
pip install -r requirements.txt
```

## Usage

### Using getCandidates()

The `getCandidates()` function is the core function of this application. It searches for documents in the UN Digital Library based on the provided search text, languages, and filter symbols. It then processes the documents to extract relevant paragraphs and terms.

#### Function Signature

```python
def getCandidates(input_search_text, input_lang, input_filterSymbols, sourcesQuantity, paragraphsPerDoc, eraseDrafts):
```

#### Parameters

- `input_search_text` (str): The search text to find terminology for.
- `input_lang` (list or str): Target languages (e.g., ["Spanish", "French"]). Use "ALL" for all supported languages.
- `input_filterSymbols` (list): Filter symbols (e.g., ["UNEP/CBD", "UNEP/EA"]).
- `sourcesQuantity` (int): Number of sources to retrieve.
- `paragraphsPerDoc` (int): Paragraphs per document.
- `eraseDrafts` (bool): Whether to erase draft documents.

#### Example Usage

```python
from termun.getcandidates import getCandidates

results = getCandidates(
    input_search_text="climate change",
    input_lang=["Spanish", "French"],
    input_filterSymbols=["UNEP/CBD"],
    sourcesQuantity=3,
    paragraphsPerDoc=2,
    eraseDrafts=True
)
print(results)
```

### Using consolidate_results()

The `consolidate_results()` function from `utils.py` consolidates the results obtained from `getCandidates()` into a compact dataframe and optionally exports it as an Excel file.

#### Function Signature

```python
def consolidate_results(metadataCleaned, exportExcel=False) -> list:
```

#### Parameters

- `metadataCleaned` (list): List of dictionaries containing the cleaned metadata.
- `exportExcel` (bool): Whether to export the consolidated results as an Excel file.

#### Example Usage

```python
from termun.utils import consolidate_results

# Assuming `results` is the output from getCandidates()
consolidated_results = consolidate_results(results, exportExcel=True)
print(consolidated_results)
```


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