"""
Utility functions for TermSeeker

This module provides various utility functions including:
- Document symbol cleaning and filtering
- UN Document URL generation
- Paragraph extraction and processing
- Bilingual text alignment and terminology extraction
"""

import re
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from duckduckgo_search import DDGS
import polars as pl
import os

# Global variable to store the model
model = None

# =============================================
# Document Symbol Cleaning Functions
# =============================================

def cleanSymbols(input_dict, removeDrafts=False, maxResults=3) -> list:
    """
    Cleans the docSymbol strings in the input dictionary by removing whitespace within parentheses,
    keeping the last part if there is a ' - ', and optionally removing items with
    docType containing "draft". Processing stops when maxResults valid items have been added.

    Args:
        input_dict (list of dict): A list of dictionaries containing metadata with docSymbol strings.
        removeDrafts (bool): Whether to remove items with docType containing "draft".
        maxResults (int): Maximum number of cleaned items to return.

    Returns:
        list of dict: A list of dictionaries with cleaned docSymbol strings (up to maxResults items).
    """
    cleaned_dict = []
    modified_count = 0
    spaces_count = 0
    hyphen_count = 0
    removed_count = 0
    englishonly_count = 0

    if int(maxResults) > 50:
        maxResults = 50

    for item in input_dict:
        # If removeDrafts is True, skip items with 'draft' in docType
        if removeDrafts and 'draft' in item['docType'].lower():
            removed_count += 1
            continue

        if removeDrafts and ('draft' in item['docTitle'].lower() or 'letter' in item['docTitle'].lower()):
            removed_count += 1
            continue

        if item['isMultiple'] == False or item['isMultiple'] == None:
            englishonly_count += 1
            continue

        original_doc_symbol = item['docSymbol']
        doc_symbol = original_doc_symbol

        # If ' - ' is present, keep the last part
        if ' - ' in doc_symbol:
            doc_symbol = doc_symbol.split(' - ')[-1]
            hyphen_count += 1

        # Remove whitespace within parentheses
        if ' (' in doc_symbol or ') ' in doc_symbol:
            doc_symbol = doc_symbol.replace(' (', '(').replace(') ', ')')
            spaces_count += 1

        if doc_symbol != original_doc_symbol:
            modified_count += 1

        item['docSymbol'] = doc_symbol

        cleaned_dict.append(item)

        # Stop processing if we reached the maxResults count
        if len(cleaned_dict) >= maxResults:
            break

    print(f"Modified {modified_count} out of {len(input_dict)} symbols. Removed whitespaces from {spaces_count} and hyphens from {hyphen_count}. Filtered out {removed_count} items with 'draft' in docType, and {englishonly_count} with no translations available.")
    return cleaned_dict

def get_un_document_urls(document_symbol) -> dict:
    """
    Convert a UN document symbol into downloadable PDF URLs for all official UN languages

    Args:
        document_symbol: Document symbol like 'UNEP/EA.5/HLS.1'

    Returns:
        Dictionary mapping language names to their PDF URLs {'French': "https://..."}
    """
    languages = {
        "Arabic": "A",
        "Chinese": "C",
        "English": "E",
        "French": "F",
        "Russian": "R",
        "Spanish": "S"
    }

    base_url = "https://daccess-ods.un.org/access.nsf/Get?OpenAgent&DS={}&Lang={}"

    urls = {}
    for language_name, language_code in languages.items():
        url = base_url.format(document_symbol, language_code)
        urls[language_name] = url

    return urls


def is_separator_or_note(paragraph):
    """
    Check if a paragraph is a separator, note, or empty paragraph that should be skipped.
    
    Args:
        paragraph (str): The paragraph text to check
        
    Returns:
        bool: True if the paragraph is a separator or note, False otherwise
    """
    # Check if paragraph is empty
    if len(paragraph.strip()) == 0:
        return True
    
    # Check for different types of notes or separators
    is_page_number = re.match(r'\s*\*\*\d+\*\*\s*', paragraph)
    is_footnote = re.match(r'\s*K\d{7}\s\d{6}\s*', paragraph)
    is_othernote = re.match(r'^(?:\*\*.*\/.*\*\*|\*\*.*\/.*\d$|\d.*\/.*\*\*)$', paragraph)
    is_separator = re.match(r'\s*-+\s*', paragraph)
    
    return bool(is_page_number or is_footnote or is_othernote or is_separator)

