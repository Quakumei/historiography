from .fixtures import (
    sample_authors_list
)
from ..historiography.analysis.authors import (
    get_authors_total_publication_counts,
    get_authors_solo_publication_counts
)

def test_get_authors_solo_publication_counts(sample_authors_list):
    counts = get_authors_solo_publication_counts(sample_authors_list[0])
    for author in sample_authors_list[1]:
        assert counts.get(author, 0) == len(list(filter(lambda x: len(x) == 1 and x[0] == author, sample_authors_list[0]))), author


def test_get_authors_total_publication_counts(sample_authors_list):
    counts = get_authors_total_publication_counts(sample_authors_list[0])
    for author in sample_authors_list[1]:
        assert counts.get(author, 0) == len(list(filter(lambda x: author in x, sample_authors_list[0]))), author
