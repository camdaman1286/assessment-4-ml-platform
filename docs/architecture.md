# ML Platform Architecture

## Diagram

```mermaid
graph TD
    Internet([Internet])
    NLB[AWS Network Load Balancer<br/>internet-facing<br/>port 80]
    Dashboard[dashboard<br/>nginx + React<br/>ml-platform]
    Gateway[gateway-service<br/>FastAPI<br/>ml-platform]
    Fraud[fraud-service<br/>FastAPI<br/>ml-platform]
    Recommend[recommendations-service<br/>FastAPI<br/>ml-platform]
    Forecast[forecasting-service<br/>FastAPI<br/>ml-platform]
    SM_Fraud[(SageMaker<br/>XGBoost<br/>Fraud Endpoint)]
    SM_Rec[(SageMaker<br/>Factorization Machines<br/>Recommendations Endpoint)]
    SM_For[(SageMaker<br/>DeepAR<br/>Forecasting Endpoint)]

    Internet --> NLB
    NLB --> Dashboard
    Dashboard -->|/fraud| Gateway
    Dashboard -->|/recommend| Gateway
    Dashboard -->|/forecast| Gateway
    Gateway -->|/fraud| Fraud
    Gateway -->|/recommend| Recommend
    Gateway -->|/forecast| Forecast
    Fraud --> SM_Fraud
    Recommend --> SM_Rec
    Forecast --> SM_For
```

## Infrastructure
- EKS Cluster: k8s-training-cluster (us-east-1)
- Node Group: student-nodes (2x t3.medium)
- Namespaces: ml-platform
- State Backend: S3 (cams-tf-state-assessment-4) + DynamoDB lock

## Namespaces
| Namespace   | Services                                                       |
|-------------|----------------------------------------------------------------|
| ml-platform | gateway, fraud, recommendations, forecasting, dashboard  |

## SageMaker Endpoints
| Endpoint                         | Model              | Algorithm |
|----------------------------------|--------------------|-----------|
| cams-fraud-endpoint-1771690056   | Fraud Detection    | XGBoost   |
| cams-recommendations-endpoint-v2 | Recommendations    | FM        |
| cams-forecasting-endpoint-v2     | Demand Forecasting | DeepAR    |

## Resource Controls (ml-platform namespace)
| Resource  | Request | Limit |
|-----------|---------|-------|
| CPU       | 4       | 8     |
| Memory    | 4Gi     | 8Gi   |
| Max Pods  | 30      | -     |
