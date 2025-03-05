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