#!pip install polars datasets huggingface_hub

import polars as pl
from datasets import load_dataset
from huggingface_hub import login, whoami

global HUGGINGFACE_TOKEN
HUGGINGFACE_TOKEN = ""  # Set your Hugging Face token here if needed

def query_dataset_by_term_and_symbol(HFdatasetName, input_term, input_symbol, tgt_content="dst_text", SplitSample="train", limit_rows=2, hf_token=None):
    """Filters a Hugging Face dataset based on the presence of a term and symbol, using streaming to handle large datasets without fully loading them into memory.
        HFdatasetName (str): The name of the Hugging Face dataset to filter. Defaults to "bot-yaya/undl_es2en_aligned" if an empty string is provided, alternatives are found in https://huggingface.co/bot-yaya for other language combinations.
        input_term (str): The term to search for in the dataset.
        input_symbol (str): The symbol to search for in the dataset. For certain datasets, this is checked in the first 10 lines of the "en" column.
        tgt_content (str, optional): The target column to search for the term and symbol. Defaults to "dst_text".
        SplitSample (str, optional): The dataset split to use (e.g., "train", "test"). Defaults to "train".
        limit_rows (int, optional): The maximum number of rows to return. Defaults to 2.
        hf_token (str, optional): The Hugging Face token for authentication. Defaults to None.
        Iterable or None: A filtered dataset containing rows where both the term and symbol are present, or None if no results are found.
    Raises:
        Exception: If there is an error logging in to Hugging Face or filtering the dataset.
    Notes:
        - For the dataset "ranWang/UN_Historical_PDF_Article_Text_Corpus", the symbol is searched in the first 10 lines of the "en" column.
        - For other datasets, slashes in the symbol are replaced with underscores, and the symbol is matched against the "record" column.
    """
    # Try to login to Hugging Face if a token is provided
    if hf_token:
        try:
            from huggingface_hub import login
            login(token=hf_token)
            whoami()
        except Exception as e:
            print(f"Error logging in to Hugging Face: {e}")
    
    HFdatasetName = "bot-yaya/undl_es2en_aligned" if HFdatasetName == "" else HFdatasetName

    dataset = load_dataset(HFdatasetName, split=SplitSample, streaming=True)

    if HFdatasetName == "ranWang/UN_Historical_PDF_Article_Text_Corpus":
        filtered_dataset = dataset.filter(
        lambda example: input_term in example["en"]
        and f" {input_symbol}/" in "\n".join(example["en"].split("\n")[:10])
    )

    else:
    # Replace slashes with underscores
        input_symbol = input_symbol.replace("/", "_")
        filtered_dataset = dataset.filter(
            lambda example: input_term in example[tgt_content]
            and example["record"].startswith(input_symbol)
        )


    try:
        results = filtered_dataset.take(limit_rows)
        print("Found results")
    except:
        try:
            print("No results found, trying with a different limit: 1 row.")
            results = filtered_dataset.take(1)
        except:
            results = None
            print("No results found")

    print(results)