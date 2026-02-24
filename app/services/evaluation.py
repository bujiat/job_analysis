"""
IR Evaluation: Precision, Recall, Precision@K.

Formulas (Stanford IR Book Ch.8 style):
- Precision = |Relevant ∩ Retrieved| / |Retrieved| = TP / (TP + FP)
- Recall = |Relevant ∩ Retrieved| / |Relevant| = TP / (TP + FN)
- Precision@K = (number of relevant in top-K retrieved) / K

P@10 uses human-labeled relevant_ids from eval_labels.json when available.
"""
import json
import os
from typing import List, Set, Dict, Optional


def precision(retrieved_ids: List[str], relevant_ids: Set[str]) -> float:
    """
    Precision = (number of relevant in retrieved) / (number of retrieved).
    Of what we returned, what fraction is relevant? If we return nothing, 0.0.
    """
    if not retrieved_ids:
        return 0.0
    retrieved_set = set(retrieved_ids)
    hit = len(relevant_ids & retrieved_set)
    return hit / len(retrieved_ids)


def recall(retrieved_ids: List[str], relevant_ids: Set[str]) -> float:
    """
    Recall = (number of relevant in retrieved) / (number of relevant).
    If there are no relevant docs, return 0.0.
    """
    if not relevant_ids:
        return 0.0
    retrieved_set = set(retrieved_ids)
    hit = len(relevant_ids & retrieved_set)
    return hit / len(relevant_ids)


def precision_at_k(retrieved_ids: List[str], relevant_ids: Set[str], k: int) -> float:
    """
    Precision@K = (number of relevant in top-K retrieved) / K.
    Only the first K results count; if we return fewer than K, denominator is still K (standard definition).
    """
    if k <= 0:
        return 0.0
    top_k = retrieved_ids[:k]
    hit = sum(1 for doc_id in top_k if doc_id in relevant_ids)
    return hit / k


def get_relevant_ids_heuristic(jobs: list, query: str) -> Set[str]:
    """
    Pseudo-relevance: docs whose title+description contain every query word (case-insensitive).
    Used when no human labels exist; for real evaluation you would use labeled (query, relevant_ids).
    """
    words = [w.strip().lower() for w in query.lower().split() if w.strip()]
    if not words:
        return set()
    relevant = set()
    for job in jobs:
        text = ((job.title or "") + " " + (job.description or "")).lower()
        if all(w in text for w in words):
            relevant.add(job.job_id)
    return relevant


def load_labels(path: str) -> Dict[str, Set[str]]:
    """
    Load human labels from JSON: [{"query": "...", "relevant_ids": ["id1", ...]}, ...].
    Returns dict: query -> set of relevant doc_ids. Empty dict if file missing or invalid.
    """
    if not path or not os.path.isfile(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}
    out = {}
    for item in data if isinstance(data, list) else []:
        q = item.get("query")
        ids = item.get("relevant_ids")
        if q is not None and isinstance(ids, list):
            out[str(q).strip()] = set(ids)
    return out


def run_evaluation(
    jobs: list,
    queries: List[str],
    build_index_fn,
    bm25_search_fn,
    k_retrieve: int = 20,
    k_values: List[int] = None,
    labels_path: Optional[str] = None,
) -> List[dict]:
    """
    Run evaluation. Precision, Recall, P@5 use heuristic relevance.
    P@10 uses human labels when labels_path exists and has that query; otherwise heuristic.
    """
    if not jobs:
        return []
    human_labels = load_labels(labels_path) if labels_path else {}
    bm25, doc_ids = build_index_fn(jobs)
    k_values = k_values or [5, 10]
    results = []
    for q in queries:
        relevant_heuristic = get_relevant_ids_heuristic(jobs, q)
        relevant_p10 = human_labels.get(q, relevant_heuristic)
        ranked = bm25_search_fn(q, bm25, doc_ids, k=k_retrieve)
        retrieved_ids = [doc_id for doc_id, _ in ranked]
        p_at = {}
        for k in k_values:
            rel = relevant_p10 if (k == 10 and q in human_labels) else relevant_heuristic
            p_at[f"p_at_{k}"] = precision_at_k(retrieved_ids, rel, k)
        results.append({
            "query": q,
            "precision": precision(retrieved_ids, relevant_heuristic),
            "recall": recall(retrieved_ids, relevant_heuristic),
            **p_at,
            "p_at_10_from_labels": q in human_labels,
            "relevant_count": len(relevant_heuristic),
            "retrieved_count": len(retrieved_ids),
        })
    return results
