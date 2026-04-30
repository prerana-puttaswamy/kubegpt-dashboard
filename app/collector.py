import subprocess
import shutil
import json

KUBECTL_PATH = shutil.which("kubectl") or "kubectl"


def run_kubectl(args):
    try:
        result = subprocess.run(
            [KUBECTL_PATH] + args,
            capture_output=True,
            text=True,
            shell=False
        )
        return result.stdout, result.stderr, result.returncode
    except Exception as e:
        return "", str(e), 1


def get_pod_info(pod_name, namespace="default"):
    describe_out, describe_err, _ = run_kubectl(
        ["describe", "pod", pod_name, "-n", namespace]
    )
    logs_out, logs_err, _ = run_kubectl(
        ["logs", pod_name, "-n", namespace]
    )
    prev_logs_out, prev_logs_err, _ = run_kubectl(
        ["logs", pod_name, "-n", namespace, "--previous"]
    )

    return {
        "describe": describe_out + describe_err,
        "logs": logs_out + logs_err,
        "previous_logs": prev_logs_out + prev_logs_err
    }


def list_pods(namespace="default"):
    stdout, stderr, code = run_kubectl(["get", "pods", "-n", namespace, "-o", "json"])

    if code != 0:
        raise RuntimeError(stderr or "Failed to fetch pods")

    data = json.loads(stdout)
    pods = []

    for item in data.get("items", []):
        name = item["metadata"]["name"]
        phase = item.get("status", {}).get("phase", "Unknown")
        container_statuses = item.get("status", {}).get("containerStatuses", [])

        restart_count = 0
        reason = None

        if container_statuses:
            for cs in container_statuses:
                restart_count += cs.get("restartCount", 0)

                state = cs.get("state", {})
                waiting = state.get("waiting")
                terminated = state.get("terminated")

                if waiting and waiting.get("reason"):
                    reason = waiting["reason"]
                    break

                if terminated and terminated.get("reason"):
                    reason = terminated["reason"]
                    break

                last_state = cs.get("lastState", {})
                last_terminated = last_state.get("terminated")
                if last_terminated and last_terminated.get("reason"):
                    reason = last_terminated["reason"]

        if not reason:
            reason = phase

        if phase == "Running" and restart_count > 0 and reason == "Running":
            reason = "Running (restarting)"

        pods.append({
            "name": name,
            "namespace": namespace,
            "status": reason,
            "phase": phase,
            "restarts": restart_count
        })

    return pods