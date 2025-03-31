import os

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

import time
from bs4 import BeautifulSoup


def queryUNTerm(TEXT_TO_SEARCH):
    # Create a new directory for the user data
    user_data_dir = "/tmp/chrome_user_data"
    os.makedirs(user_data_dir, exist_ok=True)

    # Set up Chrome options for Google Colab
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument(f'--user-data-dir={user_data_dir}')
    options.add_argument('--profile-directory=Profile 3')

    # Initialize the WebDriver
    driver = webdriver.Chrome(options=options)

    try:
        # Step 1: Open the settings page and activate the Spanish checkbox
        driver.get("https://unterm.un.org/unterm2/settings?displayIn=es&searchin=ar&searchin=en&searchin=es&searchin=fr&searchin=ru&searchin=zh")
        wait = WebDriverWait(driver, 1)  # Increase wait time to 5 seconds

        # Print the raw HTML of the settings page
        page_source = driver.page_source
        #print(page_source)

        # Check if the Spanish checkbox is present in the HTML
        if "title=\"Spanish\" type=\"checkbox\" name=\"displayIn\"" not in page_source:
            print("Spanish checkbox not found in the HTML.")

        # Retry mechanism to ensure the checkbox is clickable
        retries = 0
        for attempt in range(retries):
            try:
                spanish_checkbox = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@title='Spanish' and @name='displayIn']")))
                spanish_checkbox.click()
                print("Spanish checkbox clicked.")
                break
            except Exception as e:
                print(f"Attempt {attempt + 1} failed: {e}")
                time.sleep(2)  # Wait before retrying
            else:
                print("Exception(\"Failed to click the Spanish checkbox after multiple attempts.\")")

        time.sleep(1)  # Wait for the checkbox to be activated

        # Click the "Update Default Settings" button
        try:
            update_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@type='submit' and contains(text(), 'Update Default Settings')]")))
            update_button.click()
            print("Update Default Settings button clicked.")
        except Exception as e:
            print(f"Failed to click the Update Default Settings button: {e}")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Continue even if it fails
        pass

    try:
        # Step 1: Go to the search URL with the specified parameters
        search_url = f"https://unterm.un.org/unterm2/en/search?searchTerm={TEXT_TO_SEARCH}&searchType=0&searchLanguages=ar&searchLanguages=en&searchLanguages=es&searchLanguages=fr&searchLanguages=ru&searchLanguages=zh&languagesDisplay=en&languagesDisplay=es&acronymSearch=true&localDBSearch=true&termTitleSearch=true&phraseologySearch=false&footnoteSearch=false&fullTextSearch=false&facetedSearch=false&buildSubjectList=true"
        driver.get(search_url)
        wait = WebDriverWait(driver, 10)  # Increase wait time to 10 seconds

        # Step 2: Click on Advanced Settings
        try:
            advanced_search_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.btn.text-dark.text-nowrap.btn-link.collapsed")))
            advanced_search_button.click()
        except Exception as e:
            print(f"CSS Failed to search-click the Advanced search button: {e}")
            #driver.save_screenshot("/content/screenshot_ERROR_filters.png")

        time.sleep(2)  # Wait for the advanced search options to be visible

        # Step 3: Activate the Display in: "Spanish" button and other languages
        languages = ["Spanish", "Russian", "Chinese", "Arabic",
                     "Portuguese"]
        for lang in languages:
            try:
                lang_button = wait.until(EC.element_to_be_clickable((By.XPATH, f"//button[@id='ds-{lang}' and @aria-pressed='false']")))
                lang_button.click()
                print(f"Display in {lang} button clicked.")
            except Exception as e:
                print(f"Failed to click the Display in {lang} button: {e}")

        #driver.save_screenshot("/content/screenshot_filters.png")

        # Step 4: Wait for the table to be visible and scrape its HTML content
        try:
            table = wait.until(EC.visibility_of_element_located((By.XPATH, "//table")))
            table_html = table.get_attribute('outerHTML')
            print("Table HTML content retrieved.")
        except Exception as e:
            print(f"Failed to retrieve the table HTML content: {e}")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Close the WebDriver
        driver.quit()

    # Step 5: Convert the table HTML to a dictionary
    try:
        soup = BeautifulSoup(table_html, 'html.parser')
        rows = soup.find_all('tr')
        data = []
        for row in rows:
            cols = row.find_all('td')
            if len(cols) > 0:
                row_data = {}
                for col, lang in zip(cols[1:], ["English", "French", "Spanish", "Russian", "Chinese", "Arabic"]):
                    terms = []
                    ul = col.find('ul', class_='search-result')
                    if ul:
                        for li in ul.find_all('li'):
                            span = li.find('span', class_=True, lang=True)
                            if span:
                                term = span.get_text(strip=False)
                                term_class = span['class'][0]
                                terms.append({"term": term, "termClass": term_class})
                    row_data[lang] = terms

                # Extract source information
                source_div = cols[-1].find('div', class_='record-info')
                if source_div:
                    source = source_div.find('h5').get_text(strip=False)
                    tags = [li.get_text(strip=False) for li in source_div.find_all('li')]
                    row_data["UNTerm_Source"] = {"source": source, "tags": tags}
                else:
                    row_data["UNTerm_Source"] = {"source": "", "tags": []}

                data.append(row_data)
        #table_html_io = StringIO(table_html)
        #df = pd.read_html(table_html_io)[0]
        #markdown_table = df.to_markdown(index=False)
        #print(markdown_table)
        #data_df = pd.DataFrame(data)

        #return [data, markdown_table, table_html, df, data_df]
        return data
    except Exception as e:
        print(f"Failed to convert the table HTML to a dictionary: {e}")
        #return table_html
        return None
    

