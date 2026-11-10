# Infrastructure as Code (Terraform for Cloud MVP)

This directory contains Terraform scripts to automate the deployment of the Cloud MVP on Google Cloud Platform (GCP).

## 🛠️ Resources Created

1. **Artifact Registry (`ai-harness-repo`):** Docker registry for hosting the Agent and Webhook images.
2. **Secret Manager (`gemini-api-key`, `github-token`):** Secure storage for API keys and tokens.
3. **Cloud Run Job (`bug-hunt-agent-job`):** Containerized execution job for running the Antigravity agent (2 CPU, 4GB RAM, 10 min timeout).
4. **Cloud Run Service (`webhook-receiver`):** Public HTTPS endpoint for receiving GitHub Webhook events.
5. **IAM Bindings (`allUsers` invoker):** Grants unauthenticated access to `/webhook` so GitHub can deliver payloads.

---

## 🚀 Execution Guide

### Step 1: Create your `terraform.tfvars` file
Copy the template and fill in your GCP Project ID and secret keys:
```bash
cp terraform.tfvars.example terraform.tfvars
```

Edit `terraform.tfvars`:
```hcl
project_id     = "my-gcp-lab-project"
region         = "us-central1"
gemini_api_key = "AIzaSy..."
github_token   = "ghp_..."
```

### Step 2: Build and Push Docker Images
Before applying Terraform, build and push your Docker images to Artifact Registry:

```bash
# Authenticate Docker with GCP Artifact Registry
gcloud auth configure-docker us-central1-docker.pkg.dev

# 1. Agent Job Image
cd ../docker_harness_project
docker build -t us-central1-docker.pkg.dev/YOUR_PROJECT_ID/ai-harness-repo/agent-job:latest .
docker push us-central1-docker.pkg.dev/YOUR_PROJECT_ID/ai-harness-repo/agent-job:latest

# 2. Webhook Receiver Image
cd ../webhook_receiver
docker build -t us-central1-docker.pkg.dev/YOUR_PROJECT_ID/ai-harness-repo/webhook-receiver:latest .
docker push us-central1-docker.pkg.dev/YOUR_PROJECT_ID/ai-harness-repo/webhook-receiver:latest
```

### Step 3: Initialize and Apply Terraform
```bash
cd ../terraform
terraform init
terraform plan
terraform apply
```

### Step 4: Configure GitHub Webhook
After `terraform apply` finishes, note the output URL:
```text
webhook_receiver_url = "https://webhook-receiver-xyz.a.run.app/webhook"
```
Go to your GitHub repository -> **Settings** -> **Webhooks** -> **Add Webhook**:
- **Payload URL:** Paste the `webhook_receiver_url`.
- **Content type:** `application/json`
- **Which events:** Select **Let me select individual events** -> check **Issues**.
- Click **Add webhook**.
