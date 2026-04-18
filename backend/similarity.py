import difflib

# Simulated closed ticket store; replace with ServiceNow historical data for production workloads.
CLOSED_TICKETS = [
    {
        "description": "application down login issue",
        "resolution": "Restart service and clear cache"
    },
    {
        "description": "database connection failure",
        "resolution": "Check DB connectivity and restart pool"
    },
    {
        "description": "slow page load after deployment",
        "resolution": "Rollback the latest deploy and warm up the cache"
    },
    {
        "description": "email notifications not being sent",
        "resolution": "Verify SMTP credentials and restart email service"
    }
]

def find_similar_tickets(description, symptoms=None):
    search_text = f"{description} {symptoms or ''}".lower()
    scored_matches = []
    for ticket in CLOSED_TICKETS:
        score = difflib.SequenceMatcher(None, search_text, ticket["description"].lower()).ratio()
        if score > 0.25:
            scored_matches.append((score, ticket["resolution"]))

    scored_matches.sort(key=lambda item: item[0], reverse=True)
    return [resolution for _, resolution in scored_matches[:3]]