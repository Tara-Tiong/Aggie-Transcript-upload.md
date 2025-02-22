from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import json
import time
from bs4 import BeautifulSoup
from datetime import datetime
import xml.etree.ElementTree as ET
from selenium.common.exceptions import NoSuchElementException
import re

start_time = time.time()
def start_process(xml_file):
    driver = setup()  # Setup WebDriver
    if driver:
        articles_data = extract_articles_from_xml(xml_file, driver)
        write_to_json(articles_data, new_json_file)
        teardown(driver)

def setup():
    try:
        # Initialize Chrome WebDriver
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run in headless mode
        chrome_options.add_argument("--disable-images")
        driver = webdriver.Chrome(options=chrome_options)
        print("WebDriver initialized.")

        # url = 'https://aggietranscript.ucdavis.edu/gut-feeling-how-does-modulation-of-gut-microbiome-affect-depression-pathophysiology-and-status/'
        # driver.get(url)

        # Wait for the page to load
        time.sleep(5)  # Increase if the page is slow to load

        return driver
    except Exception as e:
        print(f"Error during setup: {e}")
        return None

def teardown(driver):
    if driver:
        driver.quit()
        print("WebDriver closed.")

def convert_date(date_str):
   try:
        # Remove any 'th', 'st', 'nd', 'rd' suffixes from the day
        date_str = date_str.replace('th', '').replace('st', '').replace('nd', '').replace('rd', '')

        # Attempt to convert to a datetime object
        date_obj = datetime.strptime(date_str, '%B %d, %Y')

        # Format as 'MM/DD/YYYY'
        formatted_date = date_obj.strftime('%m/%d/%Y')
        return formatted_date
   except ValueError as e:
        # Log the error
        print(f"Error converting date: {e}. Original date string: {date_str}")

        # Attempt to correct common typos, e.g., 'Augu' -> 'August'
        corrections = {
            'Augu': 'August',
            'Sept': 'September',  # Sometimes 'Sept' is used instead of 'September'
            'Octo': 'October',    # Example typo
        }

        # Look for and fix common typos in month names
        for typo, correct in corrections.items():
            if typo in date_str:
                date_str = date_str.replace(typo, correct)
                break  # Apply the first fix we find and try again

        # Try parsing the corrected date
        try:
            date_obj = datetime.strptime(date_str, '%B %d, %Y')
            formatted_date = date_obj.strftime('%m/%d/%Y')
            return formatted_date
        except ValueError as e:
            # Log the failure to convert even after corrections
            print(f"Failed to convert date after correction: {e}. Final date string: {date_str}")
            return "Invalid date"  # Fallback return for badly formatted dates

def capitalize_in_b_tags(html):
    """
    Finds text within <b> tags and ensures only the first letter is capitalized,
    making the rest lowercase if it's fully uppercase.
    """
    # Parse the HTML content
    soup = BeautifulSoup(html, 'html.parser')

    # Function to capitalize the first letter and lowercase the rest
    def capitalize(match):
        matched_str = match.group(0)
        return matched_str[0].upper() + matched_str[1:].lower()

    # Find all <b> tags and process the text inside them
    for b_tag in soup.find_all('b'):
        if b_tag.string:  # Ensure there is text inside the <b> tag
            # Replace fully uppercase words with capitalized first letter versions
            modified_text = re.sub(r'\b[A-Z]{2,}\b', capitalize, b_tag.string)
            b_tag.string.replace_with(modified_text)  # Update the content in the <b> tag
            print(modified_text)

    # Return the modified HTML as a string
    return str(soup)

def write_to_json(data, file_path):
    """Writes data to a JSON file."""
    try:
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=4)
        print(f"Data successfully written to {file_path}")
    except Exception as e:
        print(f"Error writing to JSON: {e}")

def wrap_strong_with_h4(html):
    """Wrap all <strong> tags with <h4> tags."""
    soup = BeautifulSoup(html, 'html.parser')
    for strong_tag in soup.find_all(['strong','b']):
        h4_tag = soup.new_tag('h4')
        h4_tag.string = strong_tag.get_text().replace(':', ' ').strip() #removes the colon inside
        strong_tag.replace_with(h4_tag)
                 # Check for a <br/> tag immediately after the <h4> tag and remove it
        next_tag = h4_tag.find_next_sibling()
        if next_tag and next_tag.name == 'br':
            next_tag.extract()
    return str(soup)

