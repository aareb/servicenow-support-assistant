import os
import requests


def _format_resolutions(resolutions):
    if not resolutions:
        return "- No historical mitigation found. Escalate to support."
    uniq = list(dict.fromkeys(resolutions))
    return "\n".join(f"- {item}" for item in uniq)


def summarize(resolutions):
    if not resolutions:
        return _format_resolutions(resolutions)

    api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    endpoint = os.getenv("OPENAI_API_URL", "https://api.openai.com/v1/chat/completions")

    if not api_key:
        return _format_resolutions(resolutions)

    prompt = (
        "You are an incident response assistant. Summarize these mitigation steps into a concise, actionable list for an IT support engineer.\n\n"
        + "\n".join(f"- {item}" for item in resolutions)
        + "\n\nSummary:"
    )

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
                    {
                        "role": "system",
                        "content": "You summarize incident mitigation steps into concise support guidance.",
                    },
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0.2,
                "max_tokens": 200,
            },
            timeout=15,
        )
        response.raise_for_status()
        result = response.json()
        return result["choices"][0]["message"]["content"].strip()
    except Exception:
        return _format_resolutions(resolutions)
