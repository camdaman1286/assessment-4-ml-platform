# fraud-service: wraps the SageMaker XGBoost fraud detection endpoint.
# Returns fraud probability and binary classification.
# Failure paths: model error, timeout, unavailable.

import os
import boto3
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="fraud-service")

ENDPOINT_NAME = os.getenv("SAGEMAKER_ENDPOINT", "cams-fraud-endpoint-1771690056")
REGION = os.getenv("AWS_REGION", "us-east-1")

client = boto3.client("sagemaker-runtime", region_name=REGION)


class FraudRequest(BaseModel):
    # Comma-separated feature values for XGBoost
    features: str


class FraudResponse(BaseModel):
    endpoint: str
    fraud_probability: float
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
        prediction = "fraudulent" if result > 0.5 else "legitimate"
        return FraudResponse(
            endpoint=ENDPOINT_NAME,
            fraud_probability=result,
            prediction=prediction
        )
    except client.exceptions.ModelError as e:
        raise HTTPException(status_code=502, detail=f"Model error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=504, detail=f"Endpoint timeout or unavailable: {str(e)}")
