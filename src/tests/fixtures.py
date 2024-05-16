import pytest
import pathlib
import selenium

from ..historiography.settings import HistoriographyDatasetConfig
from ..historiography.scrape.leninka import (
    get_chrome, urlencode
)

@pytest.fixture
def sample_fixture() -> str:
    return "fixture"

@pytest.fixture
def sample_query() -> str:
    return 'Котята'

@pytest.fixture
def sample_search_page_url(sample_query) -> str:
    return f"https://cyberleninka.ru/search?q={urlencode(sample_query)}&page=1"

@pytest.fixture(scope="session")
def driver() -> selenium.webdriver.Chrome:
    """Returns chrome driver for session"""
    driver = get_chrome()
    yield driver
    driver.close()

@pytest.fixture
def sample_valid_dataset_config(tmp_path, sample_query) -> HistoriographyDatasetConfig:
    """Sample valid config without saved dataset file"""
    sample_query_file = tmp_path / "single_search_query.txt"
    sample_query_file.write_text(sample_query)
    ds_file: pathlib.Path = tmp_path / 'historiography.csv'
    ds_file.unlink(missing_ok=True)

    return HistoriographyDatasetConfig(
        output_file_path=ds_file,
        search_queries_file=sample_query_file
    )