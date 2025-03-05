"""
TermUN: UN Terminology checker and corrector for parallel texts

This package provides functionality for:
- Converting documents to Markdown format
- Accessing the UN Digital Library for document retrieval and metadata extraction
- Finding and aligning paragraphs across different language versions
- Extracting bilingual terminology using language models
- Cleaning and standardizing UN document symbols
"""

__version__ = '0.1.0'

# Make sure these files exist at these paths
from .getcandidates import getCandidates
from .convert import convert_pdf_to_markdown
from .searchlibrary import access_un_library_by_term_and_symbol, adv_search_un_library, extract_metadata_UNLib
from .utils import find_similar_paragraph_in_target, askLLM_term_equivalents

# Define what gets imported with "from termun.src import *"
__all__ = [
    'getCandidates',
    'convert_pdf_to_markdown',
    'access_un_library_by_term_and_symbol',
    'adv_search_un_library', 
    'extract_metadata_UNLib',
    'find_similar_paragraph_in_target',
    'askLLM_term_equivalents'
]