def is_complete_sentence(text):
    """
    Check if a text ends with proper sentence-ending punctuation.
    
    Args:
        text (str): The text to check
        
    Returns:
        bool: True if the text ends with proper punctuation, False otherwise
    """
    text = text.strip()
    if not text:
        return False
    
    # Common sentence-ending punctuation in multiple languages
    ending_punctuation = ['.', '!', '?', '.)', '.', '».', '.")', ':]', '؟', '।', '。', '．']
    
    # Check for these ending characters
    for punct in ending_punctuation:
        if text.endswith(punct):
            return True
            
    return False

def find_paragraphs_with_merge(text, search_string, max_paragraphs=1) -> list:
    """
    Find paragraphs containing a search string and merge with continuation paragraphs if needed.
    
    This function splits text into paragraphs and searches for occurrences of the search string.
    When a match is found, it checks if the paragraph is complete (ends with proper punctuation)
    and merges with subsequent paragraphs when necessary to form complete thoughts.
    
    Args:
        text (str): The full text to search within
        search_string (str): The string to search for in paragraphs
        max_paragraphs (int, optional): Maximum number of paragraphs to return. Default is 1.
                                       Set to None to return all matching paragraphs.
    
    Returns:
        list or None: A list of matched paragraphs (possibly merged with continuation text),
                     or None if no matches were found.
    """
    paragraphs = text.split('\n\n')
    matched_paragraphs = []
    found_count = 0

    for i, paragraph in enumerate(paragraphs):
        # Check if this paragraph contains the search string
        if search_string.lower() in paragraph.lower():
            matched_paragraph = paragraph
            
            # Check if paragraph is incomplete (doesn't end with proper punctuation)
            paragraph_needs_continuation = not is_complete_sentence(paragraph)
            
            # Continue checking next paragraphs for continuation
            next_index = i + 1
            
            while paragraph_needs_continuation and next_index < len(paragraphs):
                next_para = paragraphs[next_index].strip()
                
                # If it's a separator or note, skip it but continue looking
                if is_separator_or_note(next_para):
                    next_index += 1
                    continue
                
                # Found actual content - check if it's not a new numbered paragraph
                # that would indicate a new thought rather than continuation
                if not re.match(r'\s*\d+\.\s', next_para):
                    matched_paragraph = matched_paragraph + " " + next_para
                    
                    # Check if we now have a complete sentence
                    if is_complete_sentence(matched_paragraph):
                        paragraph_needs_continuation = False
                    else:
                        # Continue looking for more text
                        next_index += 1
                else:
                    # It's a new numbered paragraph, stop merging
                    paragraph_needs_continuation = False
                
                # If we've checked too many paragraphs ahead, stop to prevent infinite loops
                if next_index > i + 5:  # Arbitrary limit to prevent excessive merging
                    paragraph_needs_continuation = False
            
            matched_paragraphs.append(matched_paragraph)
            found_count += 1

            # Check if we've reached the limit of paragraphs to return
            if max_paragraphs is not None and found_count >= max_paragraphs:
                break

    return matched_paragraphs if matched_paragraphs else None

def get_model(model_name='distiluse-base-multilingual-cased-v2'):
    """
    Load and return a SentenceTransformer model.

    This function loads a SentenceTransformer model with the specified model name.
    If the model is already loaded, it returns the existing model instance.

    Args:
        model_name (str): The name of the model to load. Default is 'distiluse-base-multilingual-cased-v2'.

    Returns:
        SentenceTransformer: The loaded SentenceTransformer model.
    """
    global model
    if model is None:
        print("Loading model...")
        model = SentenceTransformer(model_name)
    return model

