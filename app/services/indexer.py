"""
Build search index: preprocess documents and create BM25 model (rank_bm25).
Returns (BM25Okapi, doc_ids) for use by retrieval.
"""
from typing import List, Optional, Tuple

from rank_bm25 import BM25Okapi

from app.models.job import JobPosting
from app.services.preprocess import preprocess_text

BM25_K1 = 1.5
BM25_B = 0.5


def get_doc_text(job: JobPosting) -> str:
    """Single source for document text (indexing and snippet)."""
    return (job.title or "") + " " + (job.description or "")


def build_index(jobs: List[JobPosting]) -> Tuple[Optional[BM25Okapi], List[str]]:
    """
    Tokenize each job's text and build BM25 index.
    Returns (bm25_model, doc_ids) where doc_ids[i] is job_id for corpus[i].
    """
    if not jobs:
        return None, []

    tokenized_corpus = [preprocess_text(get_doc_text(job)) for job in jobs]
    doc_ids = [job.job_id for job in jobs]
    bm25 = BM25Okapi(tokenized_corpus, k1=BM25_K1, b=BM25_B)
    return bm25, doc_ids
