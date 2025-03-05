import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import re
from duckduckgo_search import DDGS

def find_similar_paragraph_in_target(source_paragraph, target_text, model_name='distiluse-base-multilingual-cased-v2', top_k=1) -> list[tuple[str, float]]:
    """
    Find the most similar paragraph(s) in the target text using multilingual embeddings.

    Args:
        source_paragraph: The source paragraph to match
        target_text: The target text to search in
        model_name: The name of the multilingual sentence embedding model to use
        top_k: Number of matching paragraphs to return

    Returns:
        List of top matching paragraphs from the target text
    """
    # Load model
    model = SentenceTransformer(model_name)

    # Split target text into paragraphs
    target_paragraphs = target_text.split('\n\n')

    # Compute embeddings
    source_embedding = model.encode([source_paragraph])
    target_embeddings = model.encode(target_paragraphs)

    # Compute similarities
    similarities = cosine_similarity(source_embedding, target_embeddings)[0]

    # Get indices of top similar paragraphs
    top_indices = np.argsort(similarities)[-top_k:][::-1]

    # Return top matching paragraphs and their similarity scores
    results = [(target_paragraphs[i], similarities[i]) for i in top_indices]

    return results

def askLLM_term_equivalents(source_term, source_paragraphs, target_paragraphs, source_language, target_language) -> str:
    """
    Query a LLM using DDGS().chat() to extract term equivalents across languages.

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
    I need to extract term equivalents of {source_term} between these {source_language} and {target_language} paragraphs.
    Please identify the {target_language} equivalent terms for the {source_language} term: <SOURCETERM>{source_term}</SOURCETERM>, preserving all formatting
    (italics, capitalization, gender, and number).

    {source_language.upper()} PARAGRAPH:
    {source_text}

    {target_language.upper()} PARAGRAPH(S):
    {target_text}

    Please list the equivalents in this format:
    "<SOURCETERM>{source_language}</SOURCETERM>" = "<EQUIVALENTTERM>{target_language}</EQUIVALENTTERM>"

    Answer only with the requested term and its equivalent in a single line.
    Preserve all formatting in both languages.
    """

    try:
        # Query the LLM using DuckDuckGo's chat feature
        response = DDGS().chat(prompt, model='claude-3-haiku')
        return response
    except Exception as e:
        return f"Error extracting term equivalents: {str(e)}"

def getEquivalents_from_response(response) -> list:
    """
    Extract all equivalent terms from the response.

    Args:
        response: The LLM response containing <EQUIVALENTTERM> tags

    Returns:
        List of extracted equivalent terms
    """
    # Use regex to find all occurrences of text between <EQUIVALENTTERM> and </EQUIVALENTTERM>
    pattern = r'<EQUIVALENTTERM>(.*?)</EQUIVALENTTERM>'
    matches = re.findall(pattern, response, re.DOTALL)

    return matches