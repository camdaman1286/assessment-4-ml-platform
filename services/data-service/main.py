# data-service: handles data ingestion and preprocessing.
# /health  — liveness probe
# /ready   — readiness probe
# /ingest  — placeholder ingestion endpoint

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="data-service")


class IngestRequest(BaseModel):
    payload: str


class IngestResponse(BaseModel):
    status: str
    received: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/ready")
def ready():
    return {"status": "ready"}


@app.post("/ingest", response_model=IngestResponse)
def ingest(req: IngestRequest):
    # Placeholder — replace with real ingestion logic
    return IngestResponse(status="accepted", received=req.payload)