def report_missing_translations(consolidated_data):
    """
    Reports missing translations in the consolidated UNTERM data.
    
    Args:
        consolidated_data (dict): Dictionary returned by consolidate_UNTERMres()
        
    Returns:
        dict: Dictionary with two keys:
            - missingPreferred: list of languages with empty main translations
            - missingSynonyms: list of languages with empty synonyms lists
    """
    result = {
        "missingPreferred": [],
        "missingSynonyms": []
    }
    
    # Check for missing preferred translations
    for lang in ["English", "French", "Spanish", "Russian", "Chinese", "Arabic"]:
        if not consolidated_data.get(lang):  # This will catch '', None, or missing keys
            result["missingPreferred"].append(lang)
    
    # Check for missing synonyms
    for lang in ["French", "Spanish", "Russian", "Chinese", "Arabic"]:
        synonym_key = f"{lang}Synonyms"
        if synonym_key in consolidated_data:
            if not consolidated_data[synonym_key].get("Synonyms"):  # Empty list
                result["missingSynonyms"].append(lang)
    
    return result

def consolidate_UNTermResults(data, TEXT_TO_SEARCH):
    """
    Consolidate UNTERM results into a single dictionary based on specified term selection priorities.
    Main language keys are only filled from priority_1 and priority_2 matches.
    Other priority levels only populate synonym collections.
    
    Args:
        data: List of row data from search_term_and_extract_data
        TEXT_TO_SEARCH: The original search term
        
    Returns:
        dict: Consolidated dictionary with best terms for each language plus synonyms
    """
    # Initialize result dictionary with empty values
    result = {
        "English": "",
        "French": "",
        "Spanish": "",
        "Russian": "",
        "Chinese": "",
        "Arabic": "",
        "UNTerm_Source": None
    }
    
    # Initialize synonyms dictionaries for each non-English language
    for lang in ["French", "Spanish", "Russian", "Chinese", "Arabic"]:
        result[f"{lang}Synonyms"] = {
            "Synonyms": [],
            "Similar": []
        }
    
    # Track which languages have been filled in main entries
    filled_languages = set()
    
    # Process priority_1 and priority_2 to fill main language keys
    priority_functions_main = [
        # Priority 1: Exact match & UNHQ source
        lambda row: ("English" in row and 
                    any(term.lower() == TEXT_TO_SEARCH.lower() for term in row["English"].get("preferred", []) if term) and 
                    row["UNTerm_Source"]["source"] == "UNHQ"),
        
        # Priority 2: Exact match & specific sources
        lambda row: ("English" in row and 
                    any(term.lower() == TEXT_TO_SEARCH.lower() for term in row["English"].get("preferred", []) if term) and 
                    row["UNTerm_Source"]["source"] in ["UNON", "UNEP", "UNOG"])
    ]
    
    # Fill main language fields using only priority 1 and 2
    for priority_func in priority_functions_main:
        if len(filled_languages) == len(result) - 1:  # All language fields filled (-1 for UNTerm_Source)
            break
            
        for row in data:
            if priority_func(row):
                # This row matches priority 1 or 2 - fill main language fields
                for lang in ["English", "French", "Spanish", "Russian", "Chinese", "Arabic"]:
                    if lang in filled_languages:
                        continue
                        
                    if lang in row:
                        # First try preferred terms
                        if row[lang].get("preferred"):
                            result[lang] = row[lang]["preferred"][0]
                            filled_languages.add(lang)
                        # Then try admitted terms
                        elif row[lang].get("admitted"):
                            result[lang] = row[lang]["admitted"][0]
                            filled_languages.add(lang)
                
                # Record source info if we haven't already and at least one language was filled
                if not result["UNTerm_Source"] and filled_languages:
                    result["UNTerm_Source"] = row["UNTerm_Source"]
    
    # Define all priority check functions (for collecting synonyms)
    priority_functions_all = [
        # Priority 1 (same as above)
        lambda row: ("English" in row and 
                    any(term.lower() == TEXT_TO_SEARCH.lower() for term in row["English"].get("preferred", []) if term) and 
                    row["UNTerm_Source"]["source"] == "UNHQ"),
        
        # Priority 2 (same as above)
        lambda row: ("English" in row and 
                    any(term.lower() == TEXT_TO_SEARCH.lower() for term in row["English"].get("preferred", []) if term) and 
                    row["UNTerm_Source"]["source"] in ["UNON", "UNEP", "UNOG"]),
        
        # Priority 3: Contains search term & UNHQ source
        lambda row: ("English" in row and 
                    any(TEXT_TO_SEARCH.lower() in term.lower() for term in row["English"].get("preferred", []) if term) and 
                    row["UNTerm_Source"]["source"] == "UNHQ"),
        
        # Priority 4: Contains search term & (specific sources OR environment tags)
        lambda row: ("English" in row and 
                    any(TEXT_TO_SEARCH.lower() in term.lower() 
                        for term_type in ["preferred", "admitted"] 
                        for term in row["English"].get(term_type, []) if term) and
                    (row["UNTerm_Source"]["source"] in ["UNON", "UNEP", "UNOG"] or
                     any(("Environment" in tag or "UNEP" in tag) 
                         for tag in row["UNTerm_Source"].get("tags", [])))),
        
        # Priority 5: Any exact match
        lambda row: ("English" in row and 
                    any(term.lower() == TEXT_TO_SEARCH.lower() 
                        for term_type in ["preferred", "admitted"] 
                        for term in row["English"].get(term_type, []) if term))
    ]
    
    # Collect synonyms from all rows based on priority levels
    for priority_idx, priority_func in enumerate(priority_functions_all, 1):
        for row in data:
            if priority_func(row):
                # For priority 1-2, collect admitted terms as synonyms
                if priority_idx <= 2:
                    for lang in ["French", "Spanish", "Russian", "Chinese", "Arabic"]:
                        if lang in row:
                            # Add admitted terms as synonyms (excluding the main term)
                            for term in row[lang].get("admitted", []):
                                if term and term != result[lang] and term not in result[f"{lang}Synonyms"]["Synonyms"]:
                                    result[f"{lang}Synonyms"]["Synonyms"].append(term)
                                    
                # For priority 3-5, collect all terms as similar
                else:
                    for lang in ["French", "Spanish", "Russian", "Chinese", "Arabic"]:
                        if lang in row:
                            # Collect both preferred and admitted as similar terms
                            for term_type in ["preferred", "admitted"]:
                                for term in row[lang].get(term_type, []):
                                    if (term and term != result[lang] and 
                                        term not in result[f"{lang}Synonyms"]["Similar"] and
                                        term not in result[f"{lang}Synonyms"]["Synonyms"]):
                                        result[f"{lang}Synonyms"]["Similar"].append(term)
    
    return result



