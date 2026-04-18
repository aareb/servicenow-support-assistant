# ServiceNow Support Assistant Demo Script

## Introduction (1 minute)
"Good [morning/afternoon], everyone. Today, I'll demonstrate the ServiceNow Support Assistant accelerator — a chat-based bot that helps users diagnose IT issues, create incidents, and get mitigation recommendations. This prototype shows how a ServiceNow Virtual Agent could work with AI and historical data."

## Setup Overview (30 seconds)
"This is built with FastAPI for the backend, a simple web UI for the chat, and integrates with ServiceNow for incident creation. It uses persistent sessions, fuzzy matching for similar tickets, and optional OpenAI summarization."

## Live Demo (5 minutes)
### Step 1: Start the Chat
"Let's start by opening the web UI. As you can see, the bot greets the user and asks for the issue description."

### Step 2: Describe the Issue
"I'll type a common problem: 'Login page fails after deployment.' The bot then asks for symptoms to better understand the issue."

### Step 3: Provide Symptoms
"Symptoms: 'Users see error 500.' Now it asks about production impact."

### Step 4: Impact Assessment
"Yes, this is impacting production users. The bot calculates priority based on this."

### Step 5: Affected CI
"Affected CI: 'Authentication service.'"

### Step 6: Incident Creation and Response
"Here we go — the bot creates an incident, assigns priority P1, summarizes the diagnosis, and provides mitigation steps from similar historical tickets. If OpenAI is configured, it summarizes the recommendations intelligently."

### Step 7: Reset and New Issue
"To show persistence, I can type 'reset' and start a new issue. The session state is saved in SQLite, so it survives backend restarts."

## Key Benefits (2 minutes)
- **Chat-Oriented**: Users diagnose through conversation, not forms.
- **Intelligent Matching**: Uses fuzzy logic to find similar past incidents.
- **Incident Creation**: Directly creates ServiceNow incidents with proper fields.
- **AI Enhancement**: Optional summarization for better mitigation guidance.
- **Accelerator Ready**: Easy to integrate into ServiceNow Virtual Agent via REST actions.

## Technical Highlights (1 minute)
- Backend: FastAPI with persistent SQLite sessions.
- Similarity: difflib for fuzzy matching against historical data.
- ServiceNow: REST API integration with environment-based credentials.
- UI: Clean chat interface for end-user experience.

## Next Steps (30 seconds)
"This is a production-ready prototype. For full deployment, we'd add security, logging, and ServiceNow VA topic configuration. The code is open on GitHub for review."

## Q&A (2 minutes)
"Any questions? I'd be happy to dive deeper into the code or integration details."