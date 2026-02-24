"""
Data Loader Service
"""
import json
from pathlib import Path
from typing import List, Optional
from app.models.job import JobPosting
from app.config import settings


class DataLoader:
    def __init__(self):
        self.normalized_dir = Path(settings.NORMALIZED_DATA_DIR)

    # Latest JSONL file by modification time in data/normalized/
    def load_latest(self) -> Optional[Path]:
        jsonl_files = list(self.normalized_dir.glob("jobs_*.jsonl"))
        if not jsonl_files:
            return None
        return max(jsonl_files, key=lambda p: p.stat().st_mtime)

    # Load all jobs from latest JSONL (for building search index)
    def load_all(self) -> List[JobPosting]:
        filepath = self.load_latest()
        if filepath is None or not filepath.exists():
            return []
        jobs = []
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                jobs.append(JobPosting(**json.loads(line.strip())))
        return jobs

    # Paginated list from latest JSONL
    def load_jobs(self, skip: int = 0, limit: int = 20) -> List[JobPosting]:
        filepath = self.load_latest()
        if filepath is None or not filepath.exists():
            return []
        jobs = []
        with open(filepath, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f):
                if i < skip:
                    continue
                if len(jobs) >= limit:
                    break
                jobs.append(JobPosting(**json.loads(line.strip())))
        return jobs

    # Linear scan for one job_id
    def get_job_by_id(self, job_id: str) -> Optional[JobPosting]:
        filepath = self.load_latest()
        if filepath is None or not filepath.exists():
            return None
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                d = json.loads(line.strip())
                if d.get('job_id') == job_id:
                    return JobPosting(**d)
        return None

    # Number of lines in latest JSONL
    def count_jobs(self) -> int:
        filepath = self.load_latest()
        if filepath is None or not filepath.exists():
            return 0
        count = 0
        with open(filepath, 'r', encoding='utf-8') as f:
            for _ in f:
                count += 1
        return count
