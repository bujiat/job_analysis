"""
Jobs API Endpoints
"""
from fastapi import APIRouter, Query, HTTPException
from typing import List
from app.models.job import JobPosting, JobSearchResult
from app.services.data_loader import DataLoader
from app.services.indexer import build_index, get_doc_text
from app.services.retrieval import bm25_search
from app.services.snippet import get_snippet
from app.services.evaluation import run_evaluation
from app.config import settings

router = APIRouter(prefix="/api/jobs", tags=["jobs"])
data_loader = DataLoader()


@router.get("/", response_model=List[JobPosting])
async def list_jobs(skip: int = Query(0, ge=0), limit: int = Query(20, ge=1, le=100)):
    return data_loader.load_jobs(skip=skip, limit=limit)


@router.get("/search", response_model=List[JobSearchResult])
async def search_jobs(
    q: str = Query(..., min_length=1),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
):
    """BM25 search: returns jobs ranked by relevance with snippet (highlighted query terms)."""
    jobs = data_loader.load_all()
    if not jobs:
        return []
    bm25, doc_ids = build_index(jobs)
    ranked = bm25_search(q, bm25, doc_ids, k=skip + limit)
    job_by_id = {j.job_id: j for j in jobs}
    seen = set()
    results = []
    skipped = 0
    for did, _ in ranked:
        if did in seen:
            continue
        seen.add(did)
        if skipped < skip:
            skipped += 1
            continue
        if len(results) >= limit:
            break
        job = job_by_id[did]
        snippet = get_snippet(get_doc_text(job), q)
        results.append(JobSearchResult(job=job, snippet=snippet))
    return results


@router.get("/evaluate")
async def evaluate():
    jobs = data_loader.load_all()
    if not jobs:
        return {"message": "No data. Run collection first.", "results": []}
    results = run_evaluation(
        jobs, settings.EVAL_QUERIES, build_index, bm25_search,
        k_retrieve=20, k_values=[5, 10], labels_path=settings.EVAL_LABELS_PATH,
    )
    avg = {
        "precision": sum(r["precision"] for r in results) / len(results),
        "recall": sum(r["recall"] for r in results) / len(results),
        "p_at_5": sum(r["p_at_5"] for r in results) / len(results),
        "p_at_10": sum(r["p_at_10"] for r in results) / len(results),
    }
    return {"results": results, "average": avg, "n_queries": len(results), "n_docs": len(jobs)}


@router.get("/count")
async def get_job_count():
    return {"total": data_loader.count_jobs()}


@router.get("/{job_id}", response_model=JobPosting)
async def get_job_detail(job_id: str):
    job = data_loader.get_job_by_id(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return job
