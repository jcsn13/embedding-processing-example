# Create a Firestore database in Native mode
resource "google_firestore_database" "documents_database" {
  provider    = google-beta
  project     = var.project_id
  name        = "documents"
  location_id = var.region
  type        = "FIRESTORE_NATIVE"

  # Ensure the Firestore API is enabled
  depends_on = [var.firestore_api_enabled]

  lifecycle {
    prevent_destroy       = false
    create_before_destroy = true
  }
}
