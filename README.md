\# KubeGPT Dashboard



Hybrid AI Kubernetes troubleshooting dashboard using rule-based diagnostics and local LLM fallback.



\---



\## Overview



KubeGPT Dashboard is a local-first debugging assistant for Kubernetes pod failures. It collects pod diagnostics using kubectl, applies deterministic rule-based analysis for common failure patterns, and uses a local LLM fallback for more flexible troubleshooting.



This project reduces the gap between raw Kubernetes errors and human-readable root-cause analysis.



\---



\## Features



\- Real-time pod listing from a Kubernetes namespace

\- Hybrid diagnosis pipeline:

&#x20; - Rule-based heuristics for common failures

&#x20; - Local LLM fallback using Ollama

\- Structured troubleshooting output:

&#x20; - Issue

&#x20; - Root Cause

&#x20; - Evidence

&#x20; - Recommended Fix

\- Raw kubectl describe and log snippets

\- Pod row highlighting for the last analyzed item

\- Status badges, severity, confidence, and latency indicators

\- Interactive dashboard UI built with FastAPI + HTML/CSS/JS



\---



\## Supported Failure Scenarios



\- ImagePullBackOff / ErrImagePull

\- CrashLoopBackOff

\- Startup command failures

\- Liveness probe failures



\---



\## Tech Stack



\- Python

\- FastAPI

\- Kubernetes

\- kubectl

\- Ollama

\- HTML / CSS / JavaScript



\---



\## Architecture



Frontend Dashboard

&#x20;   -> FastAPI backend

&#x20;       -> kubectl collector

&#x20;       -> rule-based analyzer

&#x20;       -> LLM fallback analyzer

&#x20;       -> structured response to UI



\---



\## Project Structure



kubegpt/

├── app/

│ ├── main.py

│ ├── collector.py

│ ├── analyzer.py

│ ├── heuristics.py

│ └── index.html

├── manifests/

│ ├── badimage.yaml

│ ├── crashloop.yaml

│ └── probe.yaml

├── screenshots/

│ ├── dashboard.png

│ ├── imagepull-overview.png

│ ├── imagepull-details.png

│ └── crashloop-analysis.png

├── .gitignore

└── README.md

\---



\## How It Works



1\. The dashboard fetches pods from a Kubernetes namespace

2\. The user selects a pod and clicks Analyze

3\. The backend collects:

&#x20;  - kubectl describe pod

&#x20;  - kubectl logs

&#x20;  - kubectl logs --previous

4\. Rule-based analysis runs first

5\. If no match is found, LLM fallback is used

6\. Results are displayed in structured format



\---



\## Running the Project Locally



cd app  

uvicorn main:app --reload  



Open in browser:  

http://127.0.0.1:8000



\---



\## Why This Project Matters



Kubernetes debugging often requires manually reading verbose logs and system states. This project transforms low-level cluster data into structured, explainable insights using a hybrid AI approach.



\---



\## Future Improvements



\- Namespace dropdown selector

\- Export analysis reports

\- Additional failure detection

\- Incident history tracking



\---



\## Author



Prerana Puttaswamy

---



\## Screenshots



\### Dashboard

!\[Dashboard](screenshots/dashboard.png)



\### Image Pull Error (Overview)

!\[Image Pull Overview](screenshots/imagepull-overview.png)



\### Image Pull Error (Detailed Analysis)

!\[Image Pull Details](screenshots/imagepull-details.png)



\### CrashLoopBackOff Analysis

!\[CrashLoop Analysis](screenshots/crashloop-analysis.png)

