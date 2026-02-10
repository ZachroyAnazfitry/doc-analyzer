# AWS deployment (ECS + ECR)

Deploy the Document Summarizer as a container on **Amazon ECS with Fargate**, with images stored in **Amazon ECR**. Budget-friendly for testing (e.g. under ~$50/month with light usage).

## Prerequisites

- AWS CLI installed and configured (`aws configure`)
- Docker installed (for building and pushing the image)

## 1. Create ECR repository

```bash
aws ecr create-repository --repository-name doc-analyzer --region us-east-1
```

Note the `repositoryUri` from the output (e.g. `123456789012.dkr.ecr.us-east-1.amazonaws.com/doc-analyzer`).

## 2. Build and push image

```bash
# Authenticate Docker to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 123456789012.dkr.ecr.us-east-1.amazonaws.com

# Build
docker build -t doc-analyzer .

# Tag and push (replace ACCOUNT and REGION)
docker tag doc-analyzer:latest ACCOUNT.dkr.ecr.REGION.amazonaws.com/doc-analyzer:latest
docker push ACCOUNT.dkr.ecr.REGION.amazonaws.com/doc-analyzer:latest
```

## 3. ECS: cluster, task definition, service

- **Cluster**: Create an ECS cluster (e.g. `doc-analyzer-cluster`) in the AWS Console or CLI.
- **Task definition**: Fargate, 0.25 vCPU, 0.5 GB memory (or 0.5 vCPU / 1 GB if the model needs more). Container: your ECR image, port 8000, env vars for `MODEL_NAME`, `MAX_LENGTH`, `MIN_LENGTH` if desired.
- **Service**: Create a service that runs the task definition. For minimal testing you can use a single task with a public IP and security group allowing inbound 8000 (or put an Application Load Balancer in front and use ALB port 80/443).

## 4. Test the deployed API

- **Postman**: Set the base URL to your ECS task public IP (or ALB URL) and port, e.g. `http://<task-ip>:8000`. Call `GET /health` and `POST /summarize` as in the README.
- **curl**: `curl http://<task-ip>:8000/health` and `curl -X POST http://<task-ip>:8000/summarize -H "Content-Type: application/json" -d '{"text":"Your text here"}'`

## 5. CI/CD with GitHub Actions

The repo includes `.github/workflows/ci-cd.yml` to build on push/PR and, on push to `main`, push the image to ECR and optionally update the ECS service. Configure GitHub secrets:

- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`

(Or use OIDC with AWS for better security.) Set ECR repository URI and ECS cluster/service name in the workflow or as repository variables.

## Cost notes

- **ECR**: Storage for a few images is usually under a dollar per month.
- **Fargate**: Billed per vCPU and memory per second. A small task (0.25 vCPU, 0.5 GB) running 24/7 is roughly in the low tens of dollars per month; scale to zero or stop the service when not testing to reduce cost.
- Use the [AWS Pricing Calculator](https://calculator.aws/) for your region and usage.
