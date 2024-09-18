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

def start_process(xml_file):
    driver = setup()  # Setup WebDriver
    if driver:
        articles_data = extract_articles_from_xml(xml_file, driver)
        write_to_json(articles_data, 'articles.json')
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
        h4_tag.string = strong_tag.get_text()
        strong_tag.replace_with(h4_tag)
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

    return articles_data

def extract_article_data(driver):
    """Extracts article details like title, body, etc. from the current webpage."""
    try:
        # Extract title
        title_element = driver.find_element(By.CSS_SELECTOR, 'h2.entry-title')
        title = title_element.text.strip() if title_element else 'No title found'
        print(f"Title found: {title}")

        author_selectors = [
            'xpath:/html/body/div[1]/main/div/section/article/div[3]/p[1]/strong',
            'xpath:/html/body/div[1]/main/div/section/article/div[3]/p[1]/b',
            'xpath:/html/body/div[1]/main/div/section/article/div[2]/p[1]/strong',
            'xpath:/html/body/div[1]/main/div/section/article/div[3]/p[2]/strong',
            'css:#post > div.post-content > p:nth-child(1) > strong',
            'css:#post-4158 > div.post-content > p:nth-child(1) > strong'
        ]

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
                    break  # Stop loop once an author is found
            except NoSuchElementException:
                print(f"Author not found at {selector}, trying next...")

        author = author if author else 'No author found'
        print(f"Author found: {author}")

        # Extract date and convert it
        date_element = driver.find_element(By.XPATH, '/html/body/div[1]/main/div/section/article/div[1]/div/div/span[3]')
        date = date_element.text.strip() if date_element else 'No date found'
        formatted_date = convert_date(date)
        print(f"Date found: {formatted_date}")

        # Extract body HTML
        body_element = driver.find_element(By.CLASS_NAME, 'post-content')
        body_html = body_element.get_attribute('outerHTML') if body_element else ''
        wrapped_body = wrap_strong_with_h4(body_html)  # Wrap <strong> tags with <h4> tags
            # Remove the line containing the author's name
        soup = BeautifulSoup(wrapped_body, 'html.parser')
        for p_tag in soup.find_all('p'):
            if author in p_tag.get_text():
                p_tag.decompose()  # Remove the paragraph containing the author text

        cleaned_body = str(soup)  # Convert back to HTML string
        print(f"wrapped body HTML saved")
        # Prepare data for JSON
        article_data = {
            'title': title,
            'author': author,
            'date': formatted_date,
            'body': cleaned_body
        }

        return article_data

    except Exception as e:
        print(f"Error extracting data: {e}")
        return None

# Start the process
start_process('linked_lit_review.xml')
