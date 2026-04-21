# AWS Deployment Plan for ServiceNow Support Assistant Accelerator


This plan uses AWS ECS/Fargate for the backend, S3 + CloudFront for the frontend, RDS or DynamoDB for session persistence, and Secrets Manager for secure credentials. The solution now includes:

- Prioritized ticket dashboard in the frontend (OpenAI-powered)
- /tickets/prioritized API endpoint for ticket triage and mitigation
- Automated CI/CD with GitHub Actions and Terraform


## Architecture Overview

- `backend/` containerized with Docker and deployed to **Amazon ECS / Fargate**
- `frontend/` static assets hosted on **Amazon S3** and delivered through **Amazon CloudFront**
- session state stored in **Amazon RDS** or **Amazon DynamoDB**
- secrets stored in **AWS Secrets Manager**
- backend environment variables injected into ECS task definitions
- logs written to **Amazon CloudWatch Logs**
- **Prioritized ticket dashboard**: OpenAI LLM ranks and explains open ServiceNow tickets, generates mitigation plans
- **/tickets/prioritized** API endpoint for frontend and integrations
- **CI/CD**: GitHub Actions workflow for build, deploy, and infrastructure

## Service Choices

### 1. Container registry
- **Amazon ECR**
- store the backend Docker image in a private ECR repository

### 2. Backend runtime
- **Amazon ECS** with **Fargate launch type**
- use an **Application Load Balancer (ALB)**
- place ECS tasks in private subnets

### 3. Frontend hosting
- **Amazon S3** bucket configured for static website hosting
- **Amazon CloudFront** distribution in front of the S3 bucket
- use **AWS Certificate Manager (ACM)** for HTTPS

### 4. Session persistence
Choose one:
- **Amazon RDS** (PostgreSQL or MySQL)
  - good for relational session data and future SQL queries
- **Amazon DynamoDB**
  - good for serverless, high-throughput session storage

### 5. Secrets and environment
- **AWS Secrets Manager** for:
  - `SN_INSTANCE_URL`
  - `SN_USER`
  - `SN_PASS`
  - `OPENAI_API_KEY`
  - optional: `OPENAI_MODEL`, `OPENAI_API_URL`
- Inject secrets into ECS task environment variables

### 6. Observability
- **Amazon CloudWatch Logs** for ECS task output
- optional **CloudWatch Alarms** for error rates / task failures


## Deployment Steps

### A. CI/CD Pipeline (Recommended)
1. Configure GitHub repository secrets for AWS credentials and resource names.
2. Edit `.github/workflows/deploy.yml` with your ECR repo, S3 bucket, and CloudFront distribution ID.
3. On every push to `main`, the workflow will:
   - Build and push backend Docker image to ECR
   - Apply Terraform to provision/update AWS infrastructure
   - Sync frontend to S3 and invalidate CloudFront

### B. Manual Steps (if not using CI/CD)
1. Build and push Docker image (see previous instructions)
2. Provision session storage (RDS or DynamoDB)
3. Configure AWS Secrets Manager for ServiceNow and OpenAI credentials
4. Deploy frontend to S3 and invalidate CloudFront
   - `SN_INSTANCE_URL`
   - `SN_USER`
   - `SN_PASS`
   - `OPENAI_API_KEY`
   - `OPENAI_MODEL`
   - `OPENAI_API_URL`
4. Grant ECS task execution role permission to read the secret.

### D. Deploy backend to ECS/Fargate
1. Create an ECS cluster.
2. Create a task definition with:
   - container image from ECR
   - port `8000`
   - environment variables or secrets from Secrets Manager
   - log configuration for CloudWatch
3. Create an ALB and target group pointing to Fargate tasks.
4. Create an ECS service using Fargate and attach it to the ALB.
5. Use security groups to allow inbound HTTPS from CloudFront or public access if needed.

### E. Host frontend on S3 and CloudFront
1. Create an S3 bucket, e.g. `servicenow-support-assistant-frontend`.
2. Upload the `frontend/` assets.
3. Configure public read or CloudFront origin access identity.
4. Create a CloudFront distribution with the S3 bucket as origin.
5. Use ACM to provision an HTTPS certificate for your domain.
6. Optionally use a custom domain and Route 53.

### F. Connect frontend to backend
1. If backend is public, update the frontend fetch URL in `frontend/index.html` to use the ALB or CloudFront domain.
2. Recommended: use an environment or config value for the backend API base URL.
3. If hosting site behind CloudFront, configure CORS on the backend and allow the CloudFront domain.

## Concrete service mapping

- **Backend**: ECS + Fargate, ECR, ALB
- **Frontend**: S3, CloudFront, ACM
- **Secrets**: Secrets Manager
- **Session store**: RDS PostgreSQL / MySQL *or* DynamoDB
- **Logs**: CloudWatch Logs

## Minimal Dockerfile

This Dockerfile builds the backend container and includes the frontend assets so the app can serve the static UI if needed.

```dockerfile
# backend/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY backend/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy backend and frontend content
COPY backend /app/backend
COPY frontend /app/frontend

WORKDIR /app/backend

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Notes on session persistence

The current code uses SQLite in `backend/session.py`.
For AWS, you should replace this with either:

- **RDS**: connect to PostgreSQL/MySQL using a DB driver such as `psycopg2-binary`, or
- **DynamoDB**: use `boto3` and a DynamoDB table for session state.

## Example ECS task environment variables

- `SN_INSTANCE_URL`
- `SN_USER`
- `SN_PASS`
- `OPENAI_API_KEY`
- `OPENAI_MODEL`
- `OPENAI_API_URL`
- `SESSION_DB` (if still using local SQLite during development)

## Optional advanced enhancements

- Add **AWS WAF** for security
- Use **Route 53** and custom domain for CloudFront
- Add **CloudWatch Alarms** for 5xx errors / task failures
- Use **AWS CodePipeline** or GitHub Actions for CI/CD

## Summary

This plan is ready for a proper AWS accelerator deployment. The Dockerfile is minimal and supports the existing backend. The next steps are:

1. decide session storage: RDS or DynamoDB
2. build and push the Docker image to ECR
3. deploy backend on ECS/Fargate behind ALB
4. host frontend on S3 + CloudFront
5. secure secrets with Secrets Manager
