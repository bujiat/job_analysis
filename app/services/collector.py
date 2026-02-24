"""
Data Collection Service - IR Step 1: Data Collection

IR Workflow:
1. Data Collection  - Get raw data from sources
2. Preprocessing - Tokenization, stop-word removal, stemming
3. Indexing - Build inverted index, calculate TF-IDF
4. Retrieval - Search and rank documents
5. Evaluation - Precision, Recall, Precision@K

This module implements Step 1: Collecting job postings from API
"""
import json
from pathlib import Path
from typing import List, Tuple
from datetime import datetime
import requests
from app.config import settings
from app.models.job import JobPosting, from_arbeitnow


class DataCollector:
    def __init__(self):
        self.raw_dir = Path(settings.RAW_DATA_DIR)
        self.normalized_dir = Path(settings.NORMALIZED_DATA_DIR)
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.normalized_dir.mkdir(parents=True, exist_ok=True)

    # Filter raw jobs by IT/tech keywords (OR in title+description)
    def _filter_jobs(self, jobs: List[dict], keywords: list = None) -> List[dict]:
        keywords = keywords or settings.DEFAULT_JOB_KEYWORDS
        filtered = []
        for job in jobs:
            text = (job.get('title', '') + ' ' + job.get('description', '')).lower()
            if any(kw.lower() in text for kw in keywords):
                filtered.append(job)
        return filtered

    # Fetch from API -> filter -> save raw -> standardize and return
    def collect(self, max_jobs: int = 200, keywords: list = None) -> List[JobPosting]:
        response = requests.get(settings.ARBEITNOW_API, timeout=10)
        data = response.json()
        raw_jobs = data.get('data', [])
        
        filtered_raw = self._filter_jobs(raw_jobs, keywords=keywords)
        filtered_raw = filtered_raw[:max_jobs]
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        raw_file = self.raw_dir / f"raw_{timestamp}.json"
        with open(raw_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        jobs = [from_arbeitnow(raw_job) for raw_job in filtered_raw]
        print(f"Collected {len(jobs)} IT/tech jobs (from {len(raw_jobs)} total)")
        return jobs
    
    # Write standardized jobs to JSONL (one JSON object per line)
    def save(self, jobs: List[JobPosting]) -> Path:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = self.normalized_dir / f"jobs_{timestamp}.jsonl"
        with open(filepath, 'w', encoding='utf-8') as f:
            for job in jobs:
                f.write(json.dumps(job.dict(), ensure_ascii=False) + '\n')
        print(f"Saved to: {filepath}")
        return filepath
    
    def collect_and_save(self, max_jobs: int = 200, keywords: list = None) -> Tuple[List[JobPosting], Path]:
        jobs = self.collect(max_jobs=max_jobs, keywords=keywords)
        filepath = self.save(jobs)
        return jobs, filepath