def queryFAOTerm(TEXT_TO_SEARCH):
    """
    Queries the FAO Term database for the given text and retrieves search results.
    Args:
        TEXT_TO_SEARCH (str): The text to search for in the FAO Term database.
    Returns:
        list: A list of search results, where each result is a list containing:
            - term (str): The term found.
            - entryID (str): The entry ID of the term.
            - isEnglishObsolete (bool): Whether the English term is obsolete.
            - language (str): The language of the term.
            - subject (str): The subject category of the term.
            - collection (str): The collection category of the term.
    Raises:
        Exception: If an error occurs during the web scraping process.
    """
    # Create a new directory for the user data
    user_data_dir = "/tmp/chrome_user_data"
    os.makedirs(user_data_dir, exist_ok=True)

    # Set up Chrome options for Google Colab
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument(f'--user-data-dir={user_data_dir}')
    options.add_argument('--profile-directory=Profile 3')

    # Initialize the WebDriver
    driver = webdriver.Chrome(options=options)

    tableHTML = False
    tableMarkDown = False

    try:
        # Open the website
        driver.get("https://faoterm.fao.org/index.html?language=en")

        # Find the search box and enter the search query
        search_box = driver.find_element(By.ID, "searchBox")
        search_box.send_keys(TEXT_TO_SEARCH)
        search_box.send_keys(Keys.RETURN)

        # Wait for the results to load (adjust the wait time if necessary)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "searchResultTable"))
        )
        time.sleep(5)  # Additional wait time to ensure all results are loaded

        # Get all available search results
        results = []
        i = 0
        while True:
            try:
                result_row = driver.find_element(By.ID, f"searchResultRow_{i}")
                term_hidden_link = result_row.find_element(By.NAME, "searchResHiddenLink")
                term = term_hidden_link.get_attribute("alt")
                term_cell = result_row.find_element(By.CLASS_NAME, "searchResultLink")
                entryID = term_cell.get_attribute("alt")
                isEnglishObsolete = bool(term_cell.find_elements(By.CLASS_NAME, "obsoleteTermLabel"))
                language = result_row.find_element(By.CLASS_NAME, "langColumn").text
                subject = result_row.find_element(By.CLASS_NAME, "subject").text
                collection = result_row.find_element(By.CLASS_NAME, "collColumn").text
                results.append([term, entryID, isEnglishObsolete, language, subject, collection])
                i += 1
            except Exception as e:
                break

        # Generate HTML and Markdown tables if results are found
        avoid = False
        if avoid:
            tableHTML = "<table><tr><th>Term</th><th>Entry ID</th><th>isEnglishObsolete</th><th>Language</th><th>Subject</th><th>Collection</th></tr>"
            tableMarkDown = "| Term | Entry ID | isEnglishObsolete | Language | Subject | Collection |\n|------|----------|------------------|----------|---------|------------|\n"
            for result in results:
                tableHTML += f"<tr><td>{result[0]}</td><td>{result[1]}</td><td>{result[2]}</td><td>{result[3]}</td><td>{result[4]}</td><td>{result[5]}</td></tr>"
                tableMarkDown += f"| {result[0]} | {result[1]} | {result[2]} | {result[3]} | {result[4]} | {result[5]} |\n"
            tableHTML += "</table>"

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        # Close the WebDriver
        driver.quit()

    return results

