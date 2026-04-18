# ServiceNow Virtual Agent Topic: Support Incident Creation

## Topic name
Create Support Incident

## Topic inputs
- issue_description
- production_impact
- affected_ci

## Conversation flow
1. Ask user to describe the issue.
2. Ask if it is impacting production users.
3. Ask for the application, service, or CI affected.
4. Summarize mitigation actions from historical resolutions.
5. Create a ServiceNow incident and return the incident number.

## Virtual Agent topic actions
- Collect `issue_description` in the first question.
- Collect `production_impact` in the second question.
- Collect `affected_ci` in the third question.
- Call the external FastAPI webhook (`/chat`) with the collected values.
- Display the incident number and recommended mitigation back to the user.

## Implementation mapping
- `backend/main.py` -> FastAPI app and static web UI endpoint.
- `backend/chat.py` -> Topic conversation state and ServiceNow incident workflow.
- `backend/session.py` -> Session state tracking between topic questions.
- `backend/prioritizer.py` -> Priority calculation based on impact.
- `backend/servicenow.py` -> ServiceNow REST incident creation.
- `backend/summarizer.py` -> AI summarization for mitigation guidance.
- `frontend/index.html` -> Web chat UI for the virtual agent conversation.

## ServiceNow configuration
- Use a ServiceNow Virtual Agent topic to collect the three slots.
- Connect the topic to the FastAPI backend via a REST action.
- Use environment variables for credentials:
  - `SN_INSTANCE_URL`
  - `SN_USER`
  - `SN_PASS`
  - `OPENAI_API_KEY` (optional for AI summarization)

## REST action example
- See `backend/servicenow_rest_action_example.md` for a sample Virtual Agent REST action and payload.
