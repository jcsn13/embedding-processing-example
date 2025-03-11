# Enable required APIs
resource "google_project_service" "aiplatform" {
  project                    = var.project_id
  service                    = "aiplatform.googleapis.com"
  disable_dependent_services = false
  disable_on_destroy         = false
}

resource "google_project_service" "cloudfunctions" {
  project                    = var.project_id
  service                    = "cloudfunctions.googleapis.com"
  disable_dependent_services = false
  disable_on_destroy         = false
}

resource "google_project_service" "cloudfunctions_v2" {
  project                    = var.project_id
  service                    = "cloudfunctions.googleapis.com"
  disable_dependent_services = false
  disable_on_destroy         = false
}

resource "google_project_service" "eventarc" {
  project                    = var.project_id
  service                    = "eventarc.googleapis.com"
  disable_dependent_services = false
  disable_on_destroy         = false
}

resource "google_project_service" "run" {
  project                    = var.project_id
  service                    = "run.googleapis.com"
  disable_dependent_services = false
  disable_on_destroy         = false
}

resource "google_project_service" "cloudbuild" {
  project                    = var.project_id
  service                    = "cloudbuild.googleapis.com"
  disable_dependent_services = false
  disable_on_destroy         = false
}

resource "google_project_service" "storage" {
  project                    = var.project_id
  service                    = "storage.googleapis.com"
  disable_dependent_services = false
  disable_on_destroy         = false
}

resource "google_project_service" "firestore" {
  project                    = var.project_id
  service                    = "firestore.googleapis.com"
  disable_dependent_services = false
  disable_on_destroy         = false
}

resource "google_project_service" "artifactregistry" {
  project                    = var.project_id
  service                    = "artifactregistry.googleapis.com"
  disable_dependent_services = false
  disable_on_destroy         = false
}

# Add a delay after enabling APIs to allow them to propagate
resource "time_sleep" "api_propagation" {
  depends_on = [
    google_project_service.aiplatform,
    google_project_service.cloudfunctions,
    google_project_service.cloudfunctions_v2,
    google_project_service.eventarc,
    google_project_service.run,
    google_project_service.cloudbuild,
    google_project_service.storage,
    google_project_service.firestore,
    google_project_service.artifactregistry
  ]

  create_duration = "60s"
}

# Create a storage bucket for documents if it doesn't exist
resource "google_storage_bucket" "document_bucket" {
  name                        = var.bucket_name
  location                    = var.region
  uniform_bucket_level_access = true
  force_destroy               = true

  depends_on = [
    google_project_service.storage,
    time_sleep.api_propagation
  ]
}

# IAM module - Create service accounts and assign permissions
module "iam" {
  source = "./modules/iam"

  project_id          = var.project_id
  project_number      = var.project_number
  cloud_function_name = var.cloud_function_name
  streamlit_app_name  = var.streamlit_app_name
  bucket_name         = var.bucket_name

  depends_on = [
    google_project_service.storage,
    time_sleep.api_propagation
  ]
}

# Add additional delay specifically for Firestore API
resource "time_sleep" "firestore_api_propagation" {
  depends_on = [
    google_project_service.firestore,
    time_sleep.api_propagation
  ]

  create_duration = "90s"
}

# Firestore module - Create Firestore database
module "firestore" {
  source = "./modules/firestore"

  project_id            = var.project_id
  region                = var.region
  firestore_api_enabled = google_project_service.firestore

  depends_on = [
    google_project_service.firestore,
    time_sleep.api_propagation,
    time_sleep.firestore_api_propagation
  ]
}

# Vector Search module - Create Vector Search indexes
module "vector_search" {
  source = "./modules/vector_search"

  project_id      = var.project_id
  region          = var.region
  sectors         = var.sectors
  dimensions      = var.embedding_dimensions
  embedding_model = var.embedding_model

  depends_on = [
    google_storage_bucket.document_bucket,
    google_project_service.aiplatform,
    google_project_service.storage,
    time_sleep.api_propagation
  ]
}

# Cloud Function module - Deploy the document processing function
module "cloud_function" {
  source = "./modules/cloud_function"

  project_id          = var.project_id
  region              = var.region
  cloud_function_name = var.cloud_function_name
  bucket_name         = var.bucket_name
  memory              = var.function_memory
  timeout             = var.function_timeout
  # Using compute service account instead of dedicated service account to avoid provider inconsistency
  service_account_email = "${var.project_number}-compute@developer.gserviceaccount.com"

  # Environment variables
  sectors                   = var.sectors
  fixed_size_chunk_size     = var.fixed_size_chunk_size
  semantic_min_chunk_size   = var.semantic_min_chunk_size
  semantic_max_chunk_size   = var.semantic_max_chunk_size
  sliding_window_chunk_size = var.sliding_window_chunk_size
  sliding_window_overlap    = var.sliding_window_overlap
  # hierarchical_levels is hardcoded in cloud_function/config.py
  embedding_model_name = var.embedding_model_name
  embedding_dimensions = var.embedding_dimensions
  sectors_collection   = var.sectors_collection
  documents_collection = var.documents_collection
  chunks_collection    = var.chunks_collection
  temp_directory       = var.temp_directory

  # Source directory for the Cloud Function
  source_dir = "../cloud_function"

  depends_on = [
    module.iam,
    module.vector_search,
    module.firestore,
    google_storage_bucket.document_bucket,
    google_project_service.cloudfunctions,
    google_project_service.cloudfunctions_v2,
    google_project_service.eventarc,
    google_project_service.run,
    google_project_service.storage,
    google_project_service.firestore,
    google_project_service.artifactregistry,
    time_sleep.api_propagation,
    module.iam.compute_logs_writer,
    module.iam.compute_artifact_registry_reader,
    module.iam.compute_artifact_registry_creator
    # Removed dependency on module.iam.function_bucket_object_viewer as it's been commented out
  ]
}

# Front End module - Deploy the Streamlit app
module "front_end" {
  source = "./modules/front_end"

  project_id            = var.project_id
  region                = var.region
  streamlit_app_name    = var.streamlit_app_name
  bucket_name           = var.bucket_name
  cloud_function_url    = module.cloud_function.function_url
  memory                = var.streamlit_memory
  service_account_email = module.iam.streamlit_service_account_email
  sectors               = var.sectors

  depends_on = [
    module.iam,
    module.cloud_function,
    google_storage_bucket.document_bucket,
    google_project_service.run,
    google_project_service.cloudbuild,
    google_project_service.storage,
    time_sleep.api_propagation
  ]
}
