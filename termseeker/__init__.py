"""
TermSeeker: A tool for assisting terminology tasks by searching the UN official documents.

This package provides functionality for:
- Accessing the UN Digital Library for document retrieval and metadata extraction
- Finding and aligning paragraphs across different language versions
- Extracting bilingual terminology using language models
- Querying the UN Terminology Database for existing translations
"""

__version__ = '0.1.0'

# Make sure these files exist at these paths
from .getcandidates import getCandidates, getTermsAndCandidates
from .convert import convert_pdf_to_markdown
from .searchlibrary import access_un_library_by_term_and_symbol, adv_search_un_library, extract_metadata_UNLib
from .utils import find_similar_paragraph_in_target, askLLM_term_equivalents, consolidate_results
from .askTermBases import queryUNTerm, consolidate_UNTermResults, report_missing_translations
from .queryHFdatasets import query_dataset_by_term_and_symbol, HUGGINGFACE_TOKEN

# Define what gets imported with "from termseeker import *"
__all__ = [
    'getCandidates',
    'convert_pdf_to_markdown',
    'access_un_library_by_term_and_symbol',
    'adv_search_un_library', 
    'extract_metadata_UNLib',
    'find_similar_paragraph_in_target',
    'askLLM_term_equivalents',
    'consolidate_results',
    'queryUNTerm',
    'consolidate_UNTermResults',
    'report_missing_translations',
    'getTermsAndCandidates',
    'query_dataset_by_term_and_symbol'
]
