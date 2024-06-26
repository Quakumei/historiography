"""
get_articles.py - articles download from cyberleninka
"""

import dataclasses
import typing as tp
import time
import random
from urllib.parse import quote as urlencode

from tqdm import tqdm
from bs4 import BeautifulSoup
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

CYBERLENINKA_BASE_URL = "https://cyberleninka.ru"
ENTRIES_PER_LENINKA_PAGE = 10
SEARCH_RESULTS_ELEMENT_ID = "search-results"

@dataclasses.dataclass
class LeninkaArticle:
    link: str = ""
    pdf_link: str = ""
    title: str = ""
    authors: tp.Tuple[str] = ()
    search_matches: tp.Tuple[str] = ()
    year: int = 0
    journal_name: str = ""
    journal_link: str = ""

    def __key(self):
        return (
            self.link,
            self.pdf_link,
            self.title,
            self.authors,
            self.search_matches,
            self.year,
            self.journal_link,
            self.journal_name
        )
    def __hash__(self):
        return hash(self.__key())

    def __eq__(self, other):
        if isinstance(other, LeninkaArticle):
            return self.__key() == other.__key()
        return NotImplemented

    @classmethod
    def from_li_web_element(cls, search_result):
        link = CYBERLENINKA_BASE_URL + search_result.h2.a.get('href')
        pdf_link = link + '/pdf'
        title = search_result.h2.a.get_text()
        authors = tuple(filter(lambda x: x != '', map(lambda x: x.strip(), search_result.find_all('span')[0].get_text().split(', '))))
        search_matches = tuple([p.get_text() for p in search_result.div.find_all('p')])
        year = int(search_result.find_all('span')[1].get_text().split(" / ")[0])
        journal_name = search_result.find_all('span')[1].a.get_text()
        journal_link = CYBERLENINKA_BASE_URL + search_result.find_all('span')[1].a.get('href')

        return cls(
            link=link,
            pdf_link=pdf_link,
            title=title,
            authors=authors,
            search_matches=search_matches,
            year=year,
            journal_name=journal_name,
            journal_link=journal_link,
        )

    def to_dict(self):
        return dataclasses.asdict(self)

def get_chrome(options: tp.Optional[ChromeOptions] = None) -> Chrome:
    if not options:
        CHROME_ARGUMENTS = (
            "--disable-extensions",
            "--profile-directory=Default",
            "--incognito",
            "--disable-plugins-discovery",
            "--start-maximized"
        )
        options = ChromeOptions()
        for arg in CHROME_ARGUMENTS:
            options.add_argument(arg)

    driver = Chrome(options=options)

    driver.delete_all_cookies()
    driver.set_window_size(823,812)
    driver.set_window_position(0,0)
    driver.execute_cdp_cmd("Page.removeScriptToEvaluateOnNewDocument", {"identifier":"1"})
    
    return driver

def scrape_leninka_articles_search_page(driver: Chrome, url: str, retry_count: int = 3) -> tp.List[LeninkaArticle]:
    """
    Opens a chrome driver to open page with search-results
    and returns a list of articles results
    """
    driver.get(url)
    element = None
    retry_counter = retry_count
    retry_wait_times = [10, 30, 60, 120, 240] 
    while not element and retry_counter != 0:
        try:
            element = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.ID, SEARCH_RESULTS_ELEMENT_ID))
            )
            time.sleep(0.5)
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(0.5)
        except:      
            if retry_counter == 0:
                raise
            time.sleep(retry_wait_times[-max(retry_counter, len(retry_wait_times))])
            retry_counter -= 1
    search_results_html = element.get_attribute('innerHTML')
    soup = BeautifulSoup(search_results_html, 'lxml')
    articles = [LeninkaArticle.from_li_web_element(li) for li in soup.find_all('li')]

    return articles

def scrape_leninka_articles_search(
    driver: Chrome,
    query: str, 
    limit: int = ENTRIES_PER_LENINKA_PAGE, 
    skip: int = 0,
    wait: float = 0.5,
    max_retry_count: int = 5
) -> tp.List[LeninkaArticle]:
    """
    Get all articles infos from search of leninka
    """    
    # Argument validation
    query = query.strip()
    if not query: 
        raise ValueError("Empty 'query' is prohibited")
    if limit < 0:
        raise ValueError(f"'limit' must be a non-negative value (received {limit=})")
    if skip < 0:
        raise ValueError(f"'skip' must be a non-negative value (received {skip=})")
    elif limit == 0:
        return []
    
    search_page_base_url = CYBERLENINKA_BASE_URL + f'/search?q={urlencode(query)}'
    starting_page_idx = skip // ENTRIES_PER_LENINKA_PAGE
    ending_page_idx = (skip + limit) // ENTRIES_PER_LENINKA_PAGE

    articles = []

    for i in tqdm(range(starting_page_idx, ending_page_idx + 1), desc='Pages'):
        search_page_url = search_page_base_url + f'&page={str(i+1)}'
        page_articles = scrape_leninka_articles_search_page(driver, search_page_url, retry_count=max_retry_count) 
        time.sleep(random.uniform(0.9*wait, 1.2*wait))
        articles.extend(page_articles)

    first_article_first_page_idx = skip % ENTRIES_PER_LENINKA_PAGE
    articles = articles[
        first_article_first_page_idx:
        first_article_first_page_idx + limit
    ]
    return articles