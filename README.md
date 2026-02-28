# Assessment 4 — ML Platform

## Overview
A production-grade ML platform deployed on AWS EKS. Three SageMaker endpoints are wrapped in FastAPI services and routed through a central gateway, with a React dashboard for interaction.

## Architecture
See [docs/architecture.md](docs/architecture.md) for the full architecture diagram.

## Services
| Service                 | Description                              |
|-------------------------|------------------------------------------|
| dashboard               | React UI served via nginx, public facing |
| gateway-service         | FastAPI gateway, explicit ML routing     |
| fraud-service           | XGBoost fraud detection via SageMaker    |
| recommendations-service | Factorization Machines via SageMaker     |
| forecasting-service     | DeepAR demand forecasting via SageMaker  |

## SageMaker Endpoints
| Endpoint                         | Algorithm | Purpose            |
|----------------------------------|-----------|--------------------|
| cams-fraud-endpoint-1771690056   | XGBoost   | Fraud Detection    |
| cams-recommendations-endpoint-v2 | FM        | Recommendations    |
| cams-forecasting-endpoint-v2     | DeepAR    | Demand Forecasting |

## Project Structure
```
assessment-4/
├── infrastructure/
│   ├── terraform/
│   │   ├── envs/dev/          # Terraform entry point
│   │   └── modules/eks/       # EKS module
│   └── k8s/                   # Kubernetes manifests
│       ├── namespaces/        # Namespace, ResourceQuota, LimitRange
│       ├── dashboard/
│       ├── gateway-service/
│       ├── fraud-service/
│       ├── recommendations-service/
│       ├── forecasting-service/
│       └── data-service/
├── services/
│   ├── dashboard/             # React + nginx
│   ├── gateway-service/       # FastAPI gateway
│   ├── fraud-service/         # FastAPI + SageMaker XGBoost
│   ├── recommendations-service/ # FastAPI + SageMaker FM
│   ├── forecasting-service/   # FastAPI + SageMaker DeepAR
│   └── data-service/          # FastAPI ingestion
├── docs/
│   └── architecture.md
└── .github/
    └── workflows/
        └── deploy.yaml        # CI/CD pipeline

## Setup

### Prerequisites
- AWS CLI configured with account 388691194728
- kubectl installed
- terraform >= 1.5.0
- docker buildx

### Connect to the cluster
```bash
aws eks update-kubeconfig --name k8s-training-cluster --region us-east-1
kubectl get nodes
```

### Terraform
```bash
cd infrastructure/terraform/envs/dev
terraform init
terraform plan
terraform apply
```

### Deploy all services
```bash
kubectl apply -f infrastructure/k8s/namespaces/
kubectl apply -f infrastructure/k8s/dashboard/
kubectl apply -f infrastructure/k8s/gateway-service/
kubectl apply -f infrastructure/k8s/fraud-service/
kubectl apply -f infrastructure/k8s/recommendations-service/
kubectl apply -f infrastructure/k8s/forecasting-service/
kubectl apply -f infrastructure/k8s/data-service/
```

### Get dashboard URL
```bash
kubectl get svc dashboard -n ml-platform
```

## CI/CD
Push to master triggers the GitHub Actions pipeline which:
1. Builds and pushes all service images to ECR
2. Deploys updated manifests to EKS
3. Verifies all rollouts complete successfully

## Scaling Up/Down
```bash
# Scale up
aws eks update-nodegroup-config   --cluster-name k8s-training-cluster   --nodegroup-name student-nodes   --scaling-config minSize=2,maxSize=4,desiredSize=2   --region us-east-1

# Scale down
aws eks update-nodegroup-config   --cluster-name k8s-training-cluster   --nodegroup-name student-nodes   --scaling-config minSize=0,maxSize=4,desiredSize=0   --region us-east-1
```

## Debugging Common Failures

### Pods not starting
```bash
kubectl describe pod <pod-name> -n ml-platform
kubectl logs <pod-name> -n ml-platform
```

### SageMaker calls failing
```bash
# Check AWS credentials secret exists
kubectl get secret aws-credentials -n ml-platform

# Check pod env vars
kubectl exec -n ml-platform <pod-name> -- env | grep AWS
```

### Dashboard not loading
```bash
# Check nginx logs
kubectl logs -n ml-platform -l app=dashboard

# Check NLB target health
aws elbv2 describe-target-health   --target-group-arn <arn>   --region us-east-1
```

### ResourceQuota exceeded
```bash
kubectl describe resourcequota ml-platform-quota -n ml-platform
```

### ECR auth expired
```bash
aws ecr get-login-password --region us-east-1 |   docker login --username AWS --password-stdin   388691194728.dkr.ecr.us-east-1.amazonaws.com
```
