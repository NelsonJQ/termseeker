def extract_document_symbols(html_content) -> list:
    """
    Extract document symbols from the given HTML content.

    Args:
        html_content (str): The HTML content of the search results page.

    Returns:
        list: A list of extracted document symbols.
    """
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')
    document_symbols = []

    # Find all div elements with class 'brief-options'
    for div in soup.find_all('div', class_='brief-options'):
        # Find the first <i> tag with class 'fa-globe' and get the next sibling text
        globe_icon = div.find('i', class_='fa-globe')
        if globe_icon:
            document_symbol = globe_icon.next_sibling.strip()
            document_symbols.append(document_symbol)

    return document_symbols


def extract_metadata_UNLib(html_content) -> list:
    """
    Extract metadata from the UN Digital Library search results.

    Args:
        html_content (str): The HTML content of the search results page.

    Returns:
        list: A list of dictionaries containing extracted metadata.
    """
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')
    metadata_list = []

    # Find all div elements with class 'result-row'
    for div in soup.find_all('div', class_='result-row'):
        metadata = {}

        # Extract document symbol
        globe_icon = div.find('i', class_='fa-globe')
        if globe_icon:
            metadata['docSymbol'] = globe_icon.next_sibling.strip()

        # Extract publication date
        calendar_icon = div.find('i', class_='fa-calendar')
        if calendar_icon:
            metadata['publicationDate'] = calendar_icon.next_sibling.strip()

        # Extract document type
        tag_icon = div.find('i', class_='fa-tag')
        if tag_icon:
            metadata['docType'] = tag_icon.next_sibling.strip()

        # Extract document title
        result_title = div.find('div', class_='result-title')
        if result_title and result_title.find('a'):
            metadata['docTitle'] = result_title.find('a').text.strip()

        # Check if there are multiple files
        file_area = div.find('div', class_='file-area')
        if file_area and 'Multiple Files' in file_area.get_text():
            metadata['isMultiple'] = True
        else:
            metadata['isMultiple'] = False

        metadata_list.append(metadata)

    return metadata_list