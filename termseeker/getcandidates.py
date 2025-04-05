import os
import re
import polars as pl
from .convert import convert_pdf_to_markdown
from .searchlibrary import access_un_library_by_term_and_symbol, adv_search_un_library, extract_metadata_UNLib
from .utils import cleanSymbols, get_un_document_urls, find_paragraphs_with_merge, \
                        find_similar_paragraph_in_target, askLLM_term_equivalents, getEquivalents_from_response, consolidate_results
from .askTermBases import queryUNTerm, consolidate_UNTermResults, report_missing_translations

from lingua import Language, LanguageDetectorBuilder

# Initialize language detector with all UN languages
LANGUAGE_MAP = {
    Language.ENGLISH: "en",
    Language.FRENCH: "fr", 
    Language.SPANISH: "es", 
    Language.CHINESE: "zh", 
    Language.RUSSIAN: "ru", 
    Language.ARABIC: "ar", 
    Language.PORTUGUESE: "pt",
    Language.SWAHILI: "sw"
}

# Create a detector instance
detector = LanguageDetectorBuilder.from_languages(*LANGUAGE_MAP.keys()).build()

def detect_language(text):
    """
    Detects the language of the given text using lingua language detector.
    
    Args:
        text (str): Text to detect language of
        
    Returns:
        str: ISO 639-1 language code (lowercase)
    """
    try:
        # Ensure text is not too short for accurate detection
        if not text or len(text.strip()) < 20:
            return "unknown"
            
        # Detect language
        detected_language = detector.detect_language_of(text)
        
        # Return the ISO code if detected, otherwise "unknown"
        if detected_language:
            return LANGUAGE_MAP.get(detected_language, "unknown")
        return "unknown"
    except Exception as e:
        print(f"Language detection failed: {e}")
        return "unknown"

def sanitize_filename(filename):
    # Replace any character that is not alphanumeric, underscore, or hyphen with an underscore
    sanitized = re.sub(r'[^\w\-_\.]', '_', filename)
    return sanitized


