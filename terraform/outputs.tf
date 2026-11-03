output "artifact_registry_repo" {
  description = "URL of the GCP Artifact Registry repository"
  value       = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.harness_repo.repository_id}"
}

output "webhook_receiver_url" {
  description = "Public URL for GitHub Webhook configuration"
  value       = "${google_cloud_run_v2_service.webhook_receiver.uri}/webhook"
}

output "agent_cloud_run_job_name" {
  description = "Name of the Cloud Run Job executing the Agent"
  value       = google_cloud_run_v2_job.agent_job.name
}
