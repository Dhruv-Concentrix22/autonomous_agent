variable "project_id" {
  description = "Google Cloud Project ID"
  type        = string
}

variable "region" {
  description = "GCP Region for deployment"
  type        = string
  default     = "us-central1"
}

variable "gemini_api_key" {
  description = "Gemini API Key for the Antigravity Agent"
  type        = string
  sensitive   = true
}

variable "github_token" {
  description = "GitHub Personal Access Token for git push and PR creation"
  type        = string
  sensitive   = true
}

variable "agent_job_image" {
  description = "Docker image URL for the Agent Cloud Run Job"
  type        = string
  default     = ""
}

variable "webhook_service_image" {
  description = "Docker image URL for the Webhook Receiver Cloud Run Service"
  type        = string
  default     = ""
}