def getCandidates(input_search_text, input_lang, input_filterSymbols, sourcesQuantity, paragraphsPerDoc, eraseDrafts, localLM=False, groqToken=None):
    UNEP_LANGUAGES = {"English": "en", "French": "fr", "Spanish": "es", "Chinese": "zh", "Russian": "ru", "Arabic": "ar", "Portuguese": "pt", "Swahili": "sw"}
    # Reverse mapping for language code to name
    LANG_CODES_TO_NAME = {v: k for k, v in UNEP_LANGUAGES.items()}

    # Initialize a variable to track if we need more documents
    need_more_docs = True
    max_docs_to_fetch = max(10, sourcesQuantity * 3)  # Fetch more documents than requested initially
    max_docs_to_fetch = min(50, max_docs_to_fetch)  # Limit to 50 documents initially
    processed_docs = 0
    
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

    # Initialize a list to collect all metadata
    all_metadata = []
    
    # First, fetch all potential metadata from the UN Library search
    if html_output:
        # Extract all metadata without limiting initially
        all_metadata = extract_metadata_UNLib(html_output)
        print(f"Found {len(all_metadata)} potential documents")

    # Only clean the symbols, but don't limit yet (set a high maxResults)
    if all_metadata:
        metadataCleaned = cleanSymbols(all_metadata, removeDrafts=eraseDrafts, maxResults=max_docs_to_fetch)
        print(f"After cleaning, {len(metadataCleaned)} documents remain for processing")
    else:
        metadataCleaned = []

    # Initialize missing keys with None
    if metadataCleaned:
        all_keys = set().union(*(d.keys() for d in metadataCleaned))
        for resultItem in metadataCleaned:
            for key in all_keys:
                resultItem.setdefault(key, None)

    # Initialize a dictionary to track paragraphs found for each language
    lang_paragraphs = {lang: [] for lang in input_lang if lang != "English"}
    
    # Initialize a dictionary to store English paragraphs for each document
    doc_english_paragraphs = {}
    
    # Initialize a list to store processed results
    processed_results = []
    
    # Process each document until we have enough paragraphs for all languages
    # or until we've processed the specified number of documents
    for i, resultItem in enumerate(metadataCleaned):
        # Check if we've processed enough documents and have paragraphs for all languages
        if processed_docs >= sourcesQuantity:
            all_languages_have_paragraphs = all(len(paras) >= paragraphsPerDoc for lang, paras in lang_paragraphs.items())
            if all_languages_have_paragraphs:
                print(f"Processed {processed_docs} documents and found at least {paragraphsPerDoc} paragraphs for all languages")
                break
                
        # Track that we're processing this document
        processed_docs += 1
        print(f"Processing document {processed_docs}/{len(metadataCleaned)}: {resultItem.get('docSymbol', 'Unknown')}")
        
        resultItem["EnglishTerm"] = input_search_text
        resultItem["docURLs"] = get_un_document_urls(resultItem["docSymbol"])  # dict

        # Process files
        print(f"Processing files for {resultItem['docURLs']['English']}...")
        englishMD = convert_pdf_to_markdown(resultItem["docURLs"]["English"])
        print("Finding paragraphs...")
        # Get all matching paragraphs
        all_english_paragraphs = find_paragraphs_with_merge(englishMD, input_search_text, max_paragraphs=None)
        
        if not all_english_paragraphs:
            print(f"No English paragraphs found in document {resultItem['docSymbol']}, skipping...")
            continue
        
        # Store all English paragraphs for this document
        doc_english_paragraphs[resultItem['docSymbol']] = all_english_paragraphs
        
        # Only use the specified number for initial processing
        englishParagraphs = all_english_paragraphs[:paragraphsPerDoc]
        resultItem["EnglishParagraphs"] = englishParagraphs  # list
        
        # Only add to processed results if we found English paragraphs
        found_target_paragraphs = False
        
        # Get the list of languages that still need paragraphs
        languages_to_process = [lang for lang in input_lang if lang != "English" and len(lang_paragraphs[lang]) < paragraphsPerDoc]
        
        # If we already have paragraphs for all languages, we can stop
        if not languages_to_process:
            print("Already found enough paragraphs for all languages")
            break
            
        print(f"Need to find paragraphs for: {', '.join(languages_to_process)}")

        # For each language that still needs more paragraphs
        for targetLang in languages_to_process:
            print(f"Processing language: {targetLang}")
            target_lang_code = UNEP_LANGUAGES.get(targetLang, "")
            
            try:
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

                # Try to find matching paragraphs for each English paragraph
                processed_eng_paragraphs = []
                new_target_paragraphs = []
                
                for engPara in englishParagraphs:
                    if len(new_target_paragraphs) >= paragraphsPerDoc:
                        break
                        
                    processed_eng_paragraphs.append(engPara)
                    # Get top 3 similar paragraphs to have alternatives
                    similar_paragraphs = find_similar_paragraph_in_target(engPara, langMD, 
                                                                        model_name='distiluse-base-multilingual-cased-v2', 
                                                                        top_k=2)
                    
                    if similar_paragraphs:
                        found_target_lang_para = False
                        
                        for para in similar_paragraphs:
                            detected_lang = detect_language(para[0])
                            # Check if paragraph is in the target language
                            if detected_lang == target_lang_code:
                                new_target_paragraphs.append(para[0])
                                found_target_lang_para = True
                                break
                                
                            
                
                # If we don't have enough target paragraphs, try with additional English paragraphs
                if len(new_target_paragraphs) < paragraphsPerDoc and len(all_english_paragraphs) > len(processed_eng_paragraphs):
                    remaining_eng_paragraphs = [p for p in all_english_paragraphs if p not in processed_eng_paragraphs]
                    
                    for engPara in remaining_eng_paragraphs:
                        if len(new_target_paragraphs) >= paragraphsPerDoc:
                            break
                            
                        similar_paragraphs = find_similar_paragraph_in_target(engPara, langMD, 
                                                                            model_name='distiluse-base-multilingual-cased-v2', 
                                                                            top_k=2)
                        
                        if similar_paragraphs:
                            for para in similar_paragraphs:
                                detected_lang = detect_language(para[0])
                                if detected_lang == target_lang_code:
                                    new_target_paragraphs.append(para[0])
                                    break
                            
                            if len(new_target_paragraphs) >= paragraphsPerDoc:
                                break
                
                # Add the new target paragraphs to our collection for this language
                if new_target_paragraphs:
                    found_target_paragraphs = True
                    lang_paragraphs[targetLang].extend(new_target_paragraphs)
                    print(f"Found {len(new_target_paragraphs)} new paragraphs for {targetLang}, total now: {len(lang_paragraphs[targetLang])}")
                    
                    # Store target paragraphs in resultItem
                    tParaColName = targetLang + 'Paragraphs'
                    resultItem[tParaColName] = new_target_paragraphs
                    
                    # Initialize targetTerm and targetSynonyms if we found paragraphs
                    targetTermColName = targetLang + 'Term'
                    targetSynonymsColName = targetLang + 'Synonyms'
                    resultItem[targetTermColName] = None
                    resultItem[targetSynonymsColName] = None
                    
                    # Extract bilingual terms as LLM string answer
                    englishParasToUse = englishParagraphs[:len(new_target_paragraphs)]

                    if localLM == None:
                        targetTerms = []
                    
                    elif localLM == False or localLM==True:
                        # Use only as many English paragraphs as we have target paragraphs
                        
                        targetTerms = askLLM_term_equivalents(input_search_text, englishParasToUse,
                                                              new_target_paragraphs, "English",
                                                              targetLang,
                                                              customInference=localLM, groqToken=groqToken)
                        print(targetTerms)

                        if "Error" in targetTerms:
                            print(f"Error in LLM response: {targetTerms['Error']}")
                            targetTerms = []
                        elif targetTerms:
                            targetTerms = getEquivalents_from_response(targetTerms)  # list of str
                        
                            # Unique values of list
                            targetTerms = list(set(targetTerms))

                            # Save the targetTerm in metadata w/ its related
                            resultItem[targetTermColName] = targetTerms[0]
                            resultItem[targetSynonymsColName] = targetTerms[1:]
                else:
                    print(f"No target paragraphs found for {targetLang} in document {resultItem['docSymbol']}")
            
            except Exception as e:
                print(f"Error processing {targetLang} document for {resultItem['docSymbol']}: {e}")
        
        # If we found any target paragraphs in this document, add it to our results
        if found_target_paragraphs:
            processed_results.append(resultItem)
            
            # If we have enough results and found at least the required number of paragraphs for each language
            if len(processed_results) >= sourcesQuantity:
                all_languages_have_paragraphs = all(len(paras) >= paragraphsPerDoc for lang, paras in lang_paragraphs.items())
                if all_languages_have_paragraphs:
                    print(f"Found at least {paragraphsPerDoc} paragraphs for all languages after processing {processed_docs} documents")
                    break
    
    # Log the language paragraph counts
    print("\n--- Language paragraph counts ---")
    for lang, paras in lang_paragraphs.items():
        print(f"{lang}: {len(paras)} paragraphs")
    
    # Return the processed results, or an empty list if none
    if processed_results:
        # Check if we have the required number of paragraphs for each language
        all_languages_have_enough_paragraphs = all(len(paras) >= paragraphsPerDoc for lang, paras in lang_paragraphs.items())
        if not all_languages_have_enough_paragraphs:
            print(f"Warning: Not all languages have {paragraphsPerDoc} or more paragraphs.")
            # You can uncomment the following line to strictly enforce the paragraph requirement
            # return []
            
        # Create Polars dataframe with the successfully processed results
        try:
            df = pl.DataFrame(processed_results, strict=False)
            print(df)
        except Exception as e:
            print(f"Error creating Polars dataframe: {e}")
    
    return processed_results if processed_results else []

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