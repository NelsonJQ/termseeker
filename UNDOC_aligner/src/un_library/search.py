import requests
from bs4 import BeautifulSoup

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