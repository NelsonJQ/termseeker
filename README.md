# Project Overview

TermSeeker is a Python application designed to facilitate the terminology work by searching for candidate terms in UN languages in official UN documents. The application uses the UN Digital Library search results in one or multiple languages (Arabic, Spanish, French, Russian, Chinese).

## Features

- Convert Word documents to Markdown format.
- Convert PDF documents (from local files or URLs) to Markdown format.
- Search the UN Digital Library by term and document symbol.
- Extract document symbols and metadata from search results.
- Generate downloadable PDF URLs for UN documents in all official languages.

## Google Colab

You can test the installation and execution of the `termseeker` library using Google Colab. Click the link below to open the notebook:

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/NelsonJQ/termseeker/blob/main/playground_termseeker.ipynb)

## Installation

To set up the project, clone the repository and install the required dependencies:

```bash
git clone https://github.com/NelsonJQ/termseeker.git
cd termseeker
pip install .
```

## Usage

### Using getCandidates()

The `getCandidates()` function is the core function of this application. It searches for documents in the UN Digital Library based on the provided search text, languages, and filter symbols. It then processes the documents to extract relevant paragraphs and terms.

#### Function Signature

```python
def getCandidates(input_search_text, input_lang,
                input_filterSymbols, sourcesQuantity,
                paragraphsPerDoc, eraseDrafts,
                localLM=False, groqToken=None
                ):
```

#### Parameters

- `input_search_text` (str): The search text to find terminology for.
- `input_lang` (list or str): Target languages (e.g., ["Spanish", "French"]). Use "ALL" for all supported languages.
- `input_filterSymbols` (list): Filter symbols (e.g., ["UNEP/CBD", "UNEP/EA"]).
- `sourcesQuantity` (int): Number of sources to retrieve.
- `paragraphsPerDoc` (int): Paragraphs per document.
- `eraseDrafts` (bool): Whether to erase draft documents.
- `localLM` (bool): Whether to use LM Studio for local inference server (Ollama) (Optional, set it as None to skip term extraction by any local or cloud LLM)
- `groqToken` (str): API key for Groq cloud inference server (70b model) (Optional)

#### Example Usage

```python
from termseeker.getcandidates import getCandidates

input_search_text = "10-Year Framework of Programmes on Sustainable Consumption and Production Patterns"
input_lang = ["Spanish", "French"]
input_filterSymbols = ["UNEP/CBD", "UNEP/EA", "FCCC"]
sourcesQuantity = 3
paragraphsPerDoc = 2
eraseDrafts = True

results = getCandidates(input_search_text, input_lang, input_filterSymbols, sourcesQuantity, paragraphsPerDoc, eraseDrafts)
print(results)
```

### Using consolidate_results()

The `consolidate_results()` function from `utils.py` consolidates the results obtained from `getCandidates()` into a compact dataframe and optionally exports it as an Excel file.

#### Function Signature

```python
def consolidate_results(result, exportExcel=False) -> list:
```

#### Parameters

- `result` (list): List of dictionaries containing the cleaned metadata (output from `getCandidates()`).
- `exportExcel` (bool): Whether to export the consolidated results as an Excel file.

#### Example Usage

```python
from termseeker.utils import consolidate_results

# Assuming `results` is the output from getCandidates()
consolidated_results = consolidate_results(results, exportExcel=True)
print(consolidated_results)
```

### Example of Returned DataFrame

The following is an example of the returned dataframe by `consolidate_results()` and `getCandidates()`:

