import pytest

from ..historiography.scrape.leninka import (
    get_chrome
)

@pytest.fixture
def sample_fixture():
    return "fixture"

@pytest.fixture
def sample_search_page_url():
    return "https://cyberleninka.ru/search?q=%D0%9A%D0%BE%D1%82%D1%8F%D1%82%D0%B0&page=1"

@pytest.fixture(scope="session")
def driver():
    driver = get_chrome()
    yield driver
    driver.close()