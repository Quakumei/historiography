import pytest

from ..historiography.scrape.leninka import (
    get_chrome, urlencode
)

@pytest.fixture
def sample_fixture():
    return "fixture"

@pytest.fixture
def sample_query():
    return 'Котята'

@pytest.fixture
def sample_search_page_url(sample_query):
    page_no = 1
    return f"https://cyberleninka.ru/search?q={urlencode(sample_query)}&page={str(page_no)}"

@pytest.fixture(scope="session")
def driver():
    driver = get_chrome()
    yield driver
    driver.close()