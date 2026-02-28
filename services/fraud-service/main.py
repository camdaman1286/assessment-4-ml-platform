# fraud-service: wraps the SageMaker XGBoost fraud detection endpoint.
# Model outputs inverted probabilities — lower score = higher fraud risk.
# Threshold set to 0.0001 based on empirical testing of output distribution.

import os
import boto3
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="fraud-service")

ENDPOINT_NAME = os.getenv("SAGEMAKER_ENDPOINT", "cams-fraud-endpoint-1771690056")
REGION = os.getenv("AWS_REGION", "us-east-1")
FRAUD_THRESHOLD = float(os.getenv("FRAUD_THRESHOLD", "0.0001"))

client = boto3.client("sagemaker-runtime", region_name=REGION)


class FraudRequest(BaseModel):
    features: str


class FraudResponse(BaseModel):
    endpoint: str
    fraud_score: float
    threshold: float
    prediction: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/ready")
def ready():
    return {"status": "ready"}


@app.post("/predict", response_model=FraudResponse)
def predict(req: FraudRequest):
    try:
        response = client.invoke_endpoint(
            EndpointName=ENDPOINT_NAME,
            ContentType="text/csv",
            Body=req.features,
        )
        result = float(response["Body"].read().decode("utf-8").strip())
        # Lower score = higher fraud risk based on model output distribution
        prediction = "fraudulent" if result < FRAUD_THRESHOLD else "legitimate"
        return FraudResponse(
            endpoint=ENDPOINT_NAME,
            fraud_score=result,
            threshold=FRAUD_THRESHOLD,
            prediction=prediction
        )
    except client.exceptions.ModelError as e:
        raise HTTPException(status_code=502, detail=f"Model error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=504, detail=f"Endpoint timeout or unavailable: {str(e)}")
