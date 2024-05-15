"""
get_articles.py - articles download from cyberleninka
"""

import dataclasses
import typing as tp
from urllib.parse import quote_plus as urlencode

from tqdm import tqdm
from bs4 import BeautifulSoup
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from src.historiography.settings import CYBERLENINKA_BASE_URL

ENTRIES_PER_LENINKA_PAGE = 10
SEARCH_RESULTS_ELEMENT_ID = "search-results"

@dataclasses.dataclass
class LeninkaArticle:
    link: str = ""
    title: str = ""
    author: str = ""
    search_matches: tp.Tuple[str] = ()
    year: int = 0
    journal_name: str = ""
    journal_link: str = ""

    @classmethod
    def from_li_web_element(cls, search_result):
        link = CYBERLENINKA_BASE_URL + search_result.h2.a.get('href')
        title = search_result.h2.a.get_text()
        author = search_result.find_all('span')[0].get_text()
        search_matches = tuple([p.get_text() for p in search_result.div.find_all('p')])
        year = int(search_result.find_all('span')[1].get_text().split(" / ")[0])
        journal_name = search_result.find_all('span')[1].a.get_text()
        journal_link = CYBERLENINKA_BASE_URL + search_result.find_all('span')[1].a.get('href')

        return cls(
            link=link,
            title=title,
            author=author,
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

def scrape_leninka_articles_search_page(driver: Chrome, url: str) -> tp.List[LeninkaArticle]:
    """
    Opens a chrome driver to open page with search-results
    and returns a list of articles results
    """
    driver.get(url)
    element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, SEARCH_RESULTS_ELEMENT_ID))
    )
    search_results_html = element.get_attribute('innerHTML')
    soup = BeautifulSoup(search_results_html, 'lxml')
    articles = [LeninkaArticle.from_li_web_element(li) for li in soup.find_all('li')]

    return articles

def scrape_leninka_articles_search(
    query: str, 
    limit: int = ENTRIES_PER_LENINKA_PAGE, 
    skip: int = 0,
    driver: Chrome = None
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
    starting_page = 1 + skip // ENTRIES_PER_LENINKA_PAGE
    ending_page = 1 + (skip + limit) // ENTRIES_PER_LENINKA_PAGE

    articles = []

    for i in tqdm(range(starting_page, ending_page + 1), desc='Pages'):
        search_page_url = search_page_base_url + f'&page={str(i)}'
        page_articles = scrape_leninka_articles_search_page(driver, search_page_url) 
        articles.extend(page_articles)

    position_of_first_article_on_first_page = skip % ENTRIES_PER_LENINKA_PAGE
    position_of_last_article_on_last_page = ((skip+limit) % ENTRIES_PER_LENINKA_PAGE)
    articles = articles[
        position_of_first_article_on_first_page:
        -(ENTRIES_PER_LENINKA_PAGE - position_of_last_article_on_last_page)
    ]
    return articles


def get_articles(search: str, limit: int = ENTRIES_PER_LENINKA_PAGE, skip: int = 0) -> tp.List:
    # 1. Get download links
    links = scrape_leninka_articles_search(search, limit, skip)
    
   
    
