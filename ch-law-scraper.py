from selenium import webdriver
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver import FirefoxOptions
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from markdownify import markdownify

# URL to scrape
url = "https://www.fedlex.admin.ch/eli/cc/1999/404/en"

# headless browser
opts = FirefoxOptions()
opts.add_argument("--headless")
driver = webdriver.Firefox(
    executable_path=GeckoDriverManager().install(), options=opts)
driver.get(url)

try:
    delay = 20  # 20 second delay
    WebDriverWait(driver, delay).until(
        EC.visibility_of_element_located((By.ID, 'lawcontent')))
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")
    lawtext = soup.find("div", id="lawcontent")

    soup.find("div", id="toolbar").decompose()

    for div in soup.find_all("div", {'class': 'footnotes'}):
        div.decompose()

    art_headers = soup.find_all("h6")
    for header in art_headers:
        header.name = "h3"

    content = markdownify(str(lawtext), heading_style='ATX')

    with open("output.md", "w") as f:
        f.write(content)

# raises Exception if element is not visible within delay duration
except TimeoutException:
    print("Timed out!")
