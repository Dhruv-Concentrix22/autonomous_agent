terraform {
  required_version = ">= 1.3.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# 1. Artifact Registry for Container Images
resource "google_artifact_registry_repository" "harness_repo" {
  location      = var.region
  repository_id = "ai-harness-repo"
  description   = "Docker repository for AI Agent Harness & Webhook Receiver images"
  format        = "DOCKER"
}

# 2. Secret Manager Secrets
resource "google_secret_manager_secret" "gemini_api_key" {
  secret_id = "gemini-api-key"
  replication {
    user_managed {
      replicas {
        location = var.region
      }
    }
  }
}

resource "google_secret_manager_secret_version" "gemini_api_key_version" {
  secret      = google_secret_manager_secret.gemini_api_key.id
  secret_data = var.gemini_api_key
}

resource "google_secret_manager_secret" "github_token" {
  secret_id = "github-token"
  replication {
    user_managed {
      replicas {
        location = var.region
      }
    }
  }
}

resource "google_secret_manager_secret_version" "github_token_version" {
  secret      = google_secret_manager_secret.github_token.id
  secret_data = var.github_token
}

# 3. Cloud Run Job (Agent Container Harness)
resource "google_cloud_run_v2_job" "agent_job" {
  name     = "bug-hunt-agent-job"
  location = var.region

  template {
    template {
      containers {
        image = var.agent_job_image != "" ? var.agent_job_image : "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.harness_repo.repository_id}/agent-job:latest"

        env {
          name = "GEMINI_API_KEY"
          value_source {
            secret_key_ref {
              secret  = google_secret_manager_secret.gemini_api_key.secret_id
              version = "latest"
            }
          }
        }

        env {
          name = "GITHUB_TOKEN"
          value_source {
            secret_key_ref {
              secret  = google_secret_manager_secret.github_token.secret_id
              version = "latest"
            }
          }
        }

        # Default placeholder env vars (will be overridden dynamically by Webhook Receiver)
        env {
          name  = "GITHUB_REPO_URL"
          value = "https://github.com/placeholder/repo.git"
        }
        env {
          name  = "GITHUB_REPO"
          value = "placeholder/repo"
        }
        env {
          name  = "ISSUE_NUMBER"
          value = "1"
        }
        env {
          name  = "ISSUE_DESCRIPTION"
          value = "Placeholder issue description"
        }

        resources {
          limits = {
            cpu    = "2"
            memory = "4Gi"
          }
        }
      }
      timeout = "600s" # 10 minute timeout for agent execution
    }
  }
}

# 4. Cloud Run Service (Webhook Receiver API)
resource "google_cloud_run_v2_service" "webhook_receiver" {
  name     = "webhook-receiver"
  location = var.region
  ingress  = "INGRESS_TRAFFIC_ALL"

  template {
    containers {
      image = var.webhook_service_image != "" ? var.webhook_service_image : "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.harness_repo.repository_id}/webhook-receiver:latest"

      env {
        name  = "GCP_PROJECT_ID"
        value = var.project_id
      }
      env {
        name  = "GCP_REGION"
        value = var.region
      }
      env {
        name  = "CLOUD_RUN_JOB_NAME"
        value = google_cloud_run_v2_job.agent_job.name
      }
      env {
        name  = "MOCK_CLOUD_RUN"
        value = "false"
      }

      resources {
        limits = {
          cpu    = "1"
          memory = "512Mi"
        }
      }
    }
  }
}

# 5. IAM - Allow Unauthenticated Access to Webhook Endpoint (For GitHub Webhooks)
resource "google_cloud_run_v2_service_iam_member" "public_webhook" {
  location = google_cloud_run_v2_service.webhook_receiver.location
  name     = google_cloud_run_v2_service.webhook_receiver.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}
