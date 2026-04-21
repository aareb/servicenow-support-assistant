import os
import requests


def _format_resolutions(resolutions):
    if not resolutions:
        return "- No historical mitigation found. Escalate to support."
    uniq = list(dict.fromkeys(resolutions))
    return "\n".join(f"- {item}" for item in uniq)


def summarize(resolutions, description=None):
    if not resolutions:
        # Try web search for mitigation if no historical data
        if description:
            try:
                api_key = os.getenv("BING_API_KEY")
                if not api_key:
                    return "- No historical mitigation found and web search unavailable. Escalate to support."
                url = "https://api.bing.microsoft.com/v7.0/search"
                params = {"q": f"how to resolve {description}", "count": 3}
                headers = {"Ocp-Apim-Subscription-Key": api_key}
                resp = requests.get(url, params=params, headers=headers, timeout=10)
                resp.raise_for_status()
                results = resp.json().get("webPages", {}).get("value", [])
                if not results:
                    return "- No historical mitigation found and no web solutions found. Escalate to support."
                summary = "Possible mitigations from the web:\n"
                for r in results:
                    summary += f"- {r.get('name')}: {r.get('snippet')} ({r.get('url')})\n"
                return summary
            except Exception:
                return "- No historical mitigation found and web search failed. Escalate to support."
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
