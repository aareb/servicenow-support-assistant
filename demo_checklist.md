# ServiceNow Support Assistant Demo Checklist

## Pre-Demo Setup (15 minutes)
-  Ensure Python 3.10+ is installed
-  Navigate to `Support-assisstant/backend`
-  Run `pip install -r requirements.txt`
-  Copy `.env.example` to `.env` and configure:
  - `SN_INSTANCE_URL` (optional for mock mode)
  - `SN_USER` and `SN_PASS` (optional)
  - `OPENAI_API_KEY` (optional for AI summarization)
-  Start backend: `uvicorn main:app --reload`
-  Open browser to `http://127.0.0.1:8000`

## Demo Flow (10 minutes)
-  Show welcome message in chat UI
-  Type issue description: "Login page fails after deployment"
-  Answer symptoms: "Users see error 500"
-  Answer impact: "Yes, production users affected"
-  Answer CI: "Authentication service"
-  Show incident creation response with priority and mitigation
-  Demonstrate reset: Type "reset" and start new issue

## Key Features to Highlight
-  Chat-oriented diagnosis (not form-based)
-  Persistent session state (survives restarts)
-  Fuzzy similarity matching to historical tickets
-  ServiceNow incident creation (mock or real)
-  AI summarization (if OpenAI key provided)
-  Clean web UI for end-user experience

## Post-Demo Notes
-  Mention accelerator nature: Ready for ServiceNow VA integration
-  Reference docs: `backend/README.md`, `servicenow_rest_action_example.md`
-  Note production hardening needed: Security, logging, etc.

## Troubleshooting
- If backend fails: Check `.env` and dependencies
- If chat doesn't respond: Verify `uvicorn` is running on port 8000
- For real ServiceNow: Ensure credentials are correct in `.env`
