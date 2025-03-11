output "database_id" {
  description = "The ID of the Firestore database"
  value       = google_firestore_database.documents_database.id
}

output "database_name" {
  description = "The name of the Firestore database"
  value       = google_firestore_database.documents_database.name
}
