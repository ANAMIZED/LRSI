"""LRSI FastAPI application."""
from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

try:
    from lrsi import __version__
except Exception:
    __version__ = "0.1.0"

app = FastAPI(
    title="LRSI",
    description="Local Recursive Self-Improvement — Autonomous Agentic Operating System API.",
    version=__version__,
)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


@app.get("/health")
def health():
    return {"status": "ok", "service": "lrsi", "version": __version__}


@app.get("/v1/status")
def status():
    return {
        "service": "lrsi",
        "version": __version__,
        "surfaces": ["cli", "sdk", "api", "mcp", "multi-agent"],
    }


@app.post("/v1/workflows")
def workflow(goal: str = "improve-skill", agents: list[str] | None = None):
    return {
        "goal": goal,
        "agents": agents or ["improver", "evaluator", "council"],
        "mode": "mock",
        "status": "accepted",
    }


@app.get("/v1/audit")
def audit(limit: int = 20):
    return {"records": [], "limit": limit, "mode": "mock"}


def run():
    import uvicorn

    uvicorn.run("lrsi.api.main:app", host="0.0.0.0", port=8080, reload=False)


if __name__ == "__main__":
    run()
