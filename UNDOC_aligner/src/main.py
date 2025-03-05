import argparse
import polars as pl
from convert.pdf_to_markdown import convert_pdf_to_markdown
from un_library.search import access_un_library_by_term_and_symbol, adv_search_un_library
from un_library.extract import extract_metadata_UNLib
from utils.clean_symbols import cleanSymbols
from utils.document_urls import get_un_document_urls
from utils.find_paragraphs import find_paragraphs_with_merge
from utils.bilingual_aligner import find_similar_paragraph_in_target, askLLM_term_equivalents, getEquivalents_from_response

def main(input_search_text, input_lang, input_filterSymbols, sourcesQuantity, paragraphsPerDoc, eraseDrafts):
    UNEP_LANGUAGES = {"English": "en", "French": "fr", "Spanish": "es", "Chinese": "zh", "Russian": "ru", "Arabic": "ar", "Portuguese": "pt", "Swahili": "sw"}

    metadataCleaned = []

    # Standardize languages
    if input_lang == "ALL":
        input_lang = list(UNEP_LANGUAGES.keys())
    if isinstance(input_lang, str) and input_lang in list(UNEP_LANGUAGES.keys()):
        input_lang = [input_lang]

    # Verify that all input languages are in UNEP_Languages
    if isinstance(input_filterSymbols, list):
        html_output = None

        if len(input_filterSymbols) == 1:
            html_output = access_un_library_by_term_and_symbol(
                input_search_text,
                input_filterSymbols[0]
            )
        elif len(input_filterSymbols) > 1:
            html_output = adv_search_un_library(
                document_symbol=input_filterSymbols,
                fulltext_term=input_search_text
            )

        if len(input_filterSymbols) == 0 or html_output is None:
            print("General term search without filters...")
            html_output = access_un_library_by_term_and_symbol(
                input_search_text,
                ""
            )

    if html_output:
        metadata = extract_metadata_UNLib(html_output)  # list
        print(metadata)
        if metadata:
            metadataCleaned = cleanSymbols(metadata, removeDrafts=eraseDrafts, maxResults=sourcesQuantity)
            print(metadataCleaned)

    # Initialize missing keys with None
    if metadataCleaned:
        all_keys = set().union(*(d.keys() for d in metadataCleaned))
        for resultItem in metadataCleaned:
            for key in all_keys:
                resultItem.setdefault(key, None)

    # Get UN Docs URL for each result docSymbol
    for resultItem in metadataCleaned:
        resultItem["EnglishTerm"] = input_search_text
        resultItem["docURLs"] = get_un_document_urls(resultItem["docSymbol"])  # dict

        # Process files
        englishMD = convert_pdf_to_markdown(resultItem["docURLs"]["English"])
        englishParagraphs = find_paragraphs_with_merge(englishMD, input_search_text, max_paragraphs=paragraphsPerDoc)
        if englishParagraphs:
            resultItem["EnglishParagraphs"] = englishParagraphs  # list

            # Other languages
            for targetLang in input_lang:
                langMD = convert_pdf_to_markdown(resultItem["docURLs"][targetLang])
                for engPara in englishParagraphs:
                    targetParagraphs = find_similar_paragraph_in_target(engPara, langMD, model_name='distiluse-base-multilingual-cased-v2', top_k=1)
                if targetParagraphs:
                    tParaColName = targetLang + 'Paragraphs'
                    resultItem[tParaColName] = targetParagraphs  # list

                    # Extract bilingual terms as LLM string answer
                    targetTerms = askLLM_term_equivalents(input_search_text, englishParagraphs, targetParagraphs, "English", targetLang)
                    print(targetTerms)

                    targetTerms = getEquivalents_from_response(targetTerms)  # list of str
                    if targetTerms:
                        # Unique values of list
                        targetTerms = list(set(targetTerms))

                        # Save the targetTerm in metadata w/ its related
                        targetTermColName = targetLang + 'Term'
                        targetSynonymsColName = targetLang + 'Synonyms'
                        resultItem[targetTermColName] = targetTerms[0]
                        resultItem[targetSynonymsColName] = targetTerms[1:]

    # Create Polars dataframe
    if metadataCleaned:
        df = pl.DataFrame(metadataCleaned)
        print(df)

    return metadataCleaned

if __name__ == "__main__":
    from termun.cli import main_cli
    main_cli()