# Create service account for Cloud Function
resource "google_service_account" "cloud_function_sa" {
  account_id   = "${var.cloud_function_name}-sa"
  display_name = "Service Account for ${var.cloud_function_name} Cloud Function"
  project      = var.project_id
}

# Create service account for Streamlit app
resource "google_service_account" "streamlit_sa" {
  account_id   = "${var.streamlit_app_name}-sa"
  display_name = "Service Account for ${var.streamlit_app_name} Streamlit App"
  project      = var.project_id
}

# Grant Cloud Function service account access to Cloud Storage
resource "google_project_iam_member" "function_storage_admin" {
  project = var.project_id
  role    = "roles/storage.admin"
  member  = "serviceAccount:${google_service_account.cloud_function_sa.email}"
}

# Grant Cloud Function service account access to Firestore
resource "google_project_iam_member" "function_firestore_admin" {
  project = var.project_id
  role    = "roles/datastore.user"
  member  = "serviceAccount:${google_service_account.cloud_function_sa.email}"
}

# Grant Cloud Function service account access to Vertex AI
resource "google_project_iam_member" "function_aiplatform_admin" {
  project = var.project_id
  role    = "roles/aiplatform.admin"
  member  = "serviceAccount:${google_service_account.cloud_function_sa.email}"
}

# Grant Streamlit service account access to Cloud Storage
resource "google_project_iam_member" "streamlit_storage_admin" {
  project = var.project_id
  role    = "roles/storage.admin"
  member  = "serviceAccount:${google_service_account.streamlit_sa.email}"
}

# Grant Streamlit service account access to invoke Cloud Function
resource "google_project_iam_member" "streamlit_function_invoker" {
  project = var.project_id
  role    = "roles/cloudfunctions.invoker"
  member  = "serviceAccount:${google_service_account.streamlit_sa.email}"
}

# Grant Streamlit service account access to Vertex AI for vector search operations
resource "google_project_iam_member" "streamlit_aiplatform_user" {
  project = var.project_id
  role    = "roles/aiplatform.user"
  member  = "serviceAccount:${google_service_account.cloud_function_sa.email}"
}

# Create a custom bucket IAM binding for the document bucket
resource "google_storage_bucket_iam_binding" "document_bucket_admin" {
  bucket = var.bucket_name
  role   = "roles/storage.admin"
  members = [
    "serviceAccount:${google_service_account.cloud_function_sa.email}",
    "serviceAccount:${google_service_account.streamlit_sa.email}"
  ]
}

# Grant the default compute service account access to Cloud Storage
resource "google_project_iam_member" "compute_storage_object_viewer" {
  project = var.project_id
  role    = "roles/storage.objectViewer"
  member  = "serviceAccount:${var.project_number}-compute@developer.gserviceaccount.com"
}

# Grant the default compute service account access to write logs
resource "google_project_iam_member" "compute_logs_writer" {
  project = var.project_id
  role    = "roles/logging.logWriter"
  member  = "serviceAccount:${var.project_number}-compute@developer.gserviceaccount.com"
}

# Grant the default compute service account access to Artifact Registry
resource "google_project_iam_member" "compute_artifact_registry_reader" {
  project = var.project_id
  role    = "roles/artifactregistry.reader"
  member  = "serviceAccount:${var.project_number}-compute@developer.gserviceaccount.com"
}

# Grant the default compute service account access to create Artifact Registry repositories
resource "google_project_iam_member" "compute_artifact_registry_creator" {
  project = var.project_id
  role    = "roles/artifactregistry.admin"
  member  = "serviceAccount:${var.project_number}-compute@developer.gserviceaccount.com"
}

# Grant the default compute service account access to Vertex AI
resource "google_project_iam_member" "compute_aiplatform_admin" {
  project = var.project_id
  role    = "roles/aiplatform.admin"
  member  = "serviceAccount:${var.project_number}-compute@developer.gserviceaccount.com"
}

# Grant the default compute service account access to Firestore
resource "google_project_iam_member" "compute_firestore" {
  project = var.project_id
  role    = "roles/datastore.user"
  member  = "serviceAccount:${var.project_number}-compute@developer.gserviceaccount.com"
}
