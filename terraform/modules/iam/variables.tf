variable "project_id" {
  description = "The GCP project ID"
  type        = string
}

variable "project_number" {
  description = "The GCP project number"
  type        = string
}

variable "cloud_function_name" {
  description = "Name of the Cloud Function"
  type        = string
}

variable "streamlit_app_name" {
  description = "Name of the Streamlit app"
  type        = string
}

variable "bucket_name" {
  description = "Name of the storage bucket for documents"
  type        = string
}
