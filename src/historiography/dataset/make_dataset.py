from pathlib import Path
import typing as tp
import numpy as np

import pandas as pd
from tqdm import tqdm

from ..logger import logger
from ..settings import HistoriographyDatasetConfig
from ..scrape.leninka import (
    get_chrome, 
    scrape_leninka_articles_search,
    LeninkaArticle,
    Chrome,
)

def read_search_queries_from_file(file: Path) -> tp.List[str]:
    with open(file, 'r') as f:
        return [l for l in map(str.strip, f.readlines()) if l]

def make_historiography_dataset(
    driver: Chrome,
    config: HistoriographyDatasetConfig = HistoriographyDatasetConfig(),
) -> pd.DataFrame:
    logger.info(f"Creating dataset with {config=}")
        
    articles: tp.List[dict] = []
    queries = read_search_queries_from_file(config.search_queries_file)
    for query in tqdm(queries, desc='Queries'):
        try:
            found_articles = scrape_leninka_articles_search(
                driver=driver, 
                query=query, 
                limit=config.articles_per_query,
                wait=config.wait_between_pages
            )
        except Exception as e:
            logger.error(f"Dataset collection for '{query}' stopped early due to exception: {e}")
            continue

        found_articles = [*map(LeninkaArticle.to_dict, found_articles)]
        for article in found_articles:
            article['query'] = query

        articles.extend(found_articles)
        logger.info(f'One of articles from "{query}": {article}')

    # lil processing
    dataset = pd.DataFrame(articles).drop_duplicates()
    dataset['authors'] = dataset['authors'].apply(lambda x: ', '.join(x) if x else "Автор не указан")
    dataset['search_match_1'] = dataset['search_matches'].apply(lambda x: x[0] if len(x) >= 1 else np.nan)
    dataset['search_match_2'] = dataset['search_matches'].apply(lambda x: x[1] if len(x) >= 2 else np.nan)
    dataset = dataset.drop(labels=['search_matches'], axis=1)

    logger.info(f"Saving dataset to {str(config.output_file_path)}")
    dataset.to_csv(str(config.output_file_path), index=False)
    return dataset
        
if __name__ == '__main__':
    driver = get_chrome()
    dataset: pd.DataFrame = make_historiography_dataset(driver=driver)
    logger.info(dataset.head())
    