def extract_articles_from_xml(xml_file, driver):
    """Extracts articles from an XML file and returns a dictionary of article dictionaries."""
    try:
        # Parse the XML file
        tree = ET.parse(xml_file)
        root = tree.getroot()
    except ET.ParseError:
        print("Error parsing XML file. Please check the structure.")
        return {}

    articles_data = {}

    # Loop through each link in the XML file
    for i, link in enumerate(root.findall('.//link'), start=1):
        url = link.text
        if not url:
            print("No URL found in <link> tag.")
            continue
        print(f"Processing URL: {url}")  # Debugging print statement

        try:
            # Navigate to the URL
            driver.get(url)
        except Exception as e:
            print(f"Error loading the page at {url}: {e}")
            continue

        # Extract article data
        article_data = extract_article_data(driver)

        if article_data:
            articles_data[f'article_{i}'] = article_data
        else:
            print(f"No article data found for {url}")

        # # Only add articles with the tag "Health and Medicine"
        # if article_data and article_data.get('tag') == "Biology":
        #     articles_data[f'article_{i}'] = article_data
        # else:
        #     print(f"Article at {url} skipped; tag did not match 'Biology'.")

         # Only add articles with the tag "Health and Medicine" and no other tags
        # if articles_data:
        #     articles_data[f'article_{i}'] = articles_data
        # else:
        #     print(f"Article at {url} skipped; tag did not match 'Health and Medicine' criteria.")

    return articles_data

def find_author(driver, author_selectors):
    author = None
    # Iterate through the list of selectors to find the author
    for selector in author_selectors:
        method, path = selector.split(':', 1)
        try:
            if method == 'xpath':
                author_element = driver.find_element(By.XPATH, path)
            elif method == 'css':
                author_element = driver.find_element(By.CSS_SELECTOR, path)

            author = author_element.text.strip()
            if author:
                 # Remove "by" or "By" from the author string
                author = author.replace("by ", "").replace("By ", "").strip()
                break  # Stop loop once an author is found
        except NoSuchElementException:
            print(f"Author not found at {selector}, trying next...")

    return author if author else 'No author found'

def remove_b_tags_in_li(html_content):
    # Parse the HTML content
    soup = BeautifulSoup(html_content, 'html.parser')

    # Find all <li> tags with the style "font-weight: 400"
    li_tags = soup.find_all('li', style="font-weight: 400")

    # Loop through each <li> tag
    for li in li_tags:
        # Find all <b> tags within the <li>
        b_tags = li.find_all('b')
        for b in b_tags:
            b.unwrap()  # Remove the <b> tag, keeping the text

    # Return the modified HTML
    return str(soup)

