output "document_bucket_name" {
  description = "The name of the document storage bucket"
  value       = google_storage_bucket.document_bucket.name
}

output "cloud_function_url" {
  description = "The URL of the deployed Cloud Function"
  value       = module.cloud_function.function_url
}

output "streamlit_service_account" {
  description = "The service account used by the Streamlit app"
  value       = module.iam.streamlit_service_account_email
}

output "streamlit_app_url" {
  description = "The URL of the deployed Streamlit app"
  value       = module.front_end.streamlit_app_url
}

output "vector_search_indexes" {
  description = "Map of sector names to Vector Search index IDs"
  value       = module.vector_search.vector_search_indexes
}

output "firestore_database_name" {
  description = "The name of the Firestore database"
  value       = module.firestore.database_name
}

output "firestore_database_id" {
  description = "The ID of the Firestore database"
  value       = module.firestore.database_id
}