def getFAOtermsByEntry(entryID: str, getMetadata=True) -> dict:
    # Create a new directory for the user data
    user_data_dir = "/tmp/chrome_user_data"
    os.makedirs(user_data_dir, exist_ok=True)

    # Set up Chrome options for Google Colab
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument(f'--user-data-dir={user_data_dir}')
    options.add_argument('--profile-directory=Profile 3')

    # Initialize the WebDriver
    driver = webdriver.Chrome(options=options)

    data = {
        "entryID": entryID,
        "Subject": "",
        "Status": "", "Category": "", "MetadataSource": "", "Reliability": ""
    }

    try:
        # Open the entry detail page
        driver.get(f"https://faoterm.fao.org/viewEntry.html?entryId={entryID}")

        # Wait for the entry detail table to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "entryDetailTable"))
        )

        # Get the metadata if required
        if getMetadata:
            metadata_table = driver.find_element(By.ID, "entryDetailTable")
            try:
                data["Subject"] = metadata_table.find_element(By.XPATH, ".//th[contains(text(), 'Subject')]/span").text.strip()
            except:
                print("Subject not found")
            try:
                data["Status"] = metadata_table.find_element(By.XPATH, ".//th[contains(text(), 'Status')]/span").text.strip()
            except:
                print("Status not found")
            try:
                data["MetadataSource"] = metadata_table.find_element(By.XPATH, ".//th[contains(text(), 'Source') and @class='lastColumn']/span").text.strip()
            except:
                print("Source not found")
            try:
                data["Category"] = metadata_table.find_element(By.XPATH, ".//th[contains(text(), 'Category')]/span").text.strip()
            except:
                print("Category not found")
            try:
                data["Reliability"] = metadata_table.find_element(By.XPATH, ".//th[contains(text(), 'Reliability')]/span").text.strip()
            except:
                print("Reliability not found")

        # Get the term details for each language
        languages = {
            "AR": {"panel_id": "AR_panel", "term_source_texts": ["مصدر المصطلح"], "remarks_texts": ["ملاحظات"]},
            "EN": {"panel_id": "EN_panel", "term_source_texts": ["Term source"], "remarks_texts": ["Remarks"]},
            "ES": {"panel_id": "ES_panel", "term_source_texts": ["Fuente del término"], "remarks_texts": ["Observaciones"]},
            "RU": {"panel_id": "RU_panel", "term_source_texts": ["Источник (термина)"], "remarks_texts": ["Примечания"]},
            "ZH": {"panel_id": "ZH_panel", "term_source_texts": ["术语来源"], "remarks_texts": ["备注"]},
            "FR": {"panel_id": "FR_panel", "term_source_texts": ["Source du terme"], "remarks_texts": ["Remarques"]},
            "PT": {"panel_id": "PT_panel", "term_source_texts": ["Term source"], "remarks_texts": ["Remarks"]}
        }

        for lang, details in languages.items():
            try:
                panel = driver.find_element(By.ID, details["panel_id"])
                terms = panel.find_elements(By.CLASS_NAME, "termName")
                term_names = [term.text for term in terms]
                data[f"{lang}Term"] = "; ".join(term_names)

                # Get the term sources for each term name
                term_sources = []
                for term in terms:
                    sources = []
                    for term_source_text in details["term_source_texts"]:
                        try:
                            source_elements = term.find_elements(By.XPATH, f".//following-sibling::h4[text()='{term_source_text}']/following-sibling::p")
                            while source_elements:
                                sources.extend([source.text for source in source_elements])
                                source_elements = source_elements[0].find_elements(By.XPATH, "./following-sibling::p")
                        except:
                            pass
                    term_sources.append((term.text, sources))
                data[f"{lang}Source"] = str(term_sources)

                # Get the related terms
                try:
                    related_terms = panel.find_elements(By.XPATH, ".//p[starts-with(@name, 'relatedTerm')]/a[@class='relatedTerm']")
                    related_terms_list = []
                    for term in related_terms:
                        onclick_attr = term.get_attribute('onclick')
                        term_id = onclick_attr.split("'")[1]
                        term_lang = onclick_attr.split("'")[3]
                        related_terms_list.append(f"{term.text} | ('{term_id}','{term_lang}')")
                    data[f"{lang}Related"] = str(related_terms_list)
                except:
                    pass

                # Get the remarks
                remarks_list = []
                for remarks_text in details["remarks_texts"]:
                    try:
                        remarks_elements = panel.find_elements(By.XPATH, f".//h4[text()='{remarks_text}']/following-sibling::p")
                        remarks_list.extend([remark.text for remark in remarks_elements])
                    except:
                        pass
                data[f"{lang}Remarks"] = "; ".join(remarks_list)

            except Exception as e:
                print(f"An error occurred while processing {lang}: {e}")

    except Exception as e:
        print(f"An error occurred: {e}")
        print(driver.page_source)  # Print the source HTML code of the page

    finally:
        # Close the WebDriver
        driver.quit()

    return data