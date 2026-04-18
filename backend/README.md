# Support Assistant Backend

## Purpose
This backend supports the ServiceNow Support Assistant prototype by:
- hosting the chat API
- managing conversation state
- creating ServiceNow incidents
- summarizing mitigation recommendations
- using historical ticket data for similarity matching

## Quick start

1. Install dependencies:
```powershell
cd "c:\Users\ba\OneDrive - ALLEGIS GROUP\Desktop\ServiceNow_Support_Accelerator\Support-assisstant\backend"
pip install -r requirements.txt
```

2. Create `.env` from the example:
```powershell
copy .env.example .env
```

3. Edit `backend/.env` with your ServiceNow and OpenAI values.

4. Run the backend:
```powershell
uvicorn main:app --reload
```

5. Open the frontend in your browser:
```text
http://127.0.0.1:8000
```

## Files
- `main.py` — FastAPI app, CORS, and static UI delivery
- `chat.py` — conversation orchestration and incident creation flow
- `session.py` — persistent SQLite-based session storage
- `prioritizer.py` — priority generation logic
- `similarity.py` — fuzzy matching against historical ticket data
- `summarizer.py` — optional OpenAI mitigation summarization
- `servicenow.py` — ServiceNow REST incident creation
- `historical_tickets.json` — sample historical ticket data

## Environment variables
The backend reads these variables from `.env` or the shell:
- `SN_INSTANCE_URL`
- `SN_USER`
- `SN_PASS`
- `SN_TABLE_NAME` (default: `incident`)
- `OPENAI_API_KEY`
- `OPENAI_MODEL` (default: `gpt-3.5-turbo`)
- `OPENAI_API_URL`
- `SESSION_DB` (default: `sessions.db`)

## ServiceNow REST action example
See `servicenow_rest_action_example.md` for the Virtual Agent REST action configuration.