def find_similar_paragraph_in_target(source_paragraph, target_text, model_name='distiluse-base-multilingual-cased-v2', top_k=1) -> list[tuple[str, float]]:
    """
    Find the most similar paragraph(s) in the target text using multilingual embeddings.
    Merges incomplete paragraphs to ensure comparison of complete thoughts.

    Args:
        source_paragraph: The source paragraph to match
        target_text: The target text to search in
        model_name: The name of the multilingual sentence embedding model to use
        top_k: Number of matching paragraphs to return

    Returns:
        List of top matching paragraphs from the target text
    """
    # Load model
    model = get_model(model_name)

    # Split target text into raw paragraphs
    raw_paragraphs = target_text.split('\n\n')
    
    # Process paragraphs - merge incomplete sentences and skip separators
    processed_paragraphs = []
    i = 0
    while i < len(raw_paragraphs):
        paragraph = raw_paragraphs[i].strip()
        
        # Skip separator or note paragraphs
        if is_separator_or_note(paragraph):
            i += 1
            continue
            
        # Check if paragraph is incomplete
        if not is_complete_sentence(paragraph):
            merged_paragraph = paragraph
            next_index = i + 1
            
            # Try to find continuation paragraphs
            while next_index < len(raw_paragraphs) and not is_complete_sentence(merged_paragraph):
                next_para = raw_paragraphs[next_index].strip()
                
                # Skip separators but continue looking
                if is_separator_or_note(next_para):
                    next_index += 1
                    continue
                
                # Check if it's not a new numbered paragraph (which would indicate a new thought)
                if not re.match(r'\s*\d+\.\s', next_para):
                    merged_paragraph = merged_paragraph + " " + next_para
                    next_index += 1
                else:
                    # It's a new numbered paragraph, stop merging
                    break
                
                # Limit the number of paragraphs to merge to prevent excessive merging
                if next_index > i + 5:
                    break
            
            processed_paragraphs.append(merged_paragraph)
            i = next_index  # Skip the paragraphs we've merged
        else:
            # It's already a complete paragraph
            processed_paragraphs.append(paragraph)
            i += 1
    
    # Handle empty processed_paragraphs (all were separators/notes)
    if not processed_paragraphs:
        return []

    # Compute embeddings
    source_embedding = model.encode([source_paragraph])
    target_embeddings = model.encode(processed_paragraphs)

    # Compute similarities
    similarities = cosine_similarity(source_embedding, target_embeddings)[0]

    # Get indices of top similar paragraphs
    top_indices = np.argsort(similarities)[-top_k:][::-1]

    # Return top matching paragraphs and their similarity scores
    results = [(processed_paragraphs[i], similarities[i]) for i in top_indices]

    return results

