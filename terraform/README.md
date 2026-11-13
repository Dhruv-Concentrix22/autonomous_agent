# Terraform Infrastructure (IaC)

## Why does this exist?
Deploying an event-driven microservice architecture manually via the GCP console is prone to human error, hard to replicate, and difficult to manage securely. 

This Terraform module exists to codify the entire Google Cloud Platform setup—ensuring least-privilege IAM roles, secure secret injection, and reproducible deployments across development and production environments.

## What does it do?
The module provisions and configures the following resources:
1. **Service Account:** A dedicated, least-privilege identity (`ai-harness-sa`) for the Cloud Run resources.
2. **Artifact Registry:** A Docker repository (`ai-harness-repo`) to store the built container images.
3. **Secret Manager:** Secure storage for `gemini-api-key` and `github-token`.
4. **IAM Policy Bindings:** Explicit, resource-level `roles/secretmanager.secretAccessor` permissions so the service account can read secrets at runtime (avoiding strict organization policy 403 errors).
5. **Cloud Run Job:** The Agent execution template (`bug-hunt-agent-job`).
6. **Cloud Run Service:** The public-facing HTTP FastAPI listener (`webhook-receiver`).

##  Commands

### Initial Setup
Ensure you have initialized your `terraform.tfvars` file with your specific values:
```hcl
project_id     = "<YOUR_GCP_PROJECT_ID>"
region         = "us-central1"
gemini_api_key = "<YOUR_GEMINI_KEY>"
github_token   = "<YOUR_GITHUB_TOKEN>"
```

### Execution
```bash
# 1. Initialize Terraform (Downloads provider plugins)
terraform init

# 2. Preview the infrastructure changes
terraform plan

# 3. Apply the changes to Google Cloud
terraform apply -auto-approve

# 4. (Optional) Destroy infrastructure if shutting down the project
terraform destroy
```