def extract_article_data(driver):
    """Extracts article details like title, body, etc. from the current webpage."""
    try:
        # Extract title
        title_element = driver.find_element(By.CSS_SELECTOR, 'h2.entry-title')
        title = title_element.text.strip() if title_element else 'No title found'
        print(f"Title found: {title}")

        author_selectors = [
            'xpath:/html/body/div[1]/main/div/section/article/div[3]/p[1]',
            'xpath:/html/body/div[1]/main/div/section/article/div[2]/p[1]',
            'xpath:/html/body/div[1]/main/div/section/article/div[3]/p[1]/strong',
            'xpath:/html/body/div[1]/main/div/section/article/div[3]/p[1]/b',
            'xpath:/html/body/div[1]/main/div/section/article/div[2]/p[1]/strong',
            'xpath:/html/body/div[1]/main/div/section/article/div[3]/p[2]/strong',
            'xpath:/html/body/div[1]/main/div/section/article/div[3]/p[1]/span',
            'xpath:/html/body/div[1]/main/div/section/article/div[3]/p[1]/span',
            'css:#post-191 > div.post-content > p:nth-child(1)',
            'css:#post > div.post-content > p:nth-child(1) > strong',
            'css:#post-4158 > div.post-content > p:nth-child(1) > strong',
            'css:#post-3731 > div.post-content > p:nth-child(1) > span',
            'css:#post-4009 > div.post-content > p:nth-child(1) > span'
        ]

        author = find_author(driver, author_selectors)
        print(f"Author found: {author}")

        # Extract date and convert it
        date_element = driver.find_element(By.XPATH, '/html/body/div[1]/main/div/section/article/div[1]/div/div/span[3]')
        date = date_element.text.strip() if date_element else 'No date found'
        formatted_date = convert_date(date)
        print(f"Date found: {formatted_date}")

        # Extract body HTML
    #     body_element = driver.find_element(By.CLASS_NAME, 'post-content')
    #     body_html = body_element.get_attribute('outerHTML') if body_element else ''
    # #    wrapped_body = wrap_strong_with_h4(body_html)  # Wrap <strong> tags with <h4> tags
    #     body_subCaps = capitalize_in_b_tags(body_html)
    #     wrapped_body = wrap_strong_with_h4(body_subCaps)
    #         # Remove the line containing the author's name
    #     soup = BeautifulSoup(wrapped_body, 'html.parser')
    #     for p_tag in soup.find_all('p'):
    #         if author in p_tag.get_text():
    #             p_tag.decompose()  # Remove the paragraph containing the author text

    #     cleaned_body = str(soup)  # Convert back to HTML string
    #     print(f"wrapped body HTML saved")

        body_element = driver.find_element(By.CLASS_NAME, 'post-content')
        body_html = body_element.get_attribute('outerHTML') if body_element else ''
        no_bList = remove_b_tags_in_li(body_html)
        # print(no_bList)
        body_subCaps = capitalize_in_b_tags(no_bList)
        wrapped_body = wrap_strong_with_h4(body_subCaps)  # Wrap <strong> tags with <h4> tags
        soup = BeautifulSoup(wrapped_body, 'html.parser')
        for tag in soup.find_all(['p', 'strong','span']):
            # Check if author is in the text of the <p> or <strong> tag
            if author in tag.get_text():
                tag.decompose()  # Remove the tag containing the author text
                print(f"Removed tag for author: {author}")

        # Additionally check for <br> tags
        for br_tag in soup.find_all(['br','p','span']):
            previous_sibling = br_tag.find_previous_sibling()
            if previous_sibling and author in previous_sibling.get_text():
                previous_sibling.decompose()  # Remove the previous sibling if it contains the author
                print(f"Removed tag for author: {author} (related to <br>)")

        # removes empty <p> tags
        for p in soup.find_all('p'):
            if p.get_text(strip=True)==' ': # check if the paragraph is empty or contains only whitespace
                p.decompose()  # removes the tag completely

        cleaned_body = str(soup)  # Return modified HTML as string

    #     # Category Tags
    #     tag_element = driver.find_element(By.LINK_TEXT, 'Biology')
    #     tag = tag_element.text.strip() if tag_element else 'Tag not found'

    # # Check if the tag is "Health and Medicine"
    #     if tag == "Biology":
    #         print(f"Tag found: {tag}")
           # Extract all tags (assuming tags are contained in <a> elements within a specific container)

        # tag_elements = driver.find_elements(By.LINK_TEXT, 'Health and Medicine')
        # tags = [tag.text.strip() for tag in tag_elements if tag.text.strip()]

        # # Check if there is exactly one tag and it matches "Health and Medicine"
        # if len(tags) == 1 and tags[0] == "Health and Medicine":
        #     print(f"Valid tag found: {tags[0]}")

        valid_tags = [
                    'Campus News and Reports', 'Health and Medicine', 'Biology', 'Microbiology', 'News', 'Cell Biology',
                    'Biochemistry', 'Neurobiology', 'Science and Society',
                    'Technology', 'Genetics', 'Literature Review', 'Art'
                ]

                # Initialize an empty list to collect found tags
        tags = []

        # Use By.LINK_TEXT to check for each tag individually
        for tag_text in valid_tags:
            try:
                tag_element = driver.find_element(By.LINK_TEXT, tag_text)
                tags.append(tag_element.text.strip())
            except:
                continue  # Skip if the tag is not found

        # Check if there is exactly one valid tag in the list of tags
        if len(tags) == 1:
            print(f"Valid tag found: {tags[0]}")
            # Prepare data for JSON
            article_data = {
                'title': title,
                'author': author,
                'date': formatted_date,
                'body': cleaned_body,
                'tag': tags[0]
            }

            return article_data

        else:
            print(f"Skipping article, tag is: {tag}")
            return None  # Return None if the tag does not match

    except Exception as e:
        print(f"Error extracting data: {e}")
        return None

# Start the process
new_json_file = 'science_and_society.json'
list_of_articles = 'xml files/science_and_society.xml'
start_process(list_of_articles)
end_time = time.time()

# Calculate the total time taken
execution_time = end_time - start_time
print(f"Execution took {execution_time} seconds.")
