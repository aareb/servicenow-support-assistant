# ServiceNow Support Assistant

## Overview

This project implements a FastAPI backend and a browser-based UI for a ServiceNow-style support accelerator. The solution now includes:

- **Conversational chat bot** for incident creation and diagnosis
- **Prioritized ticket dashboard**: View open ServiceNow tickets, prioritized and explained by OpenAI, with mitigation plans
- **OpenAI-powered prioritization and mitigation**: Uses LLMs to rank tickets and generate root cause/mitigation for new issues
- **Historical ticket similarity**: Finds and summarizes mitigations from past incidents
- **ServiceNow integration**: Create and read incidents via REST API
- **CI/CD**: Automated build, deploy, and infrastructure provisioning with GitHub Actions and Terraform

The frontend now has two main features:
- Chat conversation for new issues
- Live dashboard of prioritized open tickets with mitigation plans


## Folder structure
- `backend/` — FastAPI app, bot logic, ServiceNow integration, session state, OpenAI, prioritization, mitigation
- `frontend/` — static HTML chat UI and ticket dashboard
- `terraform/` — AWS infrastructure as code
- `.github/workflows/` — CI/CD pipeline for build and deploy

## Prerequisites
- Python 3.10+ installed
- `pip` available
- Optional: ServiceNow credentials and OpenAI API key for real incident creation and AI summarization

## Install dependencies
Open a terminal and run:

```powershell
cd "c:\Users\ba\OneDrive - ALLEGIS GROUP\Desktop\ServiceNow_Support_Accelerator\Support-assisstant\backend"
pip install -r requirements.txt
```

If you are missing `uvicorn`, install it with the same command above.


## Run locally
From `Support-assisstant/backend`:

```powershell
uvicorn main:app --reload
```

Then open:

```text
http://127.0.0.1:8000
```

To view prioritized tickets and mitigation plans, use the dashboard in the UI or call:

```http
GET /tickets/prioritized
```


## Environment variables
For full integration, set these variables before running the backend:

```powershell
$env:SN_INSTANCE_URL = "https://<your-instance>.service-now.com"
$env:SN_USER = "your_username"
$env:SN_PASS = "your_password"
$env:OPENAI_API_KEY = "sk-..."
$env:OPENAI_MODEL = "gpt-3.5-turbo"  # optional
$env:OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"  # optional
```

If ServiceNow or OpenAI variables are not set, the app falls back to mock or local logic.

## Local environment support
The backend now supports a `.env` file in `backend/` when you install `python-dotenv`.
A sample file is provided as `backend/.env.example`.


## Data and persistence improvements
- `backend/session.py` persists session state in SQLite (or can be extended to DynamoDB/RDS)
- `backend/similarity.py` uses fuzzy matching for similar tickets


## CI/CD and Deployment
- See `.github/workflows/deploy.yml` for a full GitHub Actions pipeline: builds Docker, pushes to ECR, applies Terraform, syncs frontend to S3, and invalidates CloudFront
- See `terraform/` for AWS infrastructure: ECS, S3, CloudFront, RDS/DynamoDB, Secrets Manager, ALB, etc.

## ServiceNow Virtual Agent integration
Use a Virtual Agent topic in ServiceNow to collect:
- `issue_description`
- `production_impact`
- `affected_ci`

Then call the backend REST endpoint at:

```text
POST http://<backend-host>:8000/chat
```

Request payload:

```json
{
  "user_id": "<user-id>",
  "message": "<user text>"
}
```

The backend returns a JSON response with `reply` containing the next question or final incident summary.

## How the topic maps to code
- `backend/main.py` — FastAPI app and static file route
- `backend/chat.py` — multi-step conversation and incident creation
- `backend/session.py` — per-user session state
- `backend/prioritizer.py` — priority logic
- `backend/servicenow.py` — ServiceNow incident creation
- `backend/summarizer.py` — AI-assisted mitigation summary
- `frontend/index.html` — browser chat UI

## Notes
- The frontend sends messages to `/chat` and displays bot responses.
- The current system is a good prototype for a ServiceNow Virtual Agent REST action.
- For production, secure credentials and protect the backend endpoint.
- Session state is now persisted in SQLite via `backend/session.py`.

## Additional docs
- See `backend/README.md` for backend quick-start and configuration.
- See `backend/servicenow_rest_action_example.md` for a ServiceNow REST action example.
