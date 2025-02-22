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

def track_execution():
    # Record the start time
    start_time = time.time()

    # Your code goes here
    # For example, a sample process that takes time
    for i in range(1000000):
        pass

    # Record the end time
    end_time = time.time()

    # Calculate the total time taken
    execution_time = end_time - start_time
    print(f"Execution took {execution_time} seconds.")

def start_process(xml_file):
    driver = setup()  # Setup WebDriver
    # articles_data = extract_articles_from_xml(xml_file, driver)
    articles_data = extract_article_data(driver)
    # write_to_json(articles_data, 'articles.json')
    teardown(driver)

def setup():
    try:
        # Initialize Chrome WebDriver
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run in headless mode
        chrome_options.add_argument("--disable-images")
        driver = webdriver.Chrome(options=chrome_options)
        print("WebDriver initialized.")

        url = 'https://aggietranscript.ucdavis.edu/mitofusin-2-as-a-mammalian-er-mitochondria-tether-a-review/'
        driver.get(url)

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
        h4_tag.string = strong_tag.get_text().replace(':', '').strip() #removes the colon inside
        strong_tag.replace_with(h4_tag)
                # Check for a <br/> tag immediately after the <h4> tag and remove it
        next_tag = h4_tag.find_next_sibling()
        if next_tag and next_tag.name == 'br':
            next_tag.extract()
    return str(soup)


def normalize_html(html_content):
    """Converts outerHTML to normalized HTML and returns it as a string."""
    # Parse the HTML content
    soup = BeautifulSoup(html_content, 'html.parser')

    # Convert BeautifulSoup object back to a string
    normalized_html = str(soup.prettify())  # Use prettify() to ensure well-formatted HTML

    return normalized_html

def inject_html(driver, element, html_string):
    # Use JavaScript to set the innerHTML of the target element
    driver.execute_script("arguments[0].innerHTML = arguments[1];", element, html_string)


def extract_articles_from_xml(xml_file, driver):
    """Extracts articles from an XML file and returns a list of article dictionaries."""
    tree = ET.parse(xml_file)
    root = tree.getroot()
    articles_data = []

    # Loop through each link in the XML file
    for link in root.findall('.//link'):
        url = link.text
        driver.get(url)
        article_data = extract_article_data(driver)  # Extract data for each article
        articles_data.append(article_data)

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

def remove_the_p_tags(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
     # Find all <p> tags and remove those that contain only a non-breaking space
    for p in soup.find_all('p'):
        if p.get_text(strip=True) or p.get_text() == '\u00a0': # check if the paragraph is empty or contains only whitespace
            p.decompose()  # removes the tag completely
    return str(soup)
    # html = html.replace('<p>\u00a0</p>', '')  # Specifically target the non-breaking space
    # return html

def extract_article_data(driver):
    try:
        title_element = driver.find_element(By.CSS_SELECTOR, 'h2.entry-title')
        title = title_element.text.strip() if title_element else 'No title found'
        print(f"Title found: {title}")

        author_selectors = [
            'xpath:/html/body/div[1]/main/div/section/article/div[3]/p[1]/strong',
            'xpath:/html/body/div[1]/main/div/section/article/div[3]/p[1]/b',
            'xpath:/html/body/div[1]/main/div/section/article/div[2]/p[1]/strong',
            'css:#post > div.post-content > p:nth-child(1) > strong',
            'css:#post-4158 > div.post-content > p:nth-child(1) > strong',
            'xpath:/html/body/div[1]/main/div/section/article/div[3]/p[2]/strong'
        ]

        author = find_author(driver, author_selectors)
        print(f"Author found: {author}")

        date_element = driver.find_element(By.XPATH, '/html/body/div[1]/main/div/section/article/div[1]/div/div/span[3]')
        date = date_element.text.strip() if date_element else 'No date found'
        formatted_date = convert_date(date)
        print(f"date is {formatted_date}")

        body_element = driver.find_element(By.CLASS_NAME, 'post-content')
        body_html = body_element.get_attribute('outerHTML') if body_element else ''
        no_bList = remove_b_tags_in_li(body_html)
        no_pTags = remove_the_p_tags(no_bList)
        # print(no_bList)
        body_subCaps = capitalize_in_b_tags(no_bList)
        wrapped_body = wrap_strong_with_h4(body_subCaps)  # Wrap <strong> tags with <h4> tags
        # def move_author_before_ol(html_content, author_notes):
        #     # Parse the HTML content
        #     soup = BeautifulSoup(html_content, 'html.parser')

        #     # Find the paragraph containing any of the author's notes inside <strong> or <b> tags
        #     author_paragraph = None
        #     for tag in soup.find_all(['strong', 'b']):  # Search for both <strong> and <b> tags
        #         # Check if any of the author_note strings are in the text
        #         if any(note in tag.get_text() for note in author_notes):
        #             author_paragraph = tag.find_parent('p')  # Assuming it's wrapped in a <p> tag
        #             break

        #     if author_paragraph:
        #         # Find the first <ol> tag
        #         ol_tag = soup.find('ol')
        #         if ol_tag:
        #             # Insert the author paragraph before the <ol> tag
        #             ol_tag.insert_before(author_paragraph)

        #     # Return the modified HTML
        #     return str(soup)
        # no_authorsNote = move_author_before_ol(wrapped_body, ["Author's Note:", "authors note:", "Author's note:","Author's Note", "Authors Note", ])
        # Remove the line containing the author's name
        soup = BeautifulSoup(wrapped_body, 'html.parser')
        # for p_tag in soup.find_all('p'):
        #     if author in p_tag.get_text():
        #         p_tag.decompose()  # Remove the paragraph containing the author text
        #         print(author)
        # cleaned_body = str(soup)
            # Find all <p>, <strong>, and <br> tags
        for tag in soup.find_all(['p', 'strong']):
            # Check if author is in the text of the <p> or <strong> tag
            if author in tag.get_text():
                tag.decompose()  # Remove the tag containing the author text
                print(f"Removed tag for author: {author}")

        # Additionally check for <br> tags
        for br_tag in soup.find_all('br'):
            previous_sibling = br_tag.find_previous_sibling()
            if previous_sibling and author in previous_sibling.get_text():
                previous_sibling.decompose()  # Remove the previous sibling if it contains the author
                print(f"Removed tag for author: {author} (related to <br>)")

        cleaned_body = str(soup)  # Return modified HTML as string
        # cleaned_body = move_author_before_ol(no_author, author)

        # cleaned_body = str(soup)  # Convert back to HTML string
        # Prepare data for JSON file
        article_data = {
            'title': title,
            'author': author,
            'date': formatted_date,
            'body': cleaned_body
        }

        write_to_json(article_data, 'article.json')

    except Exception as e:
        print(f"Error extracting data: {e}")

# Start the process
start_process('linked_lit_review.xml')
track_execution()
