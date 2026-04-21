# Serve the weekly incident report
from fastapi.responses import JSONResponse
import os

@app.get("/reports/weekly")
def get_weekly_report():
    report_path = os.path.join(os.path.dirname(__file__), "weekly_incident_report.json")
    if not os.path.exists(report_path):
        return {"error": "Weekly report not found. Please run the report generator."}
    with open(report_path, "r") as f:
        data = f.read()
    return JSONResponse(content=data, media_type="application/json")
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from chat import chat_handler
from servicenow import fetch_open_tickets
from prioritizer import prioritize_tickets_llm, generate_mitigation_plan
from similarity import find_similar_tickets
from summarizer import summarize

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

frontend_dir = Path(__file__).resolve().parent.parent / "frontend"
app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

@app.get("/")
def root():
    return FileResponse(frontend_dir / "index.html")

@app.post("/chat")
def chat(payload: dict):
    return chat_handler(payload)


# New endpoint: /tickets/prioritized
@app.get("/tickets/prioritized")
def get_prioritized_tickets():
    # 1. Fetch open tickets
    tickets = fetch_open_tickets(limit=20)
    if not tickets:
        return {"tickets": [], "error": "No open tickets found or ServiceNow unavailable."}

    # 2. Prioritize using OpenAI LLM
    prioritized = prioritize_tickets_llm(tickets)
    # 3. For each ticket, find similar tickets and suggest mitigation
    results = []
    for t in tickets:
        desc = t.get("description", "")
        similar = find_similar_tickets(desc)
        mitigation = summarize(similar, description=desc)
        # Find assigned priority if LLM returned it
        assigned_priority = None
        reason = None
        if isinstance(prioritized, list):
            for p in prioritized:
                if p.get("number") == t.get("number"):
                    assigned_priority = p.get("assigned_priority")
                    reason = p.get("reason")
                    break
        results.append({
            "number": t.get("number"),
            "short_description": t.get("short_description"),
            "description": t.get("description"),
            "priority": t.get("priority"),
            "assigned_priority": assigned_priority,
            "reason": reason,
            "mitigation": mitigation,
        })
    return {"tickets": results}
