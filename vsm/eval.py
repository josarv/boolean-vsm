from collections import defaultdict
from typing import Iterable, List, Tuple, Dict
from math import log, sqrt
from .index import InvertedIndex


def compute_query_vector(index: InvertedIndex, query_tokens: Iterable[str]) -> dict[str, float]:
    term_counts: Dict[str, int] = {}
    for token in query_tokens:
        term_counts[token] = term_counts.get(token, 0) + 1
    query_vector: Dict[str, float] = {}
    n_documents = index.document_count()
    for term, count in term_counts.items():
        df = index.term_document_frequency(term)
        if df == 0:
            continue
        idf = log(n_documents / df)
        tf = count / sum(term_counts.values())
        query_vector[term] = tf * idf
    return query_vector


def compute_cosine_similarities(index: InvertedIndex, query_vector: dict[str, float]) -> List[Tuple[int, float]]:
    query_norm = sqrt(sum(weight ** 2 for weight in query_vector.values()))
    if query_norm == 0:
        return []
    scores: Dict[int, float] = defaultdict(float)
    for term, q_weight in query_vector.items():
        postings = index.term_postings(term)
        for doc_id, d_weight in postings:
            scores[doc_id] += q_weight * d_weight  # accumulate dot product
    results: list[Tuple[int, float]] = []
    for doc_id, dot in scores.items():
        doc_norm = index.document_norm(doc_id)
        if doc_norm > 0:
            similarity = dot / (query_norm * doc_norm)
            results.append((doc_id, similarity))
    return results
