import asyncio
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from app.agent.orchestrator import AgentOrchestrator

app = FastAPI(title="PatchLoop API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

jobs = {}

class RunRequest(BaseModel):
    repo_url: str
    issue: str = Field(min_length=1)
    branch: str | None = None

@app.get("/api/health")
def health():
    return {"ok": True}

@app.post("/api/run")
async def run_agent(req: RunRequest):
    orchestrator = AgentOrchestrator()
    job_id = orchestrator.job_id
    jobs[job_id] = orchestrator
    # Run in background so the frontend can poll.
    asyncio.create_task(orchestrator.run(req.repo_url, req.issue, req.branch))
    return {"job_id": job_id}

@app.get("/api/run/{job_id}")
def get_run(job_id: str):
    job = jobs.get(job_id)
    if not job:
        raise HTTPException(404, "Job not found")
    return job.public_state()

@app.get("/")
def root():
    return {"name": "PatchLoop", "docs": "/docs"}
