# Terraform Starter for ServiceNow Support Assistant

This Terraform starter provisions the AWS infrastructure for the accelerator using ECS/Fargate, S3/CloudFront, Secrets Manager, and either DynamoDB or RDS for session persistence.

## What it creates

- **VPC** with public and private subnets
- **ECR repository** for backend Docker image
- **S3 bucket** for frontend assets
- **CloudFront distribution** for static frontend delivery
- **Secrets Manager secrets** for ServiceNow/OpenAI credentials
- **ECS cluster** and **Fargate service** for backend deployment
- **Application Load Balancer** with target group
- **DynamoDB table** for sessions, or **RDS database** when enabled
- **CloudWatch logs** for ECS container output

## How to use

1. Change to the Terraform directory:
   ```powershell
   cd "c:\Users\ba\OneDrive - ALLEGIS GROUP\Desktop\ServiceNow_Support_Accelerator\Support-assisstant\terraform"
   ```

2. Initialize Terraform:
   ```powershell
   terraform init
   ```

3. Review the plan:
   ```powershell
   terraform plan
   ```

4. Apply the configuration:
   ```powershell
   terraform apply
   ```

5. After apply, review the outputs for the frontend CloudFront domain and backend ALB DNS name.

## Notes

- By default, this starter enables **DynamoDB** for session persistence.
- To use **RDS** instead, set `create_rds = true` and `create_dynamodb = false`.
- If you want CloudFront to use a custom domain, set `frontend_domain_name` and `certificate_arn`.
- Upload additional frontend assets to the S3 bucket after provisioning, or extend the Terraform config to include more assets.

## Backend image deployment

The Terraform config creates an ECR repository.
Build and push your backend image from `Support-assisstant`:

```powershell
cd "c:\Users\ba\OneDrive - ALLEGIS GROUP\Desktop\ServiceNow_Support_Accelerator\Support-assisstant"
docker build -t servicenow-support-assistant -f backend/Dockerfile .
aws ecr get-login-password --region <region> | docker login --username AWS --password-stdin <account-id>.dkr.ecr.<region>.amazonaws.com
docker tag servicenow-support-assistant:latest <account-id>.dkr.ecr.<region>.amazonaws.com/servicenow-support-assistant-backend:latest
docker push <account-id>.dkr.ecr.<region>.amazonaws.com/servicenow-support-assistant-backend:latest
```

## Secrets

Use Terraform variables to provide:
- `sn_instance_url`
- `sn_user`
- `sn_pass`
- `openai_api_key`

The secrets are stored in AWS Secrets Manager and injected into the ECS task definition.

## Cleanup

To remove resources:

```powershell
terraform destroy
```
