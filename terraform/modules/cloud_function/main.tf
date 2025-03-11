resource "google_storage_bucket" "function_bucket" {
  name                        = "${var.project_id}-function-source"
  location                    = var.region
  uniform_bucket_level_access = true
}

data "archive_file" "source" {
  type        = "zip"
  source_dir  = var.source_dir
  output_path = "/tmp/function-source.zip"
}

resource "google_storage_bucket_object" "zip" {
  name   = "source-${data.archive_file.source.output_md5}.zip"
  bucket = google_storage_bucket.function_bucket.name
  source = data.archive_file.source.output_path
}

resource "google_cloudfunctions2_function" "function" {
  name        = var.cloud_function_name
  description = "Document processing function"
  location    = var.region
  project     = var.project_id

  build_config {
    runtime     = var.runtime
    entry_point = "process_document"
    source {
      storage_source {
        bucket = google_storage_bucket.function_bucket.name
        object = google_storage_bucket_object.zip.name
      }
    }
  }

  service_config {
    max_instance_count = 10
    min_instance_count = 0
    available_memory   = replace(var.memory, "MB", "Mi")
    timeout_seconds    = replace(var.timeout, "s", "")
    environment_variables = {
      PROJECT_ID                = var.project_id
      REGION                    = var.region
      BUCKET_NAME               = var.bucket_name
      SECTORS                   = "accounting, hr, legal, engineering, sales, marketing"
      FIXED_SIZE_CHUNK_SIZE     = var.fixed_size_chunk_size
      SEMANTIC_MIN_CHUNK_SIZE   = var.semantic_min_chunk_size
      SEMANTIC_MAX_CHUNK_SIZE   = var.semantic_max_chunk_size
      SLIDING_WINDOW_CHUNK_SIZE = var.sliding_window_chunk_size
      SLIDING_WINDOW_OVERLAP    = var.sliding_window_overlap
      EMBEDDING_MODEL_NAME      = var.embedding_model_name
      EMBEDDING_DIMENSIONS      = var.embedding_dimensions
      SECTORS_COLLECTION        = var.sectors_collection
      DOCUMENTS_COLLECTION      = var.documents_collection
      CHUNKS_COLLECTION         = var.chunks_collection
      TEMP_DIRECTORY            = var.temp_directory
    }
    service_account_email = var.service_account_email
  }

  labels = {
    deployment-tool = "terraform"
  }
}

# IAM entry for all users to invoke the function
resource "google_cloud_run_service_iam_member" "invoker" {
  project  = var.project_id
  location = var.region
  service  = google_cloudfunctions2_function.function.name

  role   = "roles/run.invoker"
  member = "allUsers"
}
