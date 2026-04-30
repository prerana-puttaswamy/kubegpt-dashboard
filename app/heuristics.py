def rule_based_analysis(describe: str, logs: str):
    text = f"{describe}\n{logs}".lower()

    if "imagepullbackoff" in text or "errimagepull" in text or "failed to pull image" in text:
        return {
            "issue": "Pod cannot start due to invalid container image.",
            "root_cause": "Container image tag is incorrect or does not exist.",
            "evidence": [
                "Pod shows ImagePullBackOff or ErrImagePull",
                "Logs indicate image pull failure",
                "Describe output references invalid image tag"
            ],
            "recommended_fix": [
                "Replace the invalid image tag with a valid one",
                "Reapply the deployment",
                "Verify the image exists using docker pull"
            ],
            "confidence": "high",
            "source": "rule-based"
        }

    if (
        "crashloopbackoff" in text
        or "exit code: 1" in text
        or "reason: error" in text
        or "last state:" in text and "terminated" in text
        or "starting..." in text and "exit 1" in text
    ):
        return {
            "issue": "Pod is stuck in a crash loop.",
            "root_cause": "Container startup command exits with a non-zero status.",
            "evidence": [
                "Container terminated with exit code 1 or reason Error",
                "Logs show startup begins before container exits",
                "Pod repeatedly restarts after failure"
            ],
            "recommended_fix": [
                "Inspect the startup command or entrypoint",
                "Remove the failing exit condition or fix the startup error",
                "Redeploy and confirm the container stays running"
            ],
            "confidence": "high",
            "source": "rule-based"
        }

    if "failed liveness probe" in text or "liveness probe failed" in text:
        return {
            "issue": "Pod is failing health checks.",
            "root_cause": "Liveness probe is misconfigured or the application endpoint is unhealthy.",
            "evidence": [
                "Describe output shows liveness probe failure",
                "Pod restarts after health checks",
                "Container starts but is later killed"
            ],
            "recommended_fix": [
                "Verify the probe path and port",
                "Ensure the application serves the expected endpoint",
                "Increase initialDelaySeconds if startup is slow"
            ],
            "confidence": "high",
            "source": "rule-based"
        }

    return None