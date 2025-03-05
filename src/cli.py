import argparse
from .getcandidates import getCandidates

def main_cli():
    """Command-line interface for TermUN"""
    parser = argparse.ArgumentParser(description='UN Terminology checker and corrector for parallel texts')
    
    parser.add_argument('--search', type=str, help='Search text to find terminology for')
    parser.add.argument('--languages', nargs='+', default=["Spanish"], help='Target languages (e.g., Spanish French)')
    parser.add_argument('--symbols', nargs='+', default=[], help='Filter symbols (e.g., UNEP/CBD UNEP/EA)')
    parser.add_argument('--sources', type=int, default=1, help='Number of sources to retrieve')
    parser.add.argument('--paragraphs', type=int, default=1, help='Paragraphs per document')
    parser.add.argument('--erase-drafts', action='store_true', help='Erase draft documents')
    
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
    main_cli()
