# gateway-service: routes requests to the correct downstream service.
# Explicit routing — each endpoint maps to exactly one service.
# Failure paths: timeout (504), model error (502), propagated upstream.

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import httpx
import os

app = FastAPI(title="gateway-service")

MODEL_SERVICE_URL    = os.getenv("MODEL_SERVICE_URL", "http://model-service.default.svc.cluster.local")
DATA_SERVICE_URL     = os.getenv("DATA_SERVICE_URL", "http://data-service.ml-platform.svc.cluster.local")
FRAUD_SERVICE_URL    = os.getenv("FRAUD_SERVICE_URL", "http://fraud-service.ml-platform.svc.cluster.local")
RECOMMEND_SERVICE_URL = os.getenv("RECOMMEND_SERVICE_URL", "http://recommendations-service.ml-platform.svc.cluster.local")
FORECAST_SERVICE_URL = os.getenv("FORECAST_SERVICE_URL", "http://forecasting-service.ml-platform.svc.cluster.local")

TIMEOUT = 10.0


class PredictRequest(BaseModel):
    input: str


class IngestRequest(BaseModel):
    payload: str


class FraudRequest(BaseModel):
    features: str


class RecommendRequest(BaseModel):
    user_id: int
    item_id: int


class ForecastRequest(BaseModel):
    start: str
    target: List[float]


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
            r = await client.post(f"{MODEL_SERVICE_URL}/predict", json=req.model_dump(), timeout=TIMEOUT)
            return r.json()
        except httpx.TimeoutException:
            raise HTTPException(status_code=504, detail="model-service timed out")
        except httpx.RequestError as e:
            raise HTTPException(status_code=502, detail=str(e))


@app.post("/ingest")
async def ingest(req: IngestRequest):
    async with httpx.AsyncClient() as client:
        try:
            r = await client.post(f"{DATA_SERVICE_URL}/ingest", json=req.model_dump(), timeout=TIMEOUT)
            return r.json()
        except httpx.TimeoutException:
            raise HTTPException(status_code=504, detail="data-service timed out")
        except httpx.RequestError as e:
            raise HTTPException(status_code=502, detail=str(e))


@app.post("/fraud")
async def fraud(req: FraudRequest):
    # Explicit routing — only fraud-service handles this endpoint
    async with httpx.AsyncClient() as client:
        try:
            r = await client.post(f"{FRAUD_SERVICE_URL}/predict", json=req.model_dump(), timeout=TIMEOUT)
            if r.status_code == 502:
                raise HTTPException(status_code=502, detail="fraud-service model error")
            if r.status_code == 504:
                raise HTTPException(status_code=504, detail="fraud-service timed out")
            return r.json()
        except httpx.TimeoutException:
            raise HTTPException(status_code=504, detail="fraud-service timed out")
        except httpx.RequestError as e:
            raise HTTPException(status_code=502, detail=str(e))


@app.post("/recommend")
async def recommend(req: RecommendRequest):
    # Explicit routing — only recommendations-service handles this endpoint
    async with httpx.AsyncClient() as client:
        try:
            r = await client.post(f"{RECOMMEND_SERVICE_URL}/predict", json=req.model_dump(), timeout=TIMEOUT)
            if r.status_code == 502:
                raise HTTPException(status_code=502, detail="recommendations-service model error")
            if r.status_code == 504:
                raise HTTPException(status_code=504, detail="recommendations-service timed out")
            return r.json()
        except httpx.TimeoutException:
            raise HTTPException(status_code=504, detail="recommendations-service timed out")
        except httpx.RequestError as e:
            raise HTTPException(status_code=502, detail=str(e))


@app.post("/forecast")
async def forecast(req: ForecastRequest):
    # Explicit routing — only forecasting-service handles this endpoint
    async with httpx.AsyncClient() as client:
        try:
            r = await client.post(f"{FORECAST_SERVICE_URL}/predict", json=req.model_dump(), timeout=TIMEOUT)
            if r.status_code == 502:
                raise HTTPException(status_code=502, detail="forecasting-service model error")
            if r.status_code == 504:
                raise HTTPException(status_code=504, detail="forecasting-service timed out")
            return r.json()
        except httpx.TimeoutException:
            raise HTTPException(status_code=504, detail="forecasting-service timed out")
        except httpx.RequestError as e:
            raise HTTPException(status_code=502, detail=str(e))
