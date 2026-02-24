# model-service: placeholder ML inference service.
# /health  — liveness probe (is the process alive?)
# /ready   — readiness probe (is the service ready to serve traffic?)
# /predict — inference endpoint (placeholder)

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="model-service")


class PredictRequest(BaseModel):
    input: str


class PredictResponse(BaseModel):
    prediction: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/ready")
def ready():
    return {"status": "ready"}


@app.post("/predict", response_model=PredictResponse)
def predict(req: PredictRequest):
    # Placeholder — replace with real model inference logic
    return PredictResponse(prediction=f"echo: {req.input}")
