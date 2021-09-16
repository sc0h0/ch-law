from selenium import webdriver
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver import FirefoxOptions
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from markdownify import markdownify

# target URL
url = "https://www.fedlex.admin.ch/eli/cc/24/233_245_233/en"

# utilize headless browser
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
    lawtext = soup.find("div", id="lawcontent")  # extract norms

    # remove toolbar
    soup.find("div", id="toolbar").decompose()

    # remove footnotes
    for div in soup.find_all("div", {'class': 'footnotes'}):
        div.decompose()

    # remove superscripts belonging to footnotes
    for superscripts in soup.find_all("sup"):
        for suplink in superscripts.find_all("a"):
            suplink.decompose()

    # isolate descriptive lists to paragraphs
    for dt_list in soup.find_all("dl"):
        dt_list.name = "p"

    for dt_list in soup.find_all("dt"):
        dt_list.name = "br"

    # replace div headings headers with h2 headers
    for divheader in soup.find_all("div", {'class': 'heading'}):
        divheader.name = "h2"

    # replace h6 headers with h3 headers
    for header in soup.find_all("h6"):
        header.name = "h3"

    # convert to markdown
    content = markdownify(str(lawtext), heading_style='ATX')

    # write to markdown file
    with open("output.md", "w") as f:
        f.write(content)


# raises Exception if element is not visible within delay duration
except TimeoutException:
    print("Timed out!")
