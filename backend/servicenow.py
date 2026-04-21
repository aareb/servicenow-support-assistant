import os
import requests


def create_incident(description, priority, ci):
    instance_url = os.getenv("SN_INSTANCE_URL")
    username = os.getenv("SN_USER")
    password = os.getenv("SN_PASS")
    table_name = os.getenv("SN_TABLE_NAME", "incident")

    if not (instance_url and username and password):
        return "INC-MOCK-0001"

    url = f"{instance_url.rstrip('/')}/api/now/table/{table_name}"
    payload = {
        "short_description": description[:160],
        "description": description,
        "impact": "1" if priority == "P1" else "2",
        "urgency": "1" if priority == "P1" else "2",
        "priority": "1" if priority == "P1" else "2",
        "cmdb_ci": ci,
    }
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    try:
        response = requests.post(url, auth=(username, password), json=payload, headers=headers, timeout=20)
        response.raise_for_status()
        result = response.json().get("result", {})
        return result.get("number", "INC-UNKNOWN")
    except requests.RequestException as exc:
        return f"INC-ERR-{response.status_code if 'response' in locals() else 'NO_RESP'}"
    except Exception:
        return "INC-ERR"


# New function: fetch open tickets from ServiceNow

def fetch_open_tickets(limit=20, extra_query=None):
    instance_url = os.getenv("SN_INSTANCE_URL")
    username = os.getenv("SN_USER")
    password = os.getenv("SN_PASS")
    table_name = os.getenv("SN_TABLE_NAME", "incident")

    if not (instance_url and username and password):
        return []

    url = f"{instance_url.rstrip('/')}/api/now/table/{table_name}"
    base_query = "active=true"
    if extra_query:
        base_query += f"^{extra_query}"
    params = {
        "sysparm_query": base_query,
        "sysparm_limit": str(limit),
        "sysparm_fields": "number,short_description,description,priority,impact,urgency,state,sys_created_on"
    }
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
    }
    try:
        response = requests.get(url, auth=(username, password), params=params, headers=headers, timeout=20)
        response.raise_for_status()
        return response.json().get("result", [])
    except Exception:
        return []
