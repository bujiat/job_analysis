"""
FastAPI Application Main Entry Point
"""
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import os

# Create FastAPI application
app = FastAPI(
    title="Job Aggregator",
    description="Job Information Aggregation and Analysis Platform - Information Retrieval & Parallel Computing Project",
    version="0.1.0"
)

# Configure templates and static files
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))
static_dir = os.path.join(BASE_DIR, "static")

# Mount static files if static directory exists
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """
    Homepage - Display search interface
    """
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/health")
async def health():
    """
    Health check endpoint
    """
    return {"status": "ok", "message": "Job Aggregator is running"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

