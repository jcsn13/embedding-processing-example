# Store the deployment parameters as local variables
locals {
  app_name        = var.streamlit_app_name
  region          = var.region
  project_id      = var.project_id
  source_dir      = var.source_dir
  memory          = var.memory
  service_account = var.service_account_email
  sectors_string  = join(",", var.sectors)
  image_path      = "${var.region}-docker.pkg.dev/${var.project_id}/${local.app_name}-repo/${local.app_name}"
}

# Create Artifact Registry repository for Docker images
resource "google_artifact_registry_repository" "streamlit_repo" {
  provider = google-beta

  location      = var.region
  repository_id = "${local.app_name}-repo"
  description   = "Docker repository for ${local.app_name}"
  format        = "DOCKER"
}

# Build the container image
resource "null_resource" "build_image" {
  triggers = {
    dockerfile_hash   = filesha256("${var.source_dir}/Dockerfile")
    app_hash          = filesha256("${var.source_dir}/app.py")
    requirements_hash = filesha256("${var.source_dir}/requirements.txt")
  }

  provisioner "local-exec" {
    command = <<EOF
      gcloud builds submit ${var.source_dir} \
        --project=${var.project_id} \
        --region=${var.region} \
        --tag=${local.image_path}:latest
    EOF
  }

  depends_on = [
    google_artifact_registry_repository.streamlit_repo
  ]
}

# Create a Cloud Run service
resource "google_cloud_run_v2_service" "streamlit_app" {
  name     = local.app_name
  location = var.region

  template {
    containers {
      image = "${local.image_path}:latest"

      env {
        name  = "PROJECT_ID"
        value = var.project_id
      }
      env {
        name  = "REGION"
        value = var.region
      }
      env {
        name  = "CLOUD_FUNCTION_URL"
        value = var.cloud_function_url
      }
      env {
        name  = "BUCKET_NAME"
        value = var.bucket_name
      }
      env {
        name  = "SECTORS"
        value = local.sectors_string
      }

      resources {
        limits = {
          cpu    = "1"
          memory = var.memory
        }
      }
    }

    service_account = var.service_account_email

    scaling {
      min_instance_count = 0
      max_instance_count = 10
    }
  }

  depends_on = [
    null_resource.build_image
  ]
}

# Make the service public
data "google_iam_policy" "noauth" {
  binding {
    role = "roles/run.invoker"
    members = [
      "allUsers",
    ]
  }
}

resource "google_cloud_run_v2_service_iam_policy" "noauth" {
  location    = google_cloud_run_v2_service.streamlit_app.location
  name        = google_cloud_run_v2_service.streamlit_app.name
  policy_data = data.google_iam_policy.noauth.policy_data
}
