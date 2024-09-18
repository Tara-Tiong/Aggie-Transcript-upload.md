from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
import json

def load_config(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

def test_uc_davis_login():
    driver = setup()

    print("Driver opened")

    # Perform login actions
    cas_loginButton = driver.find_element(By.CLASS_NAME, "btn--primary").click()
    cas_username = driver.find_element(By.ID, "username")
    cas_username.send_keys('tytiong')  # Replace with actual username
    cas_paraphrase = driver.find_element(By.ID, "password")
    cas_paraphrase.send_keys('TrashPassword6969')  # Replace with actual password
    cas_secLoginButton = driver.find_element(By.ID, "submit").click()
    sleep(10)
    cas_yesButton = driver.find_element(By.XPATH, "/html/body/div/div/div[1]/div/div[2]/div[3]/button").click()
    sleep(10)

    print("CAS login success")

    config = load_config('articles.json')

    for article_key, article_data in config.items():
        launch_content(driver)
        add_content(driver, article_key, article_data)
        sleep(10)  # Adjust sleep time as needed

    teardown(driver)

def launch_content(driver):
    wait = WebDriverWait(driver, 10)  # Wait up to 10 seconds for elements

    print("launch content")
    content_tab = driver.find_element(By.ID, "toolbar-link-system-admin_content")
    content_tab.click()

    add_content_tab = driver.find_element(By.CSS_SELECTOR, "#block-claro-local-actions > ul > li > a")
    add_content_tab.click()

    under_article = driver.find_element(By.CLASS_NAME,"admin-item__link")
    under_article.click()

    print("Content has been launched successfully.")

def add_content(driver, article_key, article_data):
    wait = WebDriverWait(driver, 10)  # Wait up to 10 seconds for elements
    print(f"Adding content for article: {article_key}")

    # Top Priority
    title = driver.find_element(By.ID, "edit-title-0-value")
    title.send_keys(article_data['title'])

    byline = driver.find_element(By.ID, "edit-field-sf-article-by-line-0-value")
    byline.send_keys(article_data['author'])

    # Choosing the format of body paragraph
    select = Select(driver.find_element(By.ID, "edit-body-0-format--2"))
    select.select_by_value("full_html")

    # Type in body paragraph
    body = driver.find_element(By.XPATH, "/html/body/div[2]/div/main/div[4]/div/form/div/div[1]/div/div[7]/div/div[2]/div/textarea")
    body.send_keys(article_data['body'])

    # Article Categories
    categorizing = driver.find_element(By.CSS_SELECTOR, "#edit-categorizing > summary")
    categorizing.click()

    article_type = Select(driver.find_element(By.CSS_SELECTOR, "#edit-field-sf-article-type"))
    article_type.select_by_value("24906")  # Adjust if needed

    # Authoring info which is where the date is found
    authoring_info = driver.find_element(By.CSS_SELECTOR, "#edit-author > summary")
    authoring_info.click()

    # Date
    date = driver.find_element(By.CSS_SELECTOR, "#edit-created-0-value-date")
    date.send_keys(article_data['date'])

    # Primary category for now is:
    primary_category = Select(driver.find_element(By.CSS_SELECTOR, "#edit-field-sf-article-category"))
    primary_category.select_by_value("13491")  # Adjust if needed

    # Uncheck the PUBLISHED box for tests
    un_publish = driver.find_element(By.XPATH, "/html/body/div[2]/div/main/div[4]/div/form/div/div[3]/div/div[2]/div/div/input")
    un_publish.click()

    save_article = driver.find_element(By.XPATH, "/html/body/div[2]/div/main/div[4]/div/form/div/div[3]/div/div[3]/input[1]")
    save_article.click()

    print(f"Article '{article_key}' added")
    sleep(10)

def setup():
    # Initialize Chrome WebDriver
    chrome_options = Options()
    chrome_options.add_argument("--disable-images")
    chrome_options.add_argument("--disable-extensions")
    driver = webdriver.Chrome(options=chrome_options)

    # Navigate to the Aggie Transcript login page
    driver.get("https://aggietranscript.sf.ucdavis.edu/login")
    return driver

def teardown(driver):
    # Close the browser
    driver.quit()

# Run the login test
test_uc_davis_login()
