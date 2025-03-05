import argparse
import polars as pl
from .convert import convert_pdf_to_markdown
from .searchlibrary import access_un_library_by_term_and_symbol, adv_search_un_library, extract_metadata_UNLib
from .utils import cleanSymbols, get_un_document_urls, find_paragraphs_with_merge, \
                        find_similar_paragraph_in_target, askLLM_term_equivalents, getEquivalents_from_response
from .getcandidates import getCandidates

def getterms():
    parser = argparse.ArgumentParser(description='UN Terminology checker and corrector for parallel texts')
    
    parser.add_argument('--search', type=str, help='Search text to find terminology for')
    parser.add_argument('--languages', nargs='+', default=["Spanish"], help='Target languages (e.g., Spanish French)')
    parser.add_argument('--symbols', nargs='+', default=[], help='Filter symbols (e.g., UNEP/CBD UNEP/EA)')
    parser.add_argument('--sources', type=int, default=1, help='Number of sources to retrieve')
    parser.add_argument('--paragraphs', type=int, default=1, help='Paragraphs per document')
    parser.add_argument('--erase-drafts', action='store_true', help='Erase draft documents')
    
    args = parser.parse_args()
    
    if args.search:
        results = getCandidates(
            args.search, 
            args.languages, 
            args.symbols, 
            args.sources, 
            args.paragraphs, 
            args.erase_drafts
        )
        print(results)
    else:
        parser.print_help()

if __name__ == "__main__":
    getterms()