def askLLM_term_equivalents(source_term, source_paragraphs, target_paragraphs, source_language, target_language, customInference=False) -> str:
    """
    Query a LLM to extract term equivalents across languages. By default the LLM is claude-haiku from the free service provided by DuckDuckGo.
    For custom inference, set customInference=True and provide a local server URL for LM-Studio.

    Args:
        source_term: The specific source term to find equivalents for
        source_paragraphs: The source paragraphs (context)
        target_paragraphs: List of target paragraphs or tuples from find_similar_paragraph_in_target
        source_language: Language of the source paragraph (e.g., "English")
        target_language: Language of the target paragraphs (e.g., "Spanish")

    Returns:
        String of the LLM answer with the term equivalents extracted by the LLM: <SOURCETERM>{source_language}</SOURCETERM> = <EQUIVALENTTERM>{target_language}</EQUIVALENTTERM>
    """
    # Format the source paragraphs as a single string
    source_text = "\n\n".join(source_paragraphs) if isinstance(source_paragraphs, list) else source_paragraphs

    # Extract paragraph text from tuples if necessary
    target_texts = []
    for item in target_paragraphs:
        if isinstance(item, tuple):
            # Extract the paragraph text from the tuple
            target_texts.append(item[0])
        else:
            target_texts.append(item)

    # Join the target paragraphs
    target_text = "\n\n".join(target_texts)

    prompt = f"""
    I need to extract term equivalents of this single term '{source_term}' from these {source_language} and {target_language} paragraphs.
    Please identify the {target_language} equivalent terms for the {source_language} term: <source>{source_term}</source>, preserving all formatting
    (italics, capitalization, gender, and number).

    {source_language.upper()} PARAGRAPH:
    {source_text}

    {target_language.upper()} PARAGRAPH(S):
    {target_text}

    Please list the equivalents of '{source_term}' in this format:
    "<source>{source_term}</source>" = "<equivalent>INSERT_TERM</equivalent>"

    Do not modify the tag names <source> and <equivalent>. Do not include other source terms than '{source_term}'.
    Preserve all formatting in both languages.
    """
    if customInference:
        # Try to use local LM-Studio API first
        try:
            response = lmstudioLocalAPI(prompt)
            print("Using local LM-Studio API")
            return response
        except Exception as e:
            print(f"Error extracting term equivalents with local inference server: {str(e)}")
            print("Falling back to DuckDuckGo search...")
            # Fall back to DDGS if local API fails
            try:
                response = DDGS().chat(prompt, model='claude-3-haiku')
                return response
            except Exception as e:
                return f"Error extracting term equivalents with DDGS-chat after local API failed: {str(e)}"
    else:
        # Use DDGS directly
        try:
            response = DDGS().chat(prompt, model='claude-3-haiku')
            return response
        except Exception as e:
            return f"Error extracting term equivalents with DDGS-chat: {str(e)}"

