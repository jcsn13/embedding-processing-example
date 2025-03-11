output "cloud_function_service_account_email" {
  description = "The email of the service account for the Cloud Function"
  value       = google_service_account.cloud_function_sa.email
}

output "streamlit_service_account_email" {
  description = "The email of the service account for the Streamlit app"
  value       = google_service_account.streamlit_sa.email
}

output "compute_storage_object_viewer" {
  description = "The IAM binding for the compute service account to access Cloud Storage"
  value       = google_project_iam_member.compute_storage_object_viewer
}

output "compute_logs_writer" {
  description = "The IAM binding for the compute service account to write logs"
  value       = google_project_iam_member.compute_logs_writer
}

output "compute_artifact_registry_reader" {
  description = "The IAM binding for the compute service account to access Artifact Registry"
  value       = google_project_iam_member.compute_artifact_registry_reader
}

output "compute_artifact_registry_creator" {
  description = "The IAM binding for the compute service account to create Artifact Registry repositories"
  value       = google_project_iam_member.compute_artifact_registry_creator
}
