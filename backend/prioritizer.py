def calculate_priority(session):
    if session.impact == "high":
        return "P1"
    return "P2"


# New: Prioritize a list of tickets using OpenAI LLM
import os
import requests

def prioritize_tickets_llm(tickets):
    api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    endpoint = os.getenv("OPENAI_API_URL", "https://api.openai.com/v1/chat/completions")
    if not api_key or not tickets:
        # fallback: sort by urgency/priority field if present
        return sorted(tickets, key=lambda t: (t.get("priority", "3"), t.get("urgency", "3")))

    prompt = """You are an IT support assistant. Given the following open ServiceNow tickets, assign a priority (High, Medium, Low) to each, and briefly explain your reasoning. Return as a JSON list with fields: number, assigned_priority, reason.\n\n"""
    for t in tickets:
        desc = t.get("short_description") or t.get("description") or ""
        prompt += f"Ticket {t.get('number', 'N/A')}: {desc}\n"
    prompt += "\nOutput:"

    try:
        response = requests.post(
            endpoint,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": model,
                "messages": [
                    {"role": "system", "content": "You are an IT support assistant."},
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0.2,
                "max_tokens": 500,
            },
            timeout=20,
        )
        response.raise_for_status()
        import json as _json
        content = response.json()["choices"][0]["message"]["content"]
        # Try to extract JSON from the response
        start = content.find("[")
        end = content.rfind("]")
        if start != -1 and end != -1:
            return _json.loads(content[start:end+1])
        return content
    except Exception as e:
        return tickets

# New: Generate root cause and mitigation plan for a ticket using OpenAI
def generate_mitigation_plan(ticket):
    api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    endpoint = os.getenv("OPENAI_API_URL", "https://api.openai.com/v1/chat/completions")
    if not api_key:
        return "No mitigation plan available."
    desc = ticket.get("short_description") or ticket.get("description") or ""
    prompt = f"Given this ServiceNow incident: '{desc}', generate a possible root cause and a step-by-step mitigation plan."
    try:
        response = requests.post(
            endpoint,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": model,
                "messages": [
                    {"role": "system", "content": "You are an IT support incident response assistant."},
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0.3,
                "max_tokens": 300,
            },
            timeout=15,
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"].strip()
    except Exception:
        return "No mitigation plan available."