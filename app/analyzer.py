import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "phi3"


def analyze_kubernetes_issue(pod_name, describe, logs, previous_logs):
    prompt = f"""
You are a Kubernetes debugging assistant.

STRICT RULES:
- Use ONLY the evidence provided
- Do NOT mention CPU, memory, or networking unless explicitly shown
- If image, command, exit code, or probe error is clearly visible, focus only on that
- Keep the answer short and specific

Return EXACTLY in this format:

Issue: <one short sentence>
Root Cause: <one short sentence>
Evidence:
- <bullet>
- <bullet>
- <bullet>
Recommended Fix:
- <bullet>
- <bullet>
- <bullet>
Confidence: <high/medium/low>

Pod Name: {pod_name}

=== DESCRIBE OUTPUT ===
{describe}

=== CURRENT LOGS ===
{logs}

=== PREVIOUS LOGS ===
{previous_logs}
"""

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.1
            }
        },
        timeout=120
    )

    response.raise_for_status()
    data = response.json()
    return data["response"]


def parse_llm_analysis(text: str):
    result = {
        "issue": "",
        "root_cause": "",
        "evidence": [],
        "recommended_fix": [],
        "confidence": "low",
        "source": "llm"
    }

    lines = [line.strip() for line in text.splitlines() if line.strip()]
    current_section = None

    for line in lines:
        lower = line.lower()

        if lower.startswith("issue:"):
            result["issue"] = line.split(":", 1)[1].strip()
            current_section = None
        elif lower.startswith("root cause:"):
            result["root_cause"] = line.split(":", 1)[1].strip()
            current_section = None
        elif lower.startswith("evidence:"):
            current_section = "evidence"
        elif lower.startswith("recommended fix:"):
            current_section = "recommended_fix"
        elif lower.startswith("confidence:"):
            result["confidence"] = line.split(":", 1)[1].strip().lower()
            current_section = None
        elif line.startswith("-") and current_section == "evidence":
            result["evidence"].append(line[1:].strip())
        elif line.startswith("-") and current_section == "recommended_fix":
            result["recommended_fix"].append(line[1:].strip())

    return result