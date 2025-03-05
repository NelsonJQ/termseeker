import argparse
from termun.UNDOC_aligner.src.main import main

def main_cli():
    parser = argparse.ArgumentParser(description="Run the UNDOC aligner script with custom arguments.")
    parser.add_argument("--input_search_text", type=str, required=True, help="The search text to look for in the full text.")
    parser.add_argument("--input_lang", type=str, nargs='+', required=True, help="The languages to search in.")
    parser.add_argument("--input_filterSymbols", type=str, nargs='+', required=True, help="The document symbols to filter the search results.")
    parser.add_argument("--sourcesQuantity", type=int, required=True, help="The number of sources to retrieve.")
    parser.add_argument("--paragraphsPerDoc", type=int, required=True, help="The number of paragraphs to retrieve per document.")
    parser.add_argument("--eraseDrafts", type=bool, required=True, help="Whether to erase drafts from the results.")

    args = parser.parse_args()

    result = main(args.input_search_text, args.input_lang, args.input_filterSymbols, args.sourcesQuantity, args.paragraphsPerDoc, args.eraseDrafts)
    print(result)

if __name__ == "__main__":
    main_cli()
