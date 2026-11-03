# Containerized AI Evaluation Harness (Antigravity SDK)

A true zero-compromise AI evaluation harness demonstrating how production AI evaluation systems (like SWE-bench and HumanEval) run AI agents 100% jailed inside isolated Docker containers.

## 🌟 Core Architecture

```text
+-----------------------------------------------------------------------+
|                            HOST MACHINE                               |
|  Runs command: docker run -e GEMINI_API_KEY=... bug-hunt-harness      |
+-----------------------------------------------------------------------+
                                   |
                                   v
+-----------------------------------------------------------------------+
|                    DOCKER CONTAINER (ISOLATED)                        |
|                                                                       |
|   1. Harness initializes INSIDE container (/app)                      |
|   2. Agent spawns INSIDE container                                    |
|   3. Agent reads /app/buggy_code.py INSIDE container                  |
|   4. Agent runs pytest & edits files INSIDE container                 |
|   5. Harness evaluates pytest INSIDE container                        |
|                                                                       |
+-----------------------------------------------------------------------+
```

---

## 🚀 How to Run

### Step 1: Build the Container Image
From the `docker_harness_project` directory, build the Docker image:
```bash
docker build -t bug-hunt-harness .
```

### Step 2: Run the Harness inside Docker
Pass your `GEMINI_API_KEY` into the container environment:

**In PowerShell:**
```powershell
docker run --rm -e GEMINI_API_KEY="$env:GEMINI_API_KEY" bug-hunt-harness
```

**In CMD:**
```cmd
docker run --rm -e GEMINI_API_KEY="%GEMINI_API_KEY%" bug-hunt-harness
```

**In Bash:**
```bash
docker run --rm -e GEMINI_API_KEY="$GEMINI_API_KEY" bug-hunt-harness
```

---

## 📁 File Structure

* **[Dockerfile](file:///c:/Users/dhruv.pawar1/POC/harness/docker_harness_project/Dockerfile):** Packages Python 3.11, `pytest`, `google-antigravity`, and all code files into an isolated Linux container environment.
* **[buggy_code.py](file:///c:/Users/dhruv.pawar1/POC/harness/docker_harness_project/buggy_code.py):** Contains a math bug in `calculate_totals()`.
* **[test_buggy_code.py](file:///c:/Users/dhruv.pawar1/POC/harness/docker_harness_project/test_buggy_code.py):** Pytest suite that verifies expected behavior.
* **[harness.py](file:///c:/Users/dhruv.pawar1/POC/harness/docker_harness_project/harness.py):** The in-container orchestrator that initializes the agent, streams its progress, and evaluates `pytest` exit codes inside `/app`.
