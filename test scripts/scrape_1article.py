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

        url = 'https://aggietranscript.ucdavis.edu/gene-editing-invasive-species-out-of-new-zealand/'
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
    # Strip 'th', 'st', 'nd', 'rd' suffixes from the day
    date_str = date_str.replace('th', '').replace('st', '').replace('nd', '').replace('rd', '')

    # Convert the string to a datetime object
    date_obj = datetime.strptime(date_str, '%B %d, %Y')

    # Format the date as 'MM/DD/YYYY'
    formatted_date = date_obj.strftime('%m/%d/%Y')

    return formatted_date


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

        date_element = driver.find_element(By.XPATH, '/html/body/div[1]/main/div/section/article/div[1]/div/div/span[3]')
        date = date_element.text.strip() if date_element else 'No date found'
        formatted_date = convert_date(date)
        print(f"date is {formatted_date}")

        body_element = driver.find_element(By.CLASS_NAME, 'post-content')
        body_html = body_element.get_attribute('outerHTML') if body_element else ''
        wrapped_body = wrap_strong_with_h4(body_html)  # Wrap <strong> tags with <h4> tags
        # Remove the line containing the author's name
        soup = BeautifulSoup(wrapped_body, 'html.parser')
        for p_tag in soup.find_all('p'):
            if author in p_tag.get_text():
                p_tag.decompose()  # Remove the paragraph containing the author text

        cleaned_body = str(soup)  # Convert back to HTML string
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
