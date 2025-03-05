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

    if int(maxResults) > 50:
        maxResults = 50

    for item in input_dict:
        # If removeDrafts is True, skip items with 'draft' in docType
        if removeDrafts and 'draft' in item['docType'].lower():
            removed_count += 1
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

    print(f"Modified {modified_count} out of {len(input_dict)} symbols. Removed whitespaces from {spaces_count} and hyphens from {hyphen_count}. Removed {removed_count} items with 'draft' in docType.")
    return cleaned_dict