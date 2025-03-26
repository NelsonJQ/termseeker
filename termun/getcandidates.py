import os
import re
import polars as pl
from .convert import convert_pdf_to_markdown
from .searchlibrary import access_un_library_by_term_and_symbol, adv_search_un_library, extract_metadata_UNLib
from .utils import cleanSymbols, get_un_document_urls, find_paragraphs_with_merge, \
                        find_similar_paragraph_in_target, askLLM_term_equivalents, getEquivalents_from_response, consolidate_results
from .askTermBases import queryUNTerm, consolidate_UNTermResults, report_missing_translations

def sanitize_filename(filename):
    # Replace any character that is not alphanumeric, underscore, or hyphen with an underscore
    sanitized = re.sub(r'[^\w\-_\.]', '_', filename)
    return sanitized


def getCandidates(input_search_text, input_lang, input_filterSymbols, sourcesQuantity, paragraphsPerDoc, eraseDrafts, localLM=False):
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
        print(f"Processing files for {resultItem['docURLs']['English']}...")
        englishMD = convert_pdf_to_markdown(resultItem["docURLs"]["English"])
        print("Finding paragraphs...")
        englishParagraphs = find_paragraphs_with_merge(englishMD, input_search_text, max_paragraphs=paragraphsPerDoc)
        if englishParagraphs:
            resultItem["EnglishParagraphs"] = englishParagraphs  # list
            print("\n\nEnglish Paragraphs:")
            print(resultItem)

            # Other languages
            for targetLang in input_lang:
                print(f"Processing language: {targetLang}")
                langMD = convert_pdf_to_markdown(resultItem["docURLs"][targetLang])
                
                # Ensure the directory exists before saving the file
                output_dir = "/content"
                os.makedirs(output_dir, exist_ok=True)
                
                # Sanitize the docSymbol for use in the file name
                sanitized_docSymbol = sanitize_filename(resultItem['docSymbol'])
                
                # Save langMD in text file
                output_file_path = os.path.join(output_dir, f"{sanitized_docSymbol}_{targetLang}.txt")
                with open(output_file_path, "w") as f:
                    f.write(langMD)

                targetParagraphs = []
                for engPara in englishParagraphs:
                    partialParagraphs = find_similar_paragraph_in_target(engPara, langMD, model_name='distiluse-base-multilingual-cased-v2', top_k=1)
                    if partialParagraphs:
                        targetParagraphs.extend(partialParagraphs)

                if targetParagraphs:
                    print(f"Found target paragraphs: {targetParagraphs}")
                    tParaColName = targetLang + 'Paragraphs'
                    resultItem[tParaColName] = targetParagraphs  # list


                    # Initialize targetTerm and targetSynonyms
                    targetTermColName = targetLang + 'Term'
                    targetSynonymsColName = targetLang + 'Synonyms'
                    resultItem[targetTermColName] = None
                    resultItem[targetSynonymsColName] = None

                    # Extract bilingual terms as LLM string answer
                    if localLM == None:
                        targetTerms = []
                    
                    elif localLM == False or localLM==True:
                        targetTerms = askLLM_term_equivalents(input_search_text, englishParagraphs, targetParagraphs, "English", targetLang, customInference=localLM)
                        print(targetTerms)

                        targetTerms = getEquivalents_from_response(targetTerms)  # list of str
                        if targetTerms:
                            # Unique values of list
                            targetTerms = list(set(targetTerms))

                            # Save the targetTerm in metadata w/ its related
                            resultItem[targetTermColName] = targetTerms[0]
                            resultItem[targetSynonymsColName] = targetTerms[1:]

    # Create Polars dataframe
    if metadataCleaned:
        try:
            df = pl.DataFrame(metadataCleaned, strict=False)
            print(df)
        except Exception as e:
            print(f"Error creating Polars dataframe: {e}")
            # Continue execution even if there's an error

    return metadataCleaned

def getTermsAndCandidates(input_search_text, lang_to_search="ALL", input_filterSymbols=["UNEP", "FCCC", "S"], 
                          sourcesQuantity=3, paragraphsPerDoc=2, eraseDrafts=True):
    """
    Performs a comprehensive terminology search combining UNTERM database and UN document analysis.
    First queries UNTERM database, then checks for missing preferred translations and fills gaps by
    analyzing UN Library documents to extract terminology candidates.
    
    Args:
        input_search_text (str): The term to search for
        lang_to_search (str or list): Target language(s) to search for
        input_filterSymbols (list): Document symbols to filter the search by
        sourcesQuantity (int): Maximum number of source documents to process
        paragraphsPerDoc (int): Maximum paragraphs to extract per document
        eraseDrafts (bool): Whether to remove draft documents from results
    
    Returns:
        dict: Combined terminology data from UNTERM and document extraction
    """
    # Step 1: Query the UN Terminology Database
    unterm_results = queryUNTerm(input_search_text)
    
    # Step 2: Consolidate UNTERM results
    consolidated_unterm = consolidate_UNTermResults(unterm_results, input_search_text)
    
    # Step 3: Identify missing translations
    missing_translations = report_missing_translations(consolidated_unterm)
    missing_preferred = missing_translations.get('missingPreferred', [])
    
    # Check if there are missing preferred translations
    if not missing_preferred or all(not lang for lang in missing_preferred):
        return consolidated_unterm
    
    # Determine which languages to search for in documents
    languages_to_extract = []
    if lang_to_search == "ALL":
        # When ALL is specified, search for all missing languages
        languages_to_extract = missing_preferred
    else:
        # When specific languages are requested, only search for those that are also missing
        if isinstance(lang_to_search, list):
            languages_to_extract = [lang for lang in lang_to_search if lang in missing_preferred]
    
    # If no languages to search for after filtering, return UNTERM results
    if not languages_to_extract:
        return consolidated_unterm
    
    # Step 4: Extract terminology candidates from UN Library documents
    candidates_results = getCandidates(
        input_search_text=input_search_text,
        input_lang=languages_to_extract,
        input_filterSymbols=input_filterSymbols,
        sourcesQuantity=sourcesQuantity,
        paragraphsPerDoc=paragraphsPerDoc,
        eraseDrafts=eraseDrafts
    )
    
    # Step 5: Consolidate library results
    consolidated_library = consolidate_results(candidates_results, exportExcel=False)
    
    # Step 6: Combine both results preserving order
    combined_results = consolidated_unterm.copy()
    combined_results["UNLibrary"] = True
    
    # Add library results if available
    if consolidated_library and len(consolidated_library) > 0:
        library_dict = consolidated_library[0]  # First item from the consolidated list
        for key, value in library_dict.items():
            if key not in combined_results:
                combined_results[key] = value
    
    return combined_results