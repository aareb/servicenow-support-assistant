# ServiceNow Virtual Agent REST Action Example

This file shows an example ServiceNow Virtual Agent REST action configuration for the Support Assistant prototype.

## REST message settings
- HTTP method: `POST`
- Endpoint URL: `http://<backend-host>:8000/chat`
- Authentication: none for local testing, or use a secure proxy / mid-tier in production
- Request headers:
  - `Content-Type: application/json`

## Request payload
Send the following JSON payload to `/chat`:

```json
{
  "user_id": "<user_id>",
  "message": "<user text>"
}
```

## Response payload
The backend returns JSON with a `reply` field. Example:

```json
{
  "reply": "Incident INC-0001 created\n Priority: P1\n..."
}
```

## Virtual Agent topic sample flow
1. Question: `Describe your issue.`
   - Save response to `issue_description`
2. Question: `What symptoms are you seeing?` 
   - Save response to `issue_symptoms`
3. Question: `Is this impacting production?`
   - Save response to `production_impact`
4. Question: `Which application or CI is impacted?`
   - Save response to `affected_ci`
5. REST Action:
   - `user_id` = A unique user/session identifier
   - `message` = `issue_description`

Since our backend currently manages the chat flow itself, the Virtual Agent should either:
- pass every user message through the same REST action, or
- map the current UI-style conversation into a single per-message webhook.

## Recommended integration pattern
The simplest ServiceNow integration for this prototype is:
- build a REST-triggered topic that sends a single message
- let the backend handle the multi-step conversation and state
- display the backend `reply` text as the topic response

## Notes
- For production, use ServiceNow credentials from the backend `.env` file.
- Keep the backend API protected and do not expose internal credentials through the UI.
