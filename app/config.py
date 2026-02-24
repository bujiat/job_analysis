"""
Application Configuration
"""
import os

class Settings:
    DEFAULT_JOB_KEYWORDS: list = [
        "software", "developer", "engineer", "programming", "programmer", "coding",
        "hardware", "embedded", "firmware",
        "computer", "computing", "it", "information technology",
        "data science", "data scientist", "data analyst", "data engineer", "machine learning",
        "artificial intelligence", "ai", "ml", "deep learning", "neural network",
        "devops", "cloud", "backend", "frontend", "fullstack", "full stack"
    ]
    
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATA_DIR: str = os.path.join(BASE_DIR, "data")
    RAW_DATA_DIR: str = os.path.join(DATA_DIR, "raw")
    NORMALIZED_DATA_DIR: str = os.path.join(DATA_DIR, "normalized")
    EVAL_LABELS_PATH: str = os.path.join(DATA_DIR, "eval_labels.json")
    
    ARBEITNOW_API: str = "https://arbeitnow.com/api/job-board-api"
    EVAL_QUERIES: list = ["python", "developer", "backend", "software engineer", "remote"]

settings = Settings()
