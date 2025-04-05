"""
UN Library functions for TermSeeker

This module provides functions for:
- Accessing the UN Digital Library for document retrieval
- Performing advanced searches
- Extracting metadata from UN Library documents
"""

import requests
from bs4 import BeautifulSoup
import json
import urllib.parse
import base64

def access_un_library_by_term_and_symbol(term, document_symbol) -> str:
    """
    Access the UN Digital Library and search for documents by term and document symbol.

    Args:
        term (str): The search term to look for in the full text.
        document_symbol (str): The document symbol to filter the search results.

    Returns:
        str: The HTML content of the search results page if the request is successful, None otherwise.
    """
    try:
        # Base URL
        base_url = "https://digitallibrary.un.org/search?"

        # Construct the URL with the provided term and document symbol
        url = (
            f"{base_url}ln=en&as=1&m1=p&p1={document_symbol}&f1=documentsymbol&op1=a"
            f"&m2=p&p2={term}&f2=fulltext&op2=a&rm=&sf=title&so=a&rg=50"
            f"&c=United+Nations+Digital+Library+System&of=hb&fti=1"
        )

        # Send an HTTP GET request to the URL
        response = requests.get(url)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            print("Request was successful. Content:")

            # Parse the HTML content using BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')

            # Return the HTML content
            return soup.prettify()
        else:
            print(f"Failed to retrieve the URL. Status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None

def adv_search_un_library(document_symbol=None, fulltext_term=None, date_from=None, date_to=None):
    """
    Build a search URL for the UN Digital Library

    Args:
        document_symbol: Document symbol or symbols (can be a string or list)
        fulltext_term: Term to search in full text
        date_from: Start date in YYYY-MM-DD format
        date_to: End date in YYYY-MM-DD format

    Returns:
        Search URL for the UN Digital Library
    """
    # Base URL
    base_url = "https://digitallibrary.un.org/search?"

    # Create the search query structure
    query = {
        "date_selector": {
            "dateType": "creation_date",
            "datePeriod": "specificdateperiod",
            "dateFrom": date_from or "2019-01-01",
            "dateTo": date_to or "2025-02-17"
        },
        "clauses": []
    }

    # Add document symbol search if provided
    if document_symbol:
        if isinstance(document_symbol, list):
            doc_symbols = " ".join(document_symbol)
        else:
            doc_symbols = document_symbol

        query["clauses"].append({
            "searchIn": "documentsymbol",
            "contain": "any-words",
            "term": doc_symbols,
            "operator": "AND"
        })

    # Add fulltext search if provided
    if fulltext_term:
        query["clauses"].append({
            "searchIn": "fulltext",
            "contain": "phrase-match",
            "term": fulltext_term,
            "operator": "AND"
        })

    # Convert query to JSON and then URL encode it (only once)
    query_json = json.dumps(query)
    encoded_query = urllib.parse.quote(query_json)
    encoded_query = base64.b64encode(encoded_query.encode()).decode()

    # Build parameters manually to ensure correct format
    params = [
        ("ln", "en"),
        ("as", "1"),
        ("so", "d"),
        ("rg", "50"),
        ("c", "Resource Type"),  # Note: space, not +
        ("c", "UN Bodies"),      # Separate parameter
        ("of", "hb"),
        ("fti", "1"),
        ("fti", "1"),            # Repeated parameter
        ("as_query", encoded_query),
        ("action_search", "placeholder")
    ]

    # Encode each parameter correctly
    url_parts = []
    for key, value in params:
        # Don't encode as_query again as it's already encoded
        if key == "as_query":
            url_parts.append(f"{key}={value}")
        else:
            url_parts.append(f"{key}={urllib.parse.quote(value)}")

    url = base_url + "&" + "&".join(url_parts) + "#searchresultsbox"

    print(url)
    # Send an HTTP GET request to the URL
    response = requests.get(url)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        print("Request was successful. Content:")

        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')

        # Return the HTML content
        return soup.prettify()
    else:
        print(f"Failed to retrieve the URL. Status code: {response.status_code}")
        return None

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

