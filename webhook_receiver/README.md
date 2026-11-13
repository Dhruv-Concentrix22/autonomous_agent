# Webhook Receiver (Cloud Run Service)

## Why does this exist?
GitHub Webhooks require the receiving server to respond with a `200 OK` status within 10 seconds. However, an AI Agent's task (cloning a repo, analyzing code, testing, and pushing a PR) can take several minutes. 

This component acts as an asynchronous dispatcher. It instantly acknowledges GitHub's webhook and triggers the long-running Agent Cloud Run Job in the background.

## What does it do?
1. Listens for POST requests on the `/webhook` endpoint.
2. Validates GitHub `issues.opened` events.
3. Immediately returns a `200 OK` to GitHub.
4. Asynchronously uses the Google Cloud Python SDK to dispatch the `bug-hunt-agent-job` Cloud Run Job, passing the GitHub repository URL, issue number, and description as environment variables.

## Commands

### Local Testing
To test locally, you need your GCP credentials active and a tunnel to receive GitHub webhooks.

```bash
# 1. Authenticate with Google Cloud
gcloud auth application-default login

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start the server (ensure MOCK_CLOUD_RUN=false in .env for real GCP execution)
uvicorn main:app --host 0.0.0.0 --port 8080 --reload

# 4. In a separate terminal, expose it to the internet
npx localtunnel --port 8080
```
*(Update your GitHub Webhook Payload URL to the generated localtunnel URL `https://<subdomain>.loca.lt/webhook`)*

### Deployment
To build and deploy to Google Cloud Run:

```bash
# Build the Docker image and push to Artifact Registry
gcloud builds submit --tag <REGION>-docker.pkg.dev/<YOUR_PROJECT_ID>/ai-harness-repo/webhook-receiver:latest

# Deploy to Cloud Run (Managed by Terraform, but manual update command below)
gcloud run deploy webhook-receiver \
  --image <REGION>-docker.pkg.dev/<YOUR_PROJECT_ID>/ai-harness-repo/webhook-receiver:latest \
  --region <REGION> \
  --allow-unauthenticated
```
