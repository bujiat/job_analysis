"""
Job Data Model
Defines standardized job posting data structure
Purpose: Unify data format from different sources for easier processing
"""
# Pydantic model 数据校验和解析
from typing import List
from pydantic import BaseModel

class JobPosting(BaseModel):
    """Standardized job posting data model - fields for display and IR"""
    job_id: str          # Unique job identifier
    title: str           # Job title (for display)
    company_name: str    # Company name (for display)
    location: str        # Job location (for display)
    description: str     # Job description (for IR indexing + display)
    tags: List[str]      # Skill tags (for display)
    created_at: str      # Creation timestamp (for display)
    # Additional fields for page display
    source_url: str      # Original job URL (for "View Details" link)
    remote: bool         # Is remote work available (for display filter)
    job_types: List[str] # Job types: Full-time, Part-time, etc. (for display)


class JobSearchResult(BaseModel):
    """Search result: job plus snippet with highlighted query terms."""
    job: JobPosting
    snippet: str


def from_arbeitnow(raw_job: dict) -> JobPosting:
    """
    Convert Arbeitnow API raw data to standardized JobPosting format
    
    Args:
        raw_job: Raw dictionary from API response
        
    Returns:
        Standardized JobPosting object
    """
    # Handle created_at: could be timestamp (int) or string
    created_at = raw_job.get('created_at', '')
    if isinstance(created_at, (int, float)):
        created_at = str(created_at)  # Convert timestamp to string
    
    return JobPosting(
        job_id=raw_job.get('slug', '') or raw_job.get('url', '').split('/')[-1],
        title=raw_job.get('title', ''),
        company_name=raw_job.get('company_name', ''),
        location=raw_job.get('location', ''),
        description=raw_job.get('description', ''),
        tags=raw_job.get('tags', []),
        created_at=created_at,
        source_url=raw_job.get('url', ''),
        remote=raw_job.get('remote', False),
        job_types=raw_job.get('job_types', []),
    )

