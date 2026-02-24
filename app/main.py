"""
FastAPI Application Main Entry Point
"""
import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.api import jobs as jobs_api

app = FastAPI(
    title="Job Aggregator",
    description="Job Information Aggregation and Analysis Platform",
    version="0.1.0"
)

app.include_router(jobs_api.router)

templates = Jinja2Templates(directory=os.path.join(settings.BASE_DIR, "templates"))
static_dir = os.path.join(settings.BASE_DIR, "static")

if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/job/{job_id}", response_class=HTMLResponse)
async def job_detail(request: Request, job_id: str):
    return templates.TemplateResponse("job_detail.html", {
        "request": request,
        "job_id": job_id
    })


@app.get("/health")
async def health():
    return {"status": "ok", "message": "Job Aggregator is running"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
