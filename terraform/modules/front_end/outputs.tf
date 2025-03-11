output "streamlit_app_url" {
  description = "The URL of the deployed Streamlit app"
  value       = google_cloud_run_v2_service.streamlit_app.uri
}
