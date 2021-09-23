import bs4
from selenium import webdriver
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver import FirefoxOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from markdownify import markdownify
import time
import os.path

# utilize headless browser
opts = FirefoxOptions()
opts.add_argument("--headless")
driver = webdriver.Firefox(
    executable_path=GeckoDriverManager().install(), options=opts)

# function to update superscripts recursively


def update_sup(soup):
    if soup.name == 'sup':
        if any(not isinstance(i, bs4.element.NavigableString) for i in soup.contents):
            soup.extract()
        else:
            soup.string = f'[{soup.get_text(strip=True)}]'
    for i in filter(lambda x: not isinstance(x, bs4.element.NavigableString), soup.contents):
        update_sup(i)


# select input TXT file
with open('linklist.txt', 'r') as f_in:
    for line in map(str.strip, f_in):
        if not line:
            continue

        driver.get(line)
        time.sleep(30)  # standard delay

        # wait until necessary elements are present
        delay = 60  # max delay in seconds until element is present
        WebDriverWait(driver, delay).until(
            EC.visibility_of_element_located((By.CLASS_NAME, 'srnummer')))
        WebDriverWait(driver, delay).until(
            EC.visibility_of_element_located((By.CLASS_NAME, 'erlasstitel')))
        WebDriverWait(driver, delay).until(
            EC.visibility_of_element_located((By.ID, 'lawcontent')))
        html = driver.page_source
        soup = bs4.BeautifulSoup(html, "html.parser")

        # remove toolbar
        soup.find("div", id="toolbar").decompose()

        # remove footnotes
        for div in soup.find_all("div", {'class': 'footnotes'}):
            div.decompose()

        # call function to handle superscripts
        update_sup(soup)

        # isolate descriptive lists to paragraphs
        for dl_list in soup.find_all("dl"):
            dl_list.name = "p"

        for dt_list in soup.find_all("dt"):
            dt_list.insert_after(" ")  # add whitespace after tag
            dt_list.name = "br"

        # replace div headings with h2 headers
        for divheader in soup.find_all("div", {'class': 'heading'}):
            divheader.name = "h2"

        # get norms
        lawtext = soup.find("div", id="lawcontent")

        # convert to markdown
        content = markdownify(str(lawtext), heading_style='ATX')

        # fetch SR number
        sr_num = soup.find("p", {'class': 'srnummer'})
        if not sr_num:  # <== check for NoneType
            print('element not found')
            sr_num = 'no sr num'
        else:
            sr_num = sr_num.text

        # fetch law title
        law_title = soup.find("h1", {'class': 'erlasstitel'})
        if not law_title:  # <== check for NoneType
            print('element not found')
            law_title = 'no title'
        else:
            law_title = law_title.text

        # define categories and match with sr number
        sr_num_string = str(sr_num)
        sr_digits = ["1", "2", "3", "4", "5", "6", "7", "8", "9"]
        categories = ["State - People - Authorities",
                      "Private law - Administration of civil justice - Enforcement",
                      "Criminal law - Administration of criminal justice - Execution of sentences",
                      "Education - Science - Culture",
                      "National defence",
                      "Finance",
                      "Public works - Energy - Transport",
                      "Health - Employment - Social security",
                      "Economy - Technical cooperation"]
        if sr_num_string[0] in sr_digits:
            category = categories[sr_digits.index(sr_num_string[0])]
        else:
            category = "no category"

        # write to markdown file in subdirectory
        directory = "./federal_law/" + category + "/"
        file_name = sr_num + "_" + law_title + ".md"
        file_path = os.path.join(directory, file_name)
        if not os.path.isdir(directory):
            os.mkdir(directory)
        with open(file_path, "w") as f_out:
            f_out.write(content)
            f_out.close()

f_in.close()
