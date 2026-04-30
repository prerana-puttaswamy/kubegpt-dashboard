from collector import get_pod_info
from analyzer import analyze_kubernetes_issue

pod_name = input("Enter pod name: ")

data = get_pod_info(pod_name)

print("\n=== RAW DESCRIBE SNIPPET ===\n")
print(data["describe"][:1200])

print("\n=== RAW LOGS SNIPPET ===\n")
print(data["logs"][:500])

print("\n=== AI ANALYSIS ===\n")
analysis = analyze_kubernetes_issue(
    pod_name,
    data["describe"],
    data["logs"],
    data["previous_logs"]
)
print(analysis)