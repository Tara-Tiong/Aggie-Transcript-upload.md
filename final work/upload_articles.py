from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import json
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
import time

# article category
json_dictionary = 'science_and_society.json'

start_time = time.time()
#selector values for categories -> Secondary categories
biochemistry = "#edit-field-sf-article-secondary-cats > option:nth-child(12)"
environment = "#edit-field-sf-article-secondary-cats > option:nth-child(17)"
genetics = "#edit-field-sf-article-secondary-cats > option:nth-child(19)"
neurobiology = "#edit-field-sf-article-secondary-cats > option:nth-child(22)"
cell_biology = "#edit-field-sf-article-secondary-cats > option:nth-child(15)"
microbiology = "#edit-field-sf-article-secondary-cats > option:nth-child(21)"
health_and_medicine = "#edit-field-sf-article-secondary-cats > option:nth-child(20)"
technology = "#edit-field-sf-article-secondary-cats > option:nth-child(24)"
biology = "#edit-field-sf-article-secondary-cats > option:nth-child(13)"

# selector values -> primary
literature_reviews = "13491"
news = "13506"
campus_news = "13456"
book_review= "13451" #  reviews > book review (on WP)
science_and_society = "13526"

primary_category_selection = science_and_society

def load_config(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

def test_uc_davis_login():
    driver = setup()

    print("Driver opened")

    # Click on CAS login button
    cas_loginButton = driver.find_element(By.CLASS_NAME, "btn--primary").click()
    # sleep(2)

    # Enter username and password
    cas_username = driver.find_element(By.ID, "username")
    cas_username.send_keys('tytiong')  # Replace with actual username
    # sleep(2)

    cas_paraphrase = driver.find_element(By.ID, "password")
    cas_paraphrase.send_keys('TrashPassword6969')  # Replace with actual password
    # sleep(2)

    # Click secondary login button
    cas_secLoginButton = driver.find_element(By.ID, "submit").click()
    sleep(10)

    # Click 'Yes' button if prompted
    cas_yesButton = driver.find_element(By.XPATH, "/html/body/div/div/div[1]/div/div[2]/div[3]/button").click()
    sleep(10)

    print("CAS login success")
    # teardown(driver)

    config = load_config(json_dictionary)
    # change the start_index of the article
    start_index = 2
    index = 1

    for article_key, article_data in config.items():
        if index >=start_index:
            print(f"PROCESSING ARTICLE {index} - {article_key}")
            launch_content(driver)
            sleep(10)
            add_content(driver, article_key, article_data)
            sleep(10)  # Adjust sleep time as needed
        index += 1

    # teardown(driver)
    teardown(driver)


def launch_content(driver):
    wait = WebDriverWait(driver, 10)  # Wait up to 10 seconds for elements

    # Load the content page
    # manage_toolbar = driver.find_element(By.ID, "toolbar-item-administration")
    # manage_toolbar.click()
    # sleep(2)
    print("launch content")
    content_tab = driver.find_element(By.ID, "toolbar-link-system-admin_content")
    content_tab.click()

    add_content_tab = driver.find_element(By.CSS_SELECTOR, "#block-claro-local-actions > ul > li > a")
    add_content_tab.click()

    under_article = driver.find_element(By.CLASS_NAME,"admin-item__link")
    under_article.click()

    print("Content has been launched successfully.")
    # driver.save_screenshot('add_content.png')
    # wait = WebDriverWait(driver, 30)  # Wait up to 10 seconds for elements



def add_content(driver, article_key, article_data):
    wait = WebDriverWait(driver, 10)  # Wait up to 10 seconds for elements
    print(f"Adding content for article: {article_key}")

    """Top Priority"""
    # main body
    title =  driver.find_element(By.ID, "edit-title-0-value")
    title.send_keys(article_data['title'])

    # enter author in byline
    byline = driver.find_element(By.ID, "edit-field-sf-article-by-line-0-value")
    byline.send_keys(article_data['author'])

    #choosing the format of body paragraph
    select = Select(driver.find_element(By.ID, "edit-body-0-format--2"))
    select.select_by_value("full_html")

    # type in body paragraph
    """after selecting FULL HTML"""
    body = driver.find_element(By.XPATH, "/html/body/div[2]/div/main/div[4]/div/form/div/div[1]/div/div[7]/div/div[2]/div/textarea")
    # driver.execute_script("arguments[0].innerHTML = arguments[1];", body, article_data['body'])
    body.send_keys(article_data['body'])
    sleep(10)

    #Article Categories
    categorizing_selectors = [
            'xpath:/html/body/div[2]/div/main/div[4]/div/form/div/div[2]/div/div/details[7]/summary',
            'xpath:/html/body/div[2]/div/main/div[4]/div/form/div/div[2]/div/div/details[8]',
            'css:#edit-categorizing > summary'
        ]

    categorizing = None
        # Iterate through the list of selectors to find the author
    for selector in categorizing_selectors:
        method, path = selector.split(':', 1)
        try:
            if method == 'xpath':
                categorizing_element = driver.find_element(By.XPATH, path)
                print('category: xpath selector')
            elif method == 'css':
                categorizing_element = driver.find_element(By.CSS_SELECTOR, path)
                print('category: css selector')
            categorizing = categorizing_element
            if categorizing:
                break  # Stop loop once an category is found
        except NoSuchElementException:
            print(f"Author not found at {selector}, trying next...")

    categorizing = categorizing if categorizing else 'No categorizing found'
    print(f"Author found: {categorizing}")
    categorizing.click()
    print('categorizing worked!!')

    #under categorizing -->  selects ARTICLE TYPE
    article_type = Select(driver.find_element(By.CSS_SELECTOR, "#edit-field-sf-article-type"))
    article_type.select_by_value("24906")

    #Authoring info which is where the date is found
    authoring_info = driver.find_element(By.CSS_SELECTOR, "#edit-author > summary")
    authoring_info.click()
    #date
    date = driver.find_element(By.CSS_SELECTOR, "#edit-created-0-value-date")
    date.send_keys(article_data['date'])

    # primary category for now is:
    primary_category = Select(driver.find_element(By.CSS_SELECTOR, "#edit-field-sf-article-category"))
    primary_category.select_by_value(primary_category_selection) #change if you need to select something else side bar

    #secondary category
    # secondary_category = driver.find_element(By.CSS_SELECTOR, health_and_medicine)
    # secondary_category.click()

    # uncheck the PUBLISHED box for tests
    un_publish = driver.find_element(By.XPATH, "/html/body/div[2]/div/main/div[4]/div/form/div/div[3]/div/div[2]/div/div/input")
    un_publish.click()

    save_article = driver.find_element(By.XPATH, "/html/body/div[2]/div/main/div[4]/div/form/div/div[3]/div/div[3]/input[1]")
    save_article.click()

    print(f"Article '{article_key}' added")
    sleep(10)

def setup():
    # Initialize Chrome WebDriver
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--disable-images")
    chrome_options.add_argument("--disable-extensions")
    driver = webdriver.Chrome(options=chrome_options)
    delay = 3 # seconds
    try:
        myElem = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.ID, 'IdOfMyElement')))
        print("Page is ready!")
    except TimeoutException:
        print("Loading took too much time!")

    # Navigate to the Aggie Transcript login page
    driver.get("https://aggietranscript.sf.ucdavis.edu/login")
    return driver

def teardown(driver):
    # Close the browser
    driver.quit()

# Run the login test
test_uc_davis_login()
end_time=time.time()
execution_time = end_time - start_time
print(f"Total execution time: {execution_time} seconds.")
