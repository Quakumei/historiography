import typing as tp
from pprint import pprint
from collections import Counter

import pandas as pd
from tqdm import tqdm
from pyvis.network import Network

from ..settings import HistoriographyDatasetConfig
from ..logger import logger

def build_authors_co_publications_graph(authors_l: tp.List[tp.Tuple[str]], stop_authors: tp.List[str] = ['и др.']) -> dict[str, dict[str, int]]:
    authors = authors_l.copy()
    before_len = len(authors)
    authors = filter(lambda x: len(x) > 1, authors)
    authors = list(authors)
    after_len = len(authors)
    percent_removed = 1 - after_len / (before_len)
    logger.info(f"[calculate_authors_co_publications] Filtered {before_len-after_len=} authors ({percent_removed=:.2f}) who was published alone")
    authors_co_publications: dict[str, dict[str, int]] = {}
    for authors_of_paper in tqdm(authors, desc='Authors'):
        for author in authors_of_paper:
            if author in stop_authors:
                continue
            for co_author in (a for a in authors_of_paper if a != author):
                if co_author in stop_authors:
                    continue
                if author not in authors_co_publications:
                    authors_co_publications[author] = {}
                if co_author not in authors_co_publications[author]:
                    authors_co_publications[author][co_author] = 0
                authors_co_publications[author][co_author] += 1
    return authors_co_publications

def get_authors_total_publication_counts(authors: tp.List[tp.Tuple[str]]) -> dict[str, int]:
    authors_list = []
    for authors_of_paper in authors:
        for a in authors_of_paper:
            authors_list.append(a)
    return dict(Counter(authors_list))

def get_authors_solo_publication_counts(authors: tp.List[tp.Tuple[str]]) -> dict[str, int]:
    paper_authors = authors.copy()
    single_authors = filter(lambda x: len(x) == 1, paper_authors)
    single_authors = map(lambda x: x[0], single_authors)
    return dict(Counter(single_authors))

if __name__=='__main__':
    config = HistoriographyDatasetConfig()
    # df = pd.read_csv('')
    df = pd.read_csv('data/historiography.csv')
    logger.info(df.head())
    logger.info(list(df.columns))
    authors = [author_str.split(', ') for author_str in df['authors'].tolist()]

    # 1. Сколько публикаций у каждого автора?
    author_publications_counts: dict[str, int] = get_authors_total_publication_counts(authors) 
    author_solo_publications_counts: dict[str, int] = get_authors_solo_publication_counts(authors)   

    # 2. Какие авторы чаще всего публикуются вместе? или Кто работает вместе?
    authors_co_publications = build_authors_co_publications_graph(authors)
    pprint(authors_co_publications)
    net: Network = Network(
        height='98vh', 
        width='99vw', 
        select_menu=True, 
        neighborhood_highlight=True, 
        filter_menu=True,
        bgcolor="#222222", 
        font_color="white",

    )
    for a, co_authors in authors_co_publications.items():
        net.add_node(a, label=a, title=f"Name: {a}")

    for a, co_authors in authors_co_publications.items():
        for co_a, count in co_authors.items():
            net.add_edge(a, co_a, value=count)

    for node in net.nodes:
        a = node['id']
        label_pubcount = f'Total publications #: {author_publications_counts.get(a, 0)}'
        label_solopubcount = f'Solo publications #: {author_solo_publications_counts.get(a, 0)}'
        full_label = '\n'.join([label_pubcount, label_solopubcount])
        node["title"] += '\n' + full_label
        node["value"] = author_publications_counts.get(a, 0)

    # TODO: add journals

    # os.makedirs('data/artifacts', exist_ok=True)
    # net.show_buttons(filter_=['physics'])
    net.show("co_publications_net.html", notebook=False)

    # 2. В каких журналах публиковался автор? 
