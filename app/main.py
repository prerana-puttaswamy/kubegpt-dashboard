from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from collector import list_pods, get_pod_info
from analyzer import analyze_kubernetes_issue, parse_llm_analysis
from heuristics import rule_based_analysis
import os
import time

app = FastAPI(title="KubeGPT Dashboard")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def get_severity(issue: str, root_cause: str):
    text = f"{issue} {root_cause}".lower()

    if (
        "imagepullbackoff" in text
        or "crash loop" in text
        or "crashloop" in text
        or "cannot start" in text
        or "non-zero status" in text
    ):
        return "high"

    if "probe" in text or "warning" in text or "health check" in text:
        return "medium"

    return "low"


@app.get("/")
def serve_index():
    return FileResponse(os.path.join(BASE_DIR, "index.html"))


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/pods")
def get_pods(namespace: str = Query(default="default")):
    try:
        pods = list_pods(namespace)
        return {"namespace": namespace, "pods": pods}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/analyze")
def analyze_pod(
    pod_name: str = Query(...),
    namespace: str = Query(default="default")
):
    try:
        data = get_pod_info(pod_name, namespace)

        start_time = time.time()

        # Step 1: try rule-based first
        analysis_data = rule_based_analysis(data["describe"], data["logs"])

        # Step 2: fallback to LLM if needed
        if analysis_data is None:
            raw_llm_output = analyze_kubernetes_issue(
                pod_name,
                data["describe"],
                data["logs"],
                data["previous_logs"]
            )
            analysis_data = parse_llm_analysis(raw_llm_output)

            if not analysis_data.get("recommended_fix"):
                analysis_data["recommended_fix"] = [
                    "Inspect pod logs and describe output",
                    "Verify the failing configuration or startup behavior",
                    "Redeploy after applying the fix"
                ]

            if not analysis_data.get("evidence"):
                analysis_data["evidence"] = [
                    "Analysis was generated from describe output",
                    "Logs were used as supporting context"
                ]

            if not analysis_data.get("issue"):
                analysis_data["issue"] = "Pod failure detected."

            if not analysis_data.get("root_cause"):
                analysis_data["root_cause"] = "Root cause could not be determined with high confidence."

            if not analysis_data.get("confidence"):
                analysis_data["confidence"] = "low"

            if not analysis_data.get("source"):
                analysis_data["source"] = "llm"

            latency = round(time.time() - start_time, 2)
            latency_label = "LLM"
        else:
            latency = 0
            latency_label = "instant"

        severity = get_severity(
            analysis_data.get("issue", ""),
            analysis_data.get("root_cause", "")
        )

        return {
            "pod_name": pod_name,
            "namespace": namespace,
            "severity": severity,
            "latency": latency,
            "latency_type": latency_label,
            "analysis": analysis_data,
            "describe_snippet": data["describe"][:1500],
            "logs_snippet": data["logs"][:700]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))