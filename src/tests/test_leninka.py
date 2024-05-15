import typing as tp

import pytest
import itertools

from .fixtures import (
    driver, 
    sample_search_page_url,
    sample_query
)

from ..historiography.scrape.leninka import (
    scrape_leninka_articles_search_page,
    scrape_leninka_articles_search,
    LeninkaArticle,
    ENTRIES_PER_LENINKA_PAGE
)
from ..historiography.settings import CYBERLENINKA_BASE_URL

def validate_leninka_article(article: LeninkaArticle):
    assert isinstance(article, LeninkaArticle)
    assert LeninkaArticle(**article.to_dict()) == article
    article_dict = article.to_dict()
    non_empty_keys = [
        'link',
        'title',
        'journal_name',
        'year',
        'search_matches',
        'journal_link'
        # 'author'
    ]
    for k in non_empty_keys:
        assert bool(article_dict[k]), article_dict

    links = [article.link, article.journal_link]
    possible_link_protocols = ("http://", "https://")
    for link in links:
        assert link.startswith(possible_link_protocols)

def validate_leninka_articles_list(articles: tp.List[LeninkaArticle], expected_len: int):
    assert isinstance(articles, tp.List)
    assert len(articles) == expected_len
    for article in articles:
        validate_leninka_article(article)

def test_leninka_articles_search_page(driver, sample_search_page_url):
    articles = scrape_leninka_articles_search_page(driver, sample_search_page_url)
    validate_leninka_articles_list(articles, ENTRIES_PER_LENINKA_PAGE)

@pytest.mark.parametrize(
        "limit,skip", 
        list(
            itertools.product(
                limits:=[0, 5, 10, 20], 
                skips:=[0, 15, 30]
            )
        )
)
def test_scrape_leninka_articles_search(driver, sample_query, limit, skip):    
    articles = scrape_leninka_articles_search(
        sample_query, 
        limit=limit,
        skip=skip,
        driver=driver
    )
    validate_leninka_articles_list(articles, limit)

    