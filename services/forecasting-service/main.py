# forecasting-service: wraps the SageMaker DeepAR forecasting endpoint.
# Returns 7-day demand forecast given historical time series.
# Failure paths: model error, timeout, unavailable.

import os
import boto3
import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

app = FastAPI(title="forecasting-service")

ENDPOINT_NAME = os.getenv("SAGEMAKER_ENDPOINT", "cams-forecasting-endpoint-v2")
REGION = os.getenv("AWS_REGION", "us-east-1")

client = boto3.client("sagemaker-runtime", region_name=REGION)


class ForecastRequest(BaseModel):
    # At least 14 historical data points required (context_length)
    start: str
    target: List[float]


class ForecastResponse(BaseModel):
    endpoint: str
    start: str
    forecast: List[float]


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/ready")
def ready():
    return {"status": "ready"}


@app.post("/predict", response_model=ForecastResponse)
def predict(req: ForecastRequest):
    if len(req.target) < 14:
        raise HTTPException(
            status_code=400,
            detail="At least 14 historical data points required"
        )
    try:
        payload = json.dumps({
            "instances": [
                {"start": req.start, "target": req.target}
            ],
            "configuration": {
                "num_samples": 10,
                "output_types": ["mean"]
            }
        })

        response = client.invoke_endpoint(
            EndpointName=ENDPOINT_NAME,
            ContentType="application/json",
            Body=payload
        )
        result = json.loads(response["Body"].read().decode("utf-8"))
        forecast = result["predictions"][0]["mean"]
        return ForecastResponse(
            endpoint=ENDPOINT_NAME,
            start=req.start,
            forecast=forecast
        )
    except client.exceptions.ModelError as e:
        raise HTTPException(status_code=502, detail=f"Model error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=504, detail=f"Endpoint timeout or unavailable: {str(e)}")
