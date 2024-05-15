import typing as tp

from .fixtures import (
    driver, 
    sample_search_page_url
)

from ..historiography.scrape.leninka import (
    scrape_page,
    LeninkaArticle,
    ENTRIES_PER_LENINKA_PAGE
)
from ..historiography.settings import CYBERLENINKA_BASE_URL

def test_scrape_page(driver, sample_search_page_url):
    articles = scrape_page(driver, sample_search_page_url)

    assert isinstance(articles, tp.List)
    assert len(articles) == ENTRIES_PER_LENINKA_PAGE

    for article in articles:
        assert isinstance(article, LeninkaArticle)
        assert LeninkaArticle(**article.to_dict()) == article
        assert all(list(article.to_dict().values()))

        links = [article.link, article.journal_link]
        possible_link_protocols = ("http://", "https://")
        for link in links:
            assert link.startswith(possible_link_protocols)



    