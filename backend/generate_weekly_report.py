import os
import json
from datetime import datetime, timedelta
from servicenow import fetch_open_tickets

def fetch_weekly_tickets():
    # Calculate date range for the past week
    today = datetime.utcnow()
    last_week = today - timedelta(days=7)
    # ServiceNow sys_created_on format: yyyy-MM-dd HH:mm:ss
    date_query = f"sys_created_on>={last_week.strftime('%Y-%m-%d')}"
    tickets = fetch_open_tickets(limit=1000, extra_query=date_query)
    return tickets

def summarize_tickets(tickets):
    summary = {}
    for t in tickets:
        priority = t.get('priority', 'Unknown')
        state = t.get('state', 'Unknown')
        summary.setdefault(priority, {})
        summary[priority].setdefault(state, 0)
        summary[priority][state] += 1
    return summary

def save_report(summary, tickets):
    report = {
        'generated_at': datetime.utcnow().isoformat(),
        'summary': summary,
        'tickets': tickets
    }
    with open('weekly_incident_report.json', 'w') as f:
        json.dump(report, f, indent=2)

def main():
    tickets = fetch_weekly_tickets()
    summary = summarize_tickets(tickets)
    save_report(summary, tickets)

if __name__ == '__main__':
    main()
