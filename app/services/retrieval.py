"""
BM25 retrieval using rank_bm25. Scores documents and returns top-k (doc_id, score).
"""
from typing import List, Optional, Tuple

from rank_bm25 import BM25Okapi

from app.services.preprocess import preprocess_text


def bm25_search(
    query: str,
    bm25: Optional[BM25Okapi],
    doc_ids: List[str],
    k: int = 20,
) -> List[Tuple[str, float]]:
    """
    Rank documents by BM25 score. Uses same preprocessing as index (tokenize, stop words, stem).
    Returns list of (doc_id, score) sorted by score descending, at most k results.
    """
    if bm25 is None or not doc_ids:
        return []

    query_terms = preprocess_text(query)
    if not query_terms:
        return []

    scores = bm25.get_scores(query_terms)
    indexed = [(doc_ids[i], float(scores[i])) for i in range(len(doc_ids))]
    ranked = sorted(indexed, key=lambda x: -x[1])
    return ranked[:k]
