import typing as tp

import pytest
import itertools

from ..historiography.scrape.leninka import (
    scrape_leninka_articles_search_page,
    scrape_leninka_articles_search,
    LeninkaArticle,
    ENTRIES_PER_LENINKA_PAGE,
)

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
        'journal_link',
        'pdf_link'
        # 'author'
    ]
    for k in non_empty_keys:
        assert bool(article_dict.get(k, None)), article_dict

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
        driver,
        sample_query, 
        limit=limit,
        skip=skip,
    )
    validate_leninka_articles_list(articles, limit)

def test_scrape_leninka_articles_search_does_not_duplicate(driver, sample_query):    
    articles = scrape_leninka_articles_search(
        driver,
        sample_query, 
        limit=10,
        skip=0,
    )
    validate_leninka_articles_list(articles, 10)
    articles_next = scrape_leninka_articles_search(
        driver,
        sample_query, 
        limit=10,
        skip=10,
    )
    validate_leninka_articles_list(articles_next, 10)

    assert set(articles).intersection(set(articles_next)) == set()

def test_urlencode_space():
    sample = 'a b c'
    encoded = urlencode(sample)
    assert sample.replace(" ", "%20") == encoded