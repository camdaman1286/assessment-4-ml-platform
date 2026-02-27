# recommendations-service: wraps the SageMaker FM recommendations endpoint.
# Returns recommendation score and predicted label for user-item pairs.
# Failure paths: model error, timeout, unavailable.

import os
import boto3
import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

app = FastAPI(title="recommendations-service")

ENDPOINT_NAME = os.getenv("SAGEMAKER_ENDPOINT", "cams-recommendations-endpoint-v2")
REGION = os.getenv("AWS_REGION", "us-east-1")
N_USERS = 100
N_ITEMS = 50

client = boto3.client("sagemaker-runtime", region_name=REGION)


class RecommendRequest(BaseModel):
    user_id: int
    item_id: int


class RecommendResponse(BaseModel):
    endpoint: str
    user_id: int
    item_id: int
    score: float
    recommended: bool


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/ready")
def ready():
    return {"status": "ready"}


@app.post("/predict", response_model=RecommendResponse)
def predict(req: RecommendRequest):
    if req.user_id >= N_USERS or req.item_id >= N_ITEMS:
        raise HTTPException(status_code=400, detail="user_id or item_id out of range")

    try:
        feature_vec = [0.0] * (N_USERS + N_ITEMS)
        feature_vec[req.user_id] = 1.0
        feature_vec[N_USERS + req.item_id] = 1.0

        payload = json.dumps({"instances": [{"features": feature_vec}]})

        response = client.invoke_endpoint(
            EndpointName=ENDPOINT_NAME,
            ContentType="application/json",
            Body=payload
        )
        result = json.loads(response["Body"].read().decode("utf-8"))
        score = result["predictions"][0]["score"]
        return RecommendResponse(
            endpoint=ENDPOINT_NAME,
            user_id=req.user_id,
            item_id=req.item_id,
            score=score,
            recommended=score > 0.5
        )
    except client.exceptions.ModelError as e:
        raise HTTPException(status_code=502, detail=f"Model error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=504, detail=f"Endpoint timeout or unavailable: {str(e)}")
