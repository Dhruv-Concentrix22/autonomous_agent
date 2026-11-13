# Docker Harness Project (Cloud Run Job)

## Why does this exist?
This is the "Brain and Hands" of the autonomous system. Running a powerful LLM agent directly on a host machine poses severe security risks (e.g., arbitrary code execution, unintended file deletions). 

This component exists to provide a secure, isolated, and ephemeral sandbox environment (a Docker container) where the AI can safely clone code, experiment, and run unit tests without impacting any underlying infrastructure.

##  What does it do?
1. Bootstraps a secure Linux container containing Python, Git, and the Google Antigravity SDK.
2. Dynamically clones the target GitHub repository securely via OAuth.
3. Initializes the Antigravity Agent with a hybrid toolset:
   - **Built-in File Tools:** (`VIEW_FILE`, `EDIT_FILE`, `SEARCH_DIR`, `LIST_DIR`) mapped via SDK capabilities.
   - **Custom Tools (`tools.py`):** Structured, secure commands for Git operations (`create_git_branch`, `git_commit`, `push_branch`), testing (`run_test_suite`), and GitHub REST API integration (`create_pull_request`).
4. Executes the AI reasoning loop to analyze the issue, patch the code, and submit a Pull Request.

##  Commands

### Local Testing (Mocking the Webhook)
You can run the agent locally without waiting for a webhook event by passing the necessary environment variables.

```bash
# 1. Build the Docker Image
docker build -t ai-harness-agent .

# 2. Run the container locally (Injecting credentials & target issue data)
docker run --rm \
  -e GEMINI_API_KEY="<YOUR_GEMINI_KEY>" \
  -e GITHUB_TOKEN="<YOUR_GITHUB_PAT>" \
  -e GITHUB_REPO_URL="https://github.com/<OWNER>/<REPO>.git" \
  -e GITHUB_REPO="<OWNER>/<REPO>" \
  -e ISSUE_NUMBER="1" \
  -e ISSUE_DESCRIPTION="Fix calculation bug in math.py" \
  ai-harness-agent
```

### Deployment to Google Cloud
```bash
# Build and push to Artifact Registry
gcloud builds submit --tag <REGION>-docker.pkg.dev/<YOUR_PROJECT_ID>/ai-harness-repo/agent-job:latest

# Manual test execution of the Cloud Run Job
gcloud run jobs execute bug-hunt-agent-job \
  --region=<REGION> \
  --update-env-vars="GITHUB_REPO_URL=https://github.com/...,GITHUB_REPO=...,ISSUE_NUMBER=1,ISSUE_DESCRIPTION=test"
```