| EnglishTerm                                                                        | FrenchTerm                                                                                     | SpanishTerm                                                                      | FrenchSynonyms | SpanishSynonyms | EnglishParagraphs                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             | FrenchParagraphs                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            | SpanishParagraphs                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         | docSymbol                                          | publicationDate                        | docType                                                            | docTitle                                                                                                                                                                                                                                                                                                                                                                                         |
| ---------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------- | -------------- | --------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------- | -------------------------------------- | ------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 10-Year Framework of Programmes on Sustainable Consumption and Production Patterns | Cadre décennal de programmation concernant les modes de consommation et de production durables | Marco Decenal de Programas sobre Modalidades de Consumo y Producción Sostenibles | []             | []              | _Emphasizing the need to [...] such as_<br>the 10-Year Framework of Programmes on Sustainable Consumption and Production Patterns,<br>relevant to [...], (Source: UNEP/EA.2/RES.8 on 2016-08-03)<br><br>6\. \_Also requests the [...] of the<br>10-Year Framework of Programmes on Sustainable Consumption and Production Patterns, taking into<br>account [...]: (Source: UNEP/EA.2/RES.8 on 2016-08-03)<br><br>6\. The 10-Year Framework of Programmes on Sustainable Consumption and Production Patterns<br>reported that some $80 million [...]. (Source: UNEP/EA.3/11 on 2017-09-20) | _Soulignant qu’il faut_ [...]<br>que le Cadre décennal de programmation concernant les modes de consommation et de production<br>durables, qui présentent [...], (Source: UNEP/EA.2/RES.8 on 2016-08-03)<br><br>6\. \_Prie également le [...] du Cadre décennal de programmation concernant les modes de consommation et de<br>production durables, compte tenu des [...] : (Source: UNEP/EA.2/RES.8 on 2016-08-03)<br><br>6\. Selon le Cadre décennal de programmation concernant les modes de consommation et de<br>production durables, quelque 80 millions de dollars avaient [...]. (Source: UNEP/EA.3/11 on 2017-09-20) | _Haciendo hincapié en_ [...] como el Marco Decenal de Programas sobre Modalidades de Consumo y Producción<br>Sostenibles, que guardan [...], (Source: UNEP/EA.2/RES.8 on 2016-08-03)<br><br>6\. \_Solicita también al [...] del Marco Decenal de Programas sobre Modalidades de Consumo y Producción<br>Sostenibles, teniendo en cuenta las [...]: (Source: UNEP/EA.2/RES.8 on 2016-08-03)<br><br>6\. El Marco Decenal de Programas sobre Modalidades de Consumo y Producción Sostenibles<br>informó de que a [...]. (Source: UNEP/EA.3/11 on 2017-09-20) | UNEP/EA.2/RES.8<br>UNEP/EA.1/INF/3<br>UNEP/EA.3/11 | 2016-08-03<br>2014-05-30<br>2017-09-20 | Resolutions and Decisions<br>Documents and Publications<br>Reports | 2/8. Sustainable consumption and production : resolution / adopted by the United Nations Environment Assembly<br>Results of the sixty-eighth session of the General Assembly of relevance to the United Nations Environment Assembly : note / by the Executive Director<br>Progress made pursuant to resolution 2/8 on sustainable consumption and production : report of the Executive Director |

### Choosing Between Local Inference Server and DDGS

The `askLLM_term_equivalents` function can use either a local inference server (using [LM Studio AI](https://github.com/lmstudio-ai)) or the [DuckDuckGo Search (DDGS)](https://github.com/deedy5/duckduckgo_search?tab=readme-ov-file#1-chat---ai-chat) service to extract term equivalents.

- **Local Inference Server**: 
  - **Advantages**: No dependency on external services, full data privacy, and more control over the model and its parameters.
  - **Disadvantages**: Requires setup and maintenance of the local server, which might be resource-intensive. See the documentation for calling to the server's endpoint [here](https://lmstudio.ai/docs/app/api/endpoints/openai).

- **DDGS**:
  - **Advantages**: Easy to use without setup, leverages powerful models hosted by DuckDuckGo.
  - **Disadvantages**: Dependent on external service availability and internet connection, potentially slower response times.

#### Example Usage

```python
from termseeker.utils import askLLM_term_equivalents

# Using DDGS
response = askLLM_term_equivalents(
    source_term="climate change",
    source_paragraphs=["..."],
    target_paragraphs=["..."],
    source_language="English",
    target_language="Spanish",
    customInference=False
)
print(response)

# Using Local Inference Server
response = askLLM_term_equivalents(
    source_term="climate change",
    source_paragraphs=["..."],
    target_paragraphs=["..."],
    source_language="English",
    target_language="Spanish",
    customInference=True
)
print(response)
```

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any enhancements or bug fixes.

## License

This project is licensed under the MIT License and requires permission from UN Digital Library. See the LICENSE file for more details.