# Project Overview

TermHunter is a Python application designed to facilitate the terminology work by searching for candidate terms in UN languages in official UN documents. The application uses the UN Digital Library search results in one or multiple languages (Arabic, Spanish, French, Russian, Chinese).

## Features

- Convert Word documents to Markdown format.
- Convert PDF documents (from local files or URLs) to Markdown format.
- Search the UN Digital Library by term and document symbol.
- Extract document symbols and metadata from search results.
- Generate downloadable PDF URLs for UN documents in all official languages.

## Google Colab

You can test the installation and execution of the `termun` library using Google Colab. Click the link below to open the notebook:

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/NelsonJQ/termun/blob/main/playground_termHunter.ipynb)

## Installation

To set up the project, clone the repository and install the required dependencies:

```bash
git clone https://github.com/NelsonJQ/termun.git
cd termun
pip install .
```

## Usage

### Using getCandidates()

The `getCandidates()` function is the core function of this application. It searches for documents in the UN Digital Library based on the provided search text, languages, and filter symbols. It then processes the documents to extract relevant paragraphs and terms.

#### Function Signature

```python
def getCandidates(input_search_text, input_lang, input_filterSymbols, sourcesQuantity, paragraphsPerDoc, eraseDrafts):
```

#### Parameters

- `input_search_text` (str): The search text to find terminology for.
- `input_lang` (list or str): Target languages (e.g., ["Spanish", "French"]). Use "ALL" for all supported languages.
- `input_filterSymbols` (list): Filter symbols (e.g., ["UNEP/CBD", "UNEP/EA"]).
- `sourcesQuantity` (int): Number of sources to retrieve.
- `paragraphsPerDoc` (int): Paragraphs per document.
- `eraseDrafts` (bool): Whether to erase draft documents.

#### Example Usage

```python
from termun.getcandidates import getCandidates

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
def consolidate_results(metadataCleaned, exportExcel=False) -> list:
```

#### Parameters

- `metadataCleaned` (list): List of dictionaries containing the cleaned metadata.
- `exportExcel` (bool): Whether to export the consolidated results as an Excel file.

#### Example Usage

```python
from termun.utils import consolidate_results

# Assuming `results` is the output from getCandidates()
consolidated_results = consolidate_results(results, exportExcel=True)
print(consolidated_results)
```

### Example of Returned DataFrame

The following is an example of the returned dataframe by `consolidate_results()` and `getCandidates()`:

```
| EnglishTerm                                                                        | FrenchTerm                                                                                     | SpanishTerm                                                                      | FrenchSynonyms | SpanishSynonyms | EnglishParagraphs                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             | FrenchParagraphs                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            | SpanishParagraphs                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         | docSymbol                                          | publicationDate                        | docType                                                            | docTitle                                                                                                                                                                                                                                                                                                                                                                                         |
| ---------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------- | -------------- | --------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------- | -------------------------------------- | ------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 10-Year Framework of Programmes on Sustainable Consumption and Production Patterns | Cadre décennal de programmation concernant les modes de consommation et de production durables | Marco Decenal de Programas sobre Modalidades de Consumo y Producción Sostenibles | []             | []              | _Emphasizing the need to further strengthen programmes, partnerships and frameworks, such as_<br>the 10-Year Framework of Programmes on Sustainable Consumption and Production Patterns,<br>relevant to sustainable consumption and production to replicate and scale up sustainable consumption<br>and production policies and good practices, respecting national ownership of countries’ development<br>strategies, (Source: UNEP/EA.2/RES.8 on 2016-08-03)<br><br>6\. \_Also requests the Executive Director to continue and strengthen the efforts of the_<br>United Nations Environment Programme to facilitate implementation of all programmes of the<br>10-Year Framework of Programmes on Sustainable Consumption and Production Patterns, taking into<br>account national strategies, capabilities and priorities, including through: (Source: UNEP/EA.2/RES.8 on 2016-08-03)<br><br>6\. The 10-Year Framework of Programmes on Sustainable Consumption and Production Patterns<br>reported that some $80 million has been made available by partners in its programmes up to December<br>2016\. Sustainable Development Goal 12 was allocated $90 million across the United Nations system<br>in 2016, with the Environment Programme providing the most significant contribution. The report of<br>the 10-Year Framework to the high-level political forum on sustainable development highlighted the<br>high demand for support (more than 600 eligible projects were submitted to the trust fund, although<br>only 33 could be financed). (Source: UNEP/EA.3/11 on 2017-09-20) | _Soulignant qu’il faut continuer de renforcer les programmes, les partenariats et les cadres, tels_<br>que le Cadre décennal de programmation concernant les modes de consommation et de production<br>durables, qui présentent un intérêt pour la consommation et la production durables, afin de transposer<br>et d’appliquer sur une plus grande échelle les politiques sur le sujet et les bonnes pratiques, en<br>respectant l’appropriation nationale des stratégies de développement de chaque pays, (Source: UNEP/EA.2/RES.8 on 2016-08-03)<br><br>6\. \_Prie également le Directeur exécutif de poursuivre et de renforcer les activités menées_<br>par le Programme des Nations Unies pour l’environnement pour faciliter la mise en œuvre de tous les<br>programmes du Cadre décennal de programmation concernant les modes de consommation et de<br>production durables, compte tenu des stratégies, capacités et priorités nationales et, à cette fin : (Source: UNEP/EA.2/RES.8 on 2016-08-03)<br><br>6\. Selon le Cadre décennal de programmation concernant les modes de consommation et de<br>production durables, quelque 80 millions de dollars avaient été mis à disposition par les partenaires de<br>ses programmes avant décembre 2016. L’objectif de développement durable n[o ]12 s’est vu allouer<br>90 millions de dollars à l’échelle du système des Nations Unies en 2016, le Programme pour<br>l’environnement ayant été le plus important contributeur. Le rapport du Cadre décennal au Forum<br>politique de haut niveau pour le développement durable a appelé l’attention sur la forte demande de<br>soutiens (plus de 600 projets éligibles ont été soumis au Fonds d’affectation spéciale, dont seuls 33 ont<br>pu être financés). (Source: UNEP/EA.3/11 on 2017-09-20) | _Haciendo hincapié en la necesidad de seguir fortaleciendo los programas y las asociaciones y_<br>los marcos, como el Marco Decenal de Programas sobre Modalidades de Consumo y Producción<br>Sostenibles, que guardan relación con el consumo y la producción sostenibles para reproducir y<br>ampliar las políticas de consumo y producción sostenibles y las buenas prácticas, respetando las<br>estrategias de desarrollo que son responsabilidad de los países, (Source: UNEP/EA.2/RES.8 on 2016-08-03)<br><br>6\. \_Solicita también al Director Ejecutivo que prosiga y redoble los esfuerzos del_<br>Programa de las Naciones Unidas para el Medio Ambiente para facilitar la ejecución de todos<br>los programas del Marco Decenal de Programas sobre Modalidades de Consumo y Producción<br>Sostenibles, teniendo en cuenta las estrategias, capacidades y prioridades nacionales, en<br>particular mediante: (Source: UNEP/EA.2/RES.8 on 2016-08-03)<br><br>6\. El Marco Decenal de Programas sobre Modalidades de Consumo y Producción Sostenibles<br>informó de que a diciembre de 2016 los asociados en sus programas habían aportado unos 80 millones<br>de dólares. En 2016, en todo el sistema de las Naciones Unidas se asignaron 90 millones de dólares<br>para la consecución del Objetivo de Desarrollo Sostenible 12, y la contribución más significativa fue<br>la realizada por el Programa para el Medio Ambiente. En el informe del Marco Decenal de Programas<br>sobre Modalidades de Consumo y Producción Sostenibles al foro político de alto nivel sobre el<br>desarrollo sostenible se destacó la gran demanda de apoyo (se presentaron al Fondo Fiduciario más<br>de 600 proyectos que reunían las condiciones, aunque solo podrían financiarse 33). (Source: UNEP/EA.3/11 on 2017-09-20) | UNEP/EA.2/RES.8<br>UNEP/EA.1/INF/3<br>UNEP/EA.3/11 | 2016-08-03<br>2014-05-30<br>2017-09-20 | Resolutions and Decisions<br>Documents and Publications<br>Reports | 2/8. Sustainable consumption and production : resolution / adopted by the United Nations Environment Assembly<br>Results of the sixty-eighth session of the General Assembly of relevance to the United Nations Environment Assembly : note / by the Executive Director<br>Progress made pursuant to resolution 2/8 on sustainable consumption and production : report of the Executive Director |
```

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
from termun.utils import askLLM_term_equivalents

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

This project is licensed under the MIT License. See the LICENSE file for more details.