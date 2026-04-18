from session import get_session
from prioritizer import calculate_priority
from similarity import find_similar_tickets
from summarizer import summarize
from servicenow import create_incident


def chat_handler(payload):
    user_id = payload.get("user_id", "webuser")
    message = payload.get("message", "").strip()

    if not message:
        return {"reply": "Please describe your issue so I can help."}

    session = get_session(user_id)

    if session.state == "init":
        session.description = message
        session.state = "need_symptoms"
        session.save()
        return {"reply": "Thanks. What symptoms are you seeing and when did this start?"}

    if session.state == "need_symptoms":
        session.symptoms = message
        session.state = "need_impact"
        session.save()
        return {"reply": "Is this impacting production users or a business-critical service? (yes/no)"}

    if session.state == "need_impact":
        session.impact = "high" if "yes" in message.lower() else "medium"
        session.state = "need_ci"
        session.save()
        return {"reply": "Understood. Which application, service, or CI is affected?"}

    if session.state == "need_ci":
        session.ci = message
        session.state = "complete"

        priority = calculate_priority(session)
        similar = find_similar_tickets(session.description, session.symptoms)
        mitigation = summarize(similar)

        incident_number = create_incident(
            session.description,
            priority,
            session.ci,
        )
        session.incident_id = incident_number
        session.save()

        return {
            "reply": (
                f"✅ Incident {incident_number} created\n"
                f"🚨 Priority: {priority}\n\n"
                f"🔍 Diagnosis summary:\n"
                f"Issue: {session.description}\n"
                f"Symptoms: {session.symptoms}\n\n"
                f"🔧 Recommended mitigation:\n{mitigation}\n\n"
                "If you want to log another issue, type 'reset'."
            )
        }

    if session.state == "complete":
        if message.lower() in {"reset", "new issue", "start over"}:
            session.reset()
            return {"reply": "Okay, let's start a new issue. What problem are you seeing?"}
        return {"reply": "I have already created an incident. Type 'reset' to report a different issue."}

    return {"reply": "I am ready to help. Tell me the issue you are facing."}
