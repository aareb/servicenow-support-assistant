def calculate_priority(session):
    if session.impact == "high":
        return "P1"
    return "P2"