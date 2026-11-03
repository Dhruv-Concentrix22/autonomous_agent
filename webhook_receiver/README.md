# GitHub Webhook Receiver (Cloud Run Service)

Lightweight FastAPI service that receives GitHub issue webhooks and triggers long-running Cloud Run Agent Jobs.

## 🚀 How it Works

1. GitHub fires a `POST /webhook` request when a user opens an issue.
2. The Webhook Receiver parses the repository URL, issue number, title, and body.
3. It immediately returns `200 OK` (so GitHub does not time out).
4. In the background, it calls `google-cloud-run` SDK to execute the `bug-hunt-agent-job` Cloud Run Job, injecting environment variables for the agent.

---

## 🧪 Local Testing

### Option 1: Run locally with Uvicorn
```bash
cd webhook_receiver
pip install -r requirements.txt
python main.py
```

### Option 2: Test with mock payload via `curl`
```bash
curl -X POST http://localhost:8080/webhook \
  -H "Content-Type: application/json" \
  -H "X-GitHub-Event: issues" \
  -d '{
    "action": "opened",
    "issue": {
      "number": 12,
      "title": "Fix calculate_totals discount bug",
      "body": "The calculate_totals function subtracts flat discount percentage instead of percentage math."
    },
    "repository": {
      "full_name": "my-user/my-repo",
      "clone_url": "https://github.com/my-user/my-repo.git"
    }
  }'
```

Expected response:
```json
{
  "status": "accepted",
  "message": "Agent job dispatched for Issue #12",
  "repository": "my-user/my-repo"
}
```

---

## ☁️ Deployment to Google Cloud Run

```bash
# 1. Build & push image to GCP Artifact Registry
gcloud builds submit --tag us-central1-docker.pkg.dev/YOUR_PROJECT_ID/harness-repo/webhook-receiver:latest .

# 2. Deploy as a Cloud Run Service
gcloud run deploy webhook-receiver \
  --image us-central1-docker.pkg.dev/YOUR_PROJECT_ID/harness-repo/webhook-receiver:latest \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GCP_PROJECT_ID="YOUR_PROJECT_ID",GCP_REGION="us-central1",CLOUD_RUN_JOB_NAME="bug-hunt-agent-job",MOCK_CLOUD_RUN="false"
```
