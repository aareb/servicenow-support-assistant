# ServiceNow Support Assistant

## Overview
This project implements a FastAPI backend and a simple browser chat UI for a ServiceNow-style support bot. The bot:
- collects issue description
- asks whether the issue impacts production
- asks for the affected application/CI
- calculates priority
- looks up similar historical ticket mitigations
- creates a ServiceNow incident (or returns a mock incident ID if credentials are missing)

It also includes AI summarization support for mitigation guidance using OpenAI.

The current implementation is chat-oriented:
- the frontend shows a chat conversation
- the backend maintains per-user conversation state
- the bot asks follow-up questions to diagnose the issue
- once enough information is collected, it creates an incident and returns a mitigation summary

## Folder structure
- `backend/` — FastAPI app, bot logic, ServiceNow integration, session state, summarization
- `frontend/` — static HTML chat UI

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

## Environment variables
For full integration, set these variables before running the backend:

```powershell
$env:SN_INSTANCE_URL = "https://<your-instance>.service-now.com"
$env:SN_USER = "your_username"
$env:SN_PASS = "your_password"
$env:OPENAI_API_KEY = "sk-..."
```

If `SN_INSTANCE_URL`, `SN_USER`, or `SN_PASS` are not set, the app returns a mock incident ID.
If `OPENAI_API_KEY` is not set, mitigation summary falls back to the local historical resolution formatter.

## Local environment support
The backend now supports a `.env` file in `backend/` when you install `python-dotenv`.
A sample file is provided as `backend/.env.example`.

## Data and persistence improvements
- `backend/session.py` now persists session state in `backend/sessions.db`.
- `backend/similarity.py` uses fuzzy matching instead of simple keyword lookup.

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
