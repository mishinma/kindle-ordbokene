from selenium import webdriver

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from bs4 import BeautifulSoup


cService = webdriver.ChromeService(executable_path='/usr/bin/chromedriver')
driver = webdriver.Chrome(service = cService)
# url = 'https://ordbokene.no/bm/53143'  # sjønne
url = 'https://ordbokene.no/bm/21740'  # gå
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

    # Click the button
    button_element.click()

    # Wait until the element with class 'article' is present on the page
    article_element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'article'))
    )

    # Get the outer HTML of the found element
    article_html = article_element.get_attribute('outerHTML')

    # Optional: Use Beautiful Soup to parse/manipulate the extracted HTML
    soup = BeautifulSoup(article_html, 'html.parser')
    pretty_html = soup.prettify()
    with open('selenuim_page.html', 'w', encoding='utf-8') as file:
        file.write(pretty_html)

finally:
    # Close the browser window
    driver.quit()