def lmstudioLocalAPI(prompt, url='http://localhost:1234/v1'):
    """
    Generates a response from a local language model API based on the given prompt.
    Args:
        prompt (str): The input prompt to send to the language model.
        url (str, optional): The base URL of the local language model API. Defaults to 'http://localhost:1234/v1'.
    Returns:
        str: The response generated by the language model.
    Example:
        response = lmstudioLocalAPI("Hello, how are you?")
        print(response)
    """
    
    from openai import OpenAI

    client = OpenAI(base_url=url, api_key="lm-studio")

    # Create a chat completion
    completion = client.chat.completions.create(
        model="model-identifier", #not essential
        messages=[
            {"role": "system", "content": "You are a helpful multilingual assistant that understands English, French, Chinese, Arabic, Russian and Spanish."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.1,
        max_completion_tokens=800
    )

    # Return the chatbot's response
    return completion.choices[0].message.content


def getEquivalents_from_response(response) -> list:
    """
    Extract all equivalent terms from the response.

    Args:
        response: The LLM response containing <EQUIVALENTTERM> tags

    Returns:
        List of extracted equivalent terms
    """
    # Use regex to find all occurrences of text between <EQUIVALENTTERM> and </EQUIVALENTTERM>
    pattern = r'<equivalent>(.*?)</equivalent>'
    matches = re.findall(pattern, response, re.DOTALL)

    return matches

def consolidate_results(metadataCleaned, exportExcel=False) -> list:
    """
    Consolidate results by EnglishTerm and format the output according to specified requirements.
    
    Args:
        metadataCleaned: List of dictionaries containing the metadata
        
    Returns:
        List of dictionaries with consolidated data
    """
    if not metadataCleaned:
        return []
        
    # Group by EnglishTerm
    consolidated = {}
    for item in metadataCleaned:
        english_term = item.get('EnglishTerm', '')
        if not english_term:
            continue
            
        if english_term not in consolidated:
            consolidated[english_term] = {}
            
        # Get source information for this specific item
        doc_symbol = item.get('docSymbol', 'Unknown')
        pub_date = item.get('publicationDate', 'Unknown')
        
        for key, value in item.items():
            # Skip docURLs
            if key == 'docURLs':
                continue
                
            # Process Term keys
            if key.endswith('Term'):
                if key not in consolidated[english_term]:
                    consolidated[english_term][key] = value
                    
            # Process Synonyms keys
            elif key.endswith('Synonyms'):
                if value is None:
                    continue
                if key not in consolidated[english_term]:
                    consolidated[english_term][key] = value if isinstance(value, list) else [value]
                else:
                    if isinstance(value, list):
                        consolidated[english_term][key].extend(value)
                    else:
                        consolidated[english_term][key].append(value)
                    # Remove duplicates
                    consolidated[english_term][key] = list(set(consolidated[english_term][key]))
                    
            # Process Paragraphs keys
            elif key.endswith('Paragraphs'):
                if value is None:
                    continue
                    
                # Format paragraphs with source information
                formatted_paragraphs = []
                if isinstance(value, list):
                    for paragraph in value:
                        if isinstance(paragraph, str):
                            formatted_paragraphs.append(f"{paragraph} (Source: {doc_symbol} on {pub_date})")
                        elif isinstance(paragraph, tuple) and len(paragraph) >= 1:
                            formatted_paragraphs.append(f"{paragraph[0]} (Source: {doc_symbol} on {pub_date})")
                
                # Join paragraphs with double newlines
                formatted_text = "\n\n".join(formatted_paragraphs) if formatted_paragraphs else ""
                
                if key not in consolidated[english_term]:
                    consolidated[english_term][key] = formatted_text
                elif formatted_text:  # Only add if there's actual text
                    consolidated[english_term][key] += "\n\n" + formatted_text
                    
            # Other metadata keys
            elif key in ['docSymbol', 'publicationDate', 'docType', 'docTitle']:
                if key not in consolidated[english_term]:
                    consolidated[english_term][key] = value
                elif value and value != consolidated[english_term][key]:
                    if isinstance(consolidated[english_term][key], str):
                        consolidated[english_term][key] += "\n" + str(value)
                    else:
                        consolidated[english_term][key] = str(consolidated[english_term][key]) + "\n" + str(value)
    
    # Convert to list and sort keys in the desired order
    result = []
    for term, data in consolidated.items():
        # Create a new dictionary with ordered keys
        ordered_data = {}
        
        # 1. EnglishTerm
        ordered_data['EnglishTerm'] = term
        
        # 2. Other Term keys
        term_keys = sorted([k for k in data.keys() if k.endswith('Term') and k != 'EnglishTerm'])
        for key in term_keys:
            ordered_data[key] = data[key]
            
        # 3. Synonyms keys
        synonym_keys = sorted([k for k in data.keys() if k.endswith('Synonyms')])
        for key in synonym_keys:
            ordered_data[key] = data[key]
            
        # 4. EnglishParagraphs
        if 'EnglishParagraphs' in data:
            ordered_data['EnglishParagraphs'] = data['EnglishParagraphs']
            
        # 5. Other Paragraph keys
        para_keys = sorted([k for k in data.keys() if k.endswith('Paragraphs') and k != 'EnglishParagraphs'])
        for key in para_keys:
            ordered_data[key] = data[key]
            
        # 6. Metadata keys
        meta_keys = ['docSymbol', 'publicationDate', 'docType', 'docTitle']
        for key in meta_keys:
            if key in data:
                ordered_data[key] = data[key]
        
        result.append(ordered_data)
    
    # Export to Excel if requested in a try-except block
    if exportExcel and result:
        try:
            df = pl.DataFrame(result.copy())
            
            # Use EnglishTerm for the filename
            english_term = result[0]['EnglishTerm']
            base_filename = re.sub(r'[\\/*?:"<>|]', '_', english_term)
            filename = f"{base_filename}.xlsx"
            
            # Check if file exists and append number if needed
            counter = 1
            while os.path.exists(filename):
                filename = f"{base_filename}_{counter}.xlsx"
                counter += 1
                
            df.write_excel(filename)
            print(f"Exported consolidated results to '{filename}'")
        except Exception as e:
            print(f"Error exporting consolidated results: {str(e)}")

    return result