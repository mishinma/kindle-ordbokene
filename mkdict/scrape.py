from pathlib import Path

from selenium import webdriver

from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

from bs4 import BeautifulSoup

URL_BASE = "https://ordbokene.no/bm/{}"


def download_page(url: str, dest_dir: str) -> None:
    options = Options()
    options.add_argument('--headless=new')
    cService = webdriver.ChromeService(executable_path='/usr/bin/chromedriver')
    driver = webdriver.Chrome(service = cService, options=options)
    driver.get(url)

    try:
        # Use XPath to find the button by its text "Vis bøyning"
        # and considering it might be inside multiple span elements within a button
        button_xpath = "//button[contains(@class, 'show-inflection') and contains(@class, 'v-btn')]" \
                    "/span[contains(@class, 'v-btn__content')]" \
                    "/span[contains(text(), 'Vis bøyning')]"

        # Wait until the button is clickable
        button_element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, button_xpath))
        )

        # Click the button if found
        button_element.click()
    except TimeoutException:
        # If the button is not found within 10 seconds, proceed without clicking it
        print("The 'Vis bøyning' button was not found. Proceeding without clicking it.")


    try:
        # Wait until the element with class 'article' is present on the page
        article_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'article'))
        )

        # Get the outer HTML of the found element
        article_html = article_element.get_attribute('outerHTML')

    finally:
        # Close the browser window
        driver.quit()

    # Optional: Use Beautiful Soup to parse/manipulate the extracted HTML
    soup = BeautifulSoup(article_html, 'html.parser')
    pretty_html = soup.prettify()

    # Save the HTML to a file
    dest_dir = Path(dest_dir)
    page_index = url.split('/')[-1]
    with open(dest_dir / f"page_{page_index}.html", "w") as f:
        f.write(pretty_html)


def download_pages(indexes, dest_dir):
    for page_range in indexes.split(','):
        page_range = page_range.strip()
        # Check if the input is a range or a single page
        if '-' in page_range:
            # It's a range
            start, end = map(int, page_range.split('-'))
            for i in range(start, end + 1):
                url = URL_BASE.format(i)
                download_page(url, dest_dir)
        else:
            # It's a single page
            page_index = int(page_range)
            url = URL_BASE.format(page_index)
            download_page(url, dest_dir)
