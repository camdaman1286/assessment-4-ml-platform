# gateway-service: API gateway — routes requests to downstream services.
# /health   — liveness probe
# /ready    — readiness probe
# /predict  — proxies to model-service
# /ingest   — proxies to data-service

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx
import os

app = FastAPI(title="gateway-service")

MODEL_SERVICE_URL = os.getenv("MODEL_SERVICE_URL", "http://model-service")
DATA_SERVICE_URL = os.getenv("DATA_SERVICE_URL", "http://data-service")


class PredictRequest(BaseModel):
    input: str


class IngestRequest(BaseModel):
    payload: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/ready")
def ready():
    return {"status": "ready"}


@app.post("/predict")
async def predict(req: PredictRequest):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{MODEL_SERVICE_URL}/predict",
                json=req.model_dump(),
                timeout=10.0
            )
            return response.json()
        except httpx.RequestError as e:
            raise HTTPException(status_code=502, detail=str(e))


@app.post("/ingest")
async def ingest(req: IngestRequest):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{DATA_SERVICE_URL}/ingest",
                json=req.model_dump(),
                timeout=10.0
            )
            return response.json()
        except httpx.RequestError as e:
            raise HTTPException(status_code=502, detail=str(